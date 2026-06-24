import asyncio
import motor.motor_asyncio
import serial
import datetime
# from datetime import datetime
import numpy as np
import pymongo
from pymongo import MongoClient
import urllib.parse
import pytz
import time
from typing import Dict, Any
import random
import sys

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
#
# --------------------- REFERENCE SECTION ---------------------------


# MongoDB credentials and connection string
# username = urllib.parse.quote_plus('Aerotec')  # Add your username here
# password = urllib.parse.quote_plus('1@QWASZX')  # Add your password here

# # MongoDB Atlas Cloud Database Connection
# uri = "mongodb+srv://{}:{}@atlascluster.qrjrg5e.mongodb.net/".format(username, password)
# client = motor.motor_asyncio.AsyncIOMotorClient(uri)
# db = client['MVP50_V2']  # Replace 'MVP50' with your database name

# Get database and collection name from arguments passed by streamlit
db_name = sys.argv[1]
collection_name = sys.argv[2]

# MongoDB Local Database Connection
uri = "mongodb://localhost:27017/"
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client[db_name]

# Single collection for all data points
collection = db[collection_name]




# Initialize serial port
ser = serial.Serial(port='COM3', baudrate=9600, timeout=1)

# Track metrics
start_time = time.time()
document_count = 0

# Read data from serial
checkval = [0]
while(checkval[0] != 82):
    print(checkval[0])
    checkval = ser.readline()

async def insert_data(data: Dict[str, Any]):
    """Insert data into MongoDB and update metrics."""
    global document_count
    start_insert_time = time.time()
    await collection.insert_one(data)
    end_insert_time = time.time()
    
    # Update metrics
    document_count += 1
    time_elapsed = end_insert_time - start_insert_time
    insertion_rate = 1 / time_elapsed if time_elapsed > 0 else 0  # documents per second
    
    print(f"Inserted 1 document in {time_elapsed:.4f} seconds")
    print(f"Insertion rate: {insertion_rate:.2f} documents per second")

async def parse_rtdoa(rtdo: str):
    """Parse the RTDOA data and prepare it for insertion."""
    parts = rtdo.strip().split(',')
    if parts[0] == 'RTDOA':
        try:
            # Get current UTC time and convert to AST
            utc_now = datetime.datetime.now(datetime.UTC)
            ast_tz = pytz.timezone('America/Halifax')  # Atlantic Standard Time (AST) timezone
            ast_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ast_tz)
            timestamp = ast_now.isoformat()  # Use AST timestamp

            # Create a dictionary for the document
            data = {
                'timestamp': timestamp,
                'fields': {}
            }
            # Add Upper Deck Pressure and S Cool
            for i, field_name in enumerate(['manifold_pressure',
                                            'rpm', 
                                            'hp', 
                                            'fuel_flow', 
                                            'upper_deck',
                                            'metered_fuel_pressure',
                                            'unmetered_fuel_pressure',
                                            'front_oil_p',
                                            'rear_oil_p',
                                            'oil_temperature',
                                            'volts',
                                            'amps',
                                            'egt_1',
                                            'egt_2', 
                                            'egt_3', 
                                            'egt_4', 
                                            'egt_5', 
                                            'egt_6',
                                            'cht_1', 
                                            'cht_2', 
                                            'cht_3', 
                                            'cht_4', 
                                            'cht_5', 
                                            'cht_6', 
                                            'oat', 
                                            'tit',
                                            'cdt', 
                                            'iat_carb', 
                                            'mag_drop'
                                            # , 'warn'
                                            ]):
                if i + 1 < len(parts):
                    # data['fields'][field_name] = parts[i + 1]
                    # Add random integer to the value
                    try:
                        value = float(parts[i + 1])  # Convert to float for realistic fluctuation
                        random_fluctuation = random.uniform(-15, 15)  # Adjust range as needed
                        data['fields'][field_name] = value #+ random_fluctuation
                    except ValueError:
                        data['fields'][field_name] = parts[i + 1]  # Keep as string if conversion fails
                # random_fluctuation = random.uniform(-15, 15)  # Adjust range as needed
            await insert_data(data)
        except (ValueError, IndexError) as e:
            print(f"Error parsing data: {e}")

# async def read_serial_data():
#     """Read data from the serial port asynchronously."""
#     while True:
#         rtdo = ser.readline().decode('ascii')
#         if rtdo:
#             await parse_rtdoa(rtdo)

async def read_serial_data():
    """Continuously read data from the serial port with auto-reconnect."""
    global ser

    while True:
        try:
            # If serial connection is not open, try to reopen it
            if not ser.is_open:
                print("Serial port closed. Attempting to reconnect...")
                ser.close()
                await asyncio.sleep(2)
                ser = serial.Serial(port='COM4', baudrate=9600, timeout=1)
                print("Reconnected to serial port.")

            # Read a line from the serial device
            rtdo = ser.readline().decode('ascii', errors='ignore')
            if rtdo:
                await parse_rtdoa(rtdo)

        except (serial.SerialException, OSError) as e:
            print(f"Serial connection lost: {e}")
            print("Waiting for device to reconnect...")
            ser.close()
            await asyncio.sleep(5)  # wait a few seconds before retrying

        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(2)


