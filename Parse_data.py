"""
Parse_data.py — MVP-50 serial data reader for the Aerotec test cell.

Reads RTDOA lines from the MVP-50 over USB serial (COM3), parses engine
telemetry fields, and inserts documents into a local MongoDB collection.
Launched as a subprocess by the Streamlit dashboard:

    python Parse_data.py <db_name> <collection_name>
"""

import asyncio
import datetime
import sys
import time
from typing import Any, Dict

import motor.motor_asyncio
import pytz
import serial

# ------------------- DATA CHANNEL PARAMETER EXAMPLE ----------------
#Parameter Format:
#Name; alternate names, x, x, x,
# M.P.,MP,MAP,
# RPM,
# HP,
# F.FLOW,FFLOW,
# UPRDDK,UPPDEK,UPRDEK 
# FUEL P,FUEL.P,
# FL P1,
# OIL P,
# OIL P2,
# OIL T,
# VOLTS,
# AMPS,
# EGT 1,
# EGT 2,
# EGT 3,
# EGT 4,
# EGT 5,
# EGT 6,
# CHT 1,
# CHT 2,
# CHT 3,
# CHT 4,
# CHT 5,
# CHT 6,
# OAT,
# TIT,
# CDT,
# IAT CARB,
# MAG DROP,
# S.COOL,
# WARN,
#End of Parameter List

# ---------------------------------------------------------------------------
# MongoDB setup — db/collection names are passed in by st_dashboard.py
# ---------------------------------------------------------------------------
db_name = sys.argv[1]
collection_name = sys.argv[2]

uri = "mongodb://localhost:27017/"
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client[db_name]
collection = db[collection_name]

# ---------------------------------------------------------------------------
# Serial port configuration (MVP-50 USB connection)
# ---------------------------------------------------------------------------
SERIAL_PORT = 'COM3'
BAUDRATE = 9600
SERIAL_TIMEOUT = 1          # seconds per readline() call before returning empty
STARTUP_CONNECT_TIMEOUT_SEC = 120   # max wait for USB to appear at startup
CONNECT_RETRY_INTERVAL_SEC = 2    # pause between startup/reopen attempts
RECONNECT_INTERVAL_SEC = 5        # pause after a mid-run disconnect

# RTDOA comma-separated field order after the "RTDOA" header token.
# Maps to MVP-50 data channels: M.P., RPM, HP, F.FLOW, UPRDDK, FUEL P, etc.
RTDOA_FIELD_NAMES = [
    'manifold_pressure', 'rpm', 'hp', 'fuel_flow', 'upper_deck',
    'metered_fuel_pressure', 'unmetered_fuel_pressure',
    'front_oil_p', 'rear_oil_p', 'oil_temperature',
    'volts', 'amps',
    'egt_1', 'egt_2', 'egt_3', 'egt_4', 'egt_5', 'egt_6',
    'cht_1', 'cht_2', 'cht_3', 'cht_4', 'cht_5', 'cht_6',
    'oat', 'tit', 'cdt', 'iat_carb', 'mag_drop',
]

# ASCII code for 'R' — first byte of every "RTDOA,..." line from the MVP-50
RTDOA_STREAM_MARKER = 82

ser = None
document_count = 0


def create_serial() -> serial.Serial:
    """Open a new serial connection to the MVP-50 on COM3."""
    return serial.Serial(port=SERIAL_PORT, baudrate=BAUDRATE, timeout=SERIAL_TIMEOUT)


async def open_serial_with_startup_timeout() -> serial.Serial:
    """
    Retry opening COM3 until the MVP-50 USB device is available.

    Gives the operator up to STARTUP_CONNECT_TIMEOUT_SEC to plug in the device.
    Exits with code 1 if the port never becomes available within that window.
    """
    start = time.time()
    while True:
        try:
            port = create_serial()
            print(f"Connected to {SERIAL_PORT}.")
            return port
        except (serial.SerialException, OSError) as e:
            elapsed = time.time() - start
            if elapsed >= STARTUP_CONNECT_TIMEOUT_SEC:
                print(
                    f"Failed to open {SERIAL_PORT} within "
                    f"{STARTUP_CONNECT_TIMEOUT_SEC}s: {e}"
                )
                sys.exit(1)
            remaining = STARTUP_CONNECT_TIMEOUT_SEC - elapsed
            print(f"Waiting for {SERIAL_PORT}... ({remaining:.0f}s remaining)")
            await asyncio.sleep(CONNECT_RETRY_INTERVAL_SEC)