# async def main():
#     # Ensure the serial port is open
#     if ser.is_open:
#         try:
#             await read_serial_data()
#         except KeyboardInterrupt:
#             print("\nProgram interrupted. Exiting...")
#         finally:
#             # Close serial port connection
#             ser.close()
#             print("Serial port closed.")
#     else:
#         print("Failed to open serial port.")

async def main():
    """Main supervisor loop that keeps trying to read serial data indefinitely."""
    global ser

    while True:
        try:
            # Ensure serial port is open or try to reopen
            if not ser.is_open:
                print("Opening serial port...")
                ser.open()
            
            # Start reading data
            await read_serial_data()

        except (serial.SerialException, OSError) as e:
            print(f"Serial connection error in main: {e}")
            print("Attempting to reconnect in 5 seconds...")
            try:
                ser.close()
            except:
                pass
            await asyncio.sleep(5)

        except KeyboardInterrupt:
            print("\nProgram interrupted. Exiting cleanly...")
            break

        except Exception as e:
            print(f"Unexpected error in main: {e}")
            await asyncio.sleep(2)

    # Clean up before exit
    if ser.is_open:
        ser.close()
        print("Serial port closed.")



# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())


# # Parse csv data
# import asyncio
# import motor.motor_asyncio
# import datetime
# import pytz
# import time
# import random
# import sys
# import csv
# from typing import Dict, Any
# import re

# # -------------------- MongoDB setup --------------------
# db_name = sys.argv[1]
# collection_name = sys.argv[2]
# # db_name = "testdb"
# # collection_name = "testcoll"

# uri = "mongodb://localhost:27017/"
# client = motor.motor_asyncio.AsyncIOMotorClient(uri)
# db = client[db_name]
# collection = db[collection_name]

# # -------------------- Global tracking --------------------
# document_count = 0

# # -------------------- Field list --------------------
# FIELD_NAMES = [
#     'manifold_pressure', 'rpm', 'hp', 'fuel_flow', 'metered_fuel_pressure', 'unmetered_fuel_pressure',
#     'front_oil_p', 'rear_oil_p', 'oil_temperature', 'volts', 'amps',
#     'egt_1', 'egt_2', 'egt_3', 'egt_4', 'egt_5', 'egt_6',
#     'cht_1', 'cht_2', 'cht_3', 'cht_4', 'cht_5', 'cht_6',
#     'oat', 'tit', 'cdt', 'iat_carb', 'mag_drop'
# ]

# # -------------------- Insert function --------------------
# async def insert_data(data: Dict[str, Any]):
#     """Insert a document into MongoDB asynchronously and report timing."""
#     global document_count
#     start_insert_time = time.time()
#     await collection.insert_one(data)
#     end_insert_time = time.time()

#     document_count += 1
#     time_elapsed = end_insert_time - start_insert_time
#     insertion_rate = 1 / time_elapsed if time_elapsed > 0 else 0
#     print(f"Inserted {document_count} docs total | last insert {time_elapsed:.4f}s | rate {insertion_rate:.2f} docs/s")

# # -------------------- Parse RTDOA line --------------------
# async def parse_rtdoa(rtdo: str):
#     """Parse the RTDOA data (supports comma- or tab-separated lines)."""
#     # split on commas or tabs (consecutive separators handled)
#     parts = re.split(r'[,\t]+', rtdo.strip())
#     if not parts:
#         return

#     if parts[0].upper() != 'RTDOA':
#         return

#     try:
#         # timestamp as before (AST)
#         utc_now = datetime.datetime.now(datetime.UTC)
#         ast_tz = pytz.timezone('America/Halifax')
#         ast_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ast_tz)
#         timestamp = ast_now.isoformat()

#         data = {'timestamp': timestamp, 'fields': {}}

#         # fields in parts start at index 1
#         for i, field_name in enumerate(FIELD_NAMES):
#             part_index = 1 + i
#             if part_index < len(parts):
#                 raw = parts[part_index]
#                 # try convert to float (keep string if fails)
#                 try:
#                     value = float(raw)
#                 except Exception:
#                     value = raw
#                 data['fields'][field_name] = value
#         await insert_data(data)
#     except Exception as e:
#         print(f"Error parsing RTDOA line: {e}")

# # -------------------- CSV Reader --------------------
# async def read_csv_data(csv_path: str):
#     rate = 3  # lines per second
#     delay = 1 / rate  # seconds between lines

#     while True:  # infinite loop
#         with open(csv_path, 'r', newline='') as f:
#             for line in f:
#                 line = line.strip()
#                 if not line:
#                     continue
#                 await parse_rtdoa(line)
#                 await asyncio.sleep(delay)  # throttle the loop

#         print(f"Reached end of CSV — restarting from top...")


# # -------------------- Entry point --------------------
# async def main():
#     # if len(sys.argv) < 4:
#     #     print("Usage: python parse_data_csv.py <db_name> <collection_name> <csv_path>")
#     #     sys.exit(1)

#     csv_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\Old Test Data\CSV\Lycoming-O-320-E2D-2026-01-14\Lycoming-O-320-E2D-2026-01-14-12-01-21 (150HP).csv"
#     await read_csv_data(csv_path)

# if __name__ == "__main__":
#     asyncio.run(main())