async def wait_for_stream_start(port: serial.Serial) -> None:
    """
    Block until the MVP-50 sends its first RTDOA byte.

    Once COM3 is open the device may still be idle; this waits indefinitely
    (no timeout) for the first 'R' byte that marks the start of a data line.
    Empty reads are handled safely — no crash on timeout.
    """
    print("Waiting for MVP-50 data stream...")
    while True:
        # Run blocking serial I/O in a thread so the asyncio loop stays responsive
        line = await asyncio.to_thread(port.readline)
        if line and line[0] == RTDOA_STREAM_MARKER:
            print("Data stream detected.")
            return


async def insert_data(data: Dict[str, Any]) -> None:
    """Insert one parsed telemetry document into MongoDB and log timing."""
    global document_count
    start_insert_time = time.time()
    await collection.insert_one(data)
    end_insert_time = time.time()

    document_count += 1
    time_elapsed = end_insert_time - start_insert_time
    insertion_rate = 1 / time_elapsed if time_elapsed > 0 else 0

    print(f"Inserted 1 document in {time_elapsed:.4f} seconds")
    print(f"Insertion rate: {insertion_rate:.2f} documents per second")


async def parse_rtdoa(rtdo: str) -> None:
    """
    Parse one RTDOA line from the MVP-50 and insert it into MongoDB.

    Expected format: RTDOA,<manifold_pressure>,<rpm>,...
    Timestamps are stored in Atlantic Standard Time (America/Halifax).
    """
    parts = rtdo.strip().split(',')
    if parts[0] != 'RTDOA':
        return

    try:
        utc_now = datetime.datetime.now(datetime.UTC)
        ast_tz = pytz.timezone('America/Halifax')
        ast_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ast_tz)

        data = {
            'timestamp': ast_now.isoformat(),
            'fields': {},
        }

        for i, field_name in enumerate(RTDOA_FIELD_NAMES):
            if i + 1 < len(parts):
                try:
                    data['fields'][field_name] = float(parts[i + 1])
                except ValueError:
                    data['fields'][field_name] = parts[i + 1]

        try:
            await insert_data(data)
        except Exception as e:
            # Keep reading serial data even if MongoDB is temporarily unavailable
            print(f"Error inserting data: {e}")

    except (ValueError, IndexError) as e:
        print(f"Error parsing data: {e}")


async def read_serial_data() -> None:
    """
    Main read loop — continuously read RTDOA lines and parse them.

    Reconnects automatically if the USB cable is unplugged mid-run.
    Each readline() waits up to SERIAL_TIMEOUT seconds; empty reads are skipped.
    """
    global ser

    while True:
        try:
            if not ser.is_open:
                print("Serial port closed. Attempting to reconnect...")
                try:
                    ser.close()
                except Exception:
                    pass
                await asyncio.sleep(CONNECT_RETRY_INTERVAL_SEC)
                ser = create_serial()
                print("Reconnected to serial port.")

            line = await asyncio.to_thread(ser.readline)
            if line:
                rtdo = line.decode('ascii', errors='ignore')
                if rtdo:
                    await parse_rtdoa(rtdo)

        except (serial.SerialException, OSError) as e:
            print(f"Serial connection lost: {e}")
            print("Waiting for device to reconnect...")
            try:
                ser.close()
            except Exception:
                pass
            await asyncio.sleep(RECONNECT_INTERVAL_SEC)

        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(CONNECT_RETRY_INTERVAL_SEC)


async def main() -> None:
    """
    Entry point: connect to COM3, wait for data, then run the read loop.

    Exits cleanly on KeyboardInterrupt (Ctrl+C) or when terminated by the dashboard.
    """
    global ser

    try:
        ser = await open_serial_with_startup_timeout()
        await wait_for_stream_start(ser)
        await read_serial_data()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting cleanly...")
    finally:
        if ser is not None and ser.is_open:
            ser.close()
            print("Serial port closed.")


if __name__ == "__main__":
    asyncio.run(main())
