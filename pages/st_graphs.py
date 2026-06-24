import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import motor.motor_asyncio
import asyncio
import time

# --- Page Config ---
st.set_page_config(layout="wide", 
                   page_title="Engine Run Analysis", 
                   page_icon=st.session_state.get("page_icon", ":small_airplane:"), 
                   initial_sidebar_state="collapsed")

# Pages File Paths
main_page_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\st_main.py"
dashboard_page_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\pages\st_dashboard.py"

# --- Constants & State ---
if 'logo' not in st.session_state: #or st.session_state.selected_engine is None:
    st.warning("Initialization incomplete. Redirecting to main page...")
    time.sleep(1)
    st.switch_page(main_page_path)  # Redirect back to engine selection

elif 'page_icon' not in st.session_state:
    st.warning("Initialization incomplete. Redirecting to main page...")
    time.sleep(1)
    st.switch_page(main_page_path)  # Redirect back to engine selection

uri = "mongodb://localhost:27017/"
client = motor.motor_asyncio.AsyncIOMotorClient(uri)

# Define Groups
FIELD_GROUPS = {
    "EGTs (Exhaust Gas Temp)": ["egt_1", "egt_2", "egt_3", "egt_4", "egt_5", "egt_6", "tit"],
    "CHTs (Cyl Head Temp)": ["cht_1", "cht_2", "cht_3", "cht_4", "cht_5", "cht_6"],
    "Pressures": ["manifold_pressure", "metered_fuel_pressure", "unmetered_fuel_pressure", "front_oil_p", "rear_oil_p"],
    "Electrical": ["volts", "amps"],
    "Temperatures (Misc)": ["oil_temperature", "iat_carb", "oat", "cdt"],
    "Power & Fuel": ["hp", "fuel_flow", "mag_drop"]
}

# Flatten groups to get a master list of all fields for Custom Mode
ALL_FIELDS = []
for fields in FIELD_GROUPS.values():
    ALL_FIELDS.extend(fields)
# Remove duplicates just in case
ALL_FIELDS = list(set(ALL_FIELDS))
ALL_FIELDS.sort()

if 'data_slots' not in st.session_state:
    st.session_state.data_slots = {} 
if 'slot_configs' not in st.session_state:
    st.session_state.slot_configs = {1: {}, 2: {}, 3: {}}

# --- Helper Functions ---

async def get_database_names():
    return await client.list_database_names()

async def get_collection_names(db_name):
    database = client[db_name]
    return await database.list_collection_names()

async def create_index(collection):
    await collection.create_index([("timestamp", pymongo.ASCENDING)])

async def fetch_data_for_slot(db_name, col_name, slot_index):
    try:
        collection = client[db_name][col_name]
        await create_index(collection)
        
        pipeline = [
            {"$sort": {"timestamp": 1}},
            {
                "$project": {
                    "timestamp": 1,
                    "volts": "$fields.volts",
                    "manifold_pressure": "$fields.manifold_pressure",
                    "rpm": "$fields.rpm",
                    "hp": "$fields.hp",
                    "fuel_flow": "$fields.fuel_flow",
                    "metered_fuel_pressure": "$fields.metered_fuel_pressure",
                    "unmetered_fuel_pressure": "$fields.unmetered_fuel_pressure",
                    "front_oil_p": "$fields.front_oil_p",
                    "rear_oil_p": "$fields.rear_oil_p",
                    "oil_temperature": "$fields.oil_temperature",
                    "amps": "$fields.amps",
                    "cdt": "$fields.cdt",
                    "tit": "$fields.tit",
                    "iat_carb": "$fields.iat_carb",
                    "oat": "$fields.oat",
                    "mag_drop": "$fields.mag_drop",
                    "egt_1": "$fields.egt_1",
                    "egt_2": "$fields.egt_2",
                    "egt_3": "$fields.egt_3",
                    "egt_4": "$fields.egt_4",
                    "egt_5": "$fields.egt_5",
                    "egt_6": "$fields.egt_6",
                    "cht_1": "$fields.cht_1",
                    "cht_2": "$fields.cht_2",
                    "cht_3": "$fields.cht_3",
                    "cht_4": "$fields.cht_4",
                    "cht_5": "$fields.cht_5",
                    "cht_6": "$fields.cht_6",
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        data_list = await cursor.to_list(length=None)
        
        if not data_list:
            return slot_index, pd.DataFrame()

        df = pd.DataFrame(data_list)
        return slot_index, df

    except Exception as e:
        st.error(f"Error fetching data for Dataset {slot_index}: {e}")
        return slot_index, pd.DataFrame()

async def fetch_data_wrapper(db, col, i):
    return await fetch_data_for_slot(db, col, i)

def generate_dual_axis_plot(dataframe, category_name, fields):
    if dataframe.empty:
        return None

    data = dataframe.copy()
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    valid_fields = [f for f in fields if f in data.columns]
    if not valid_fields:
        return None
    
    numeric_cols = valid_fields + ['rpm']
    numeric_cols = [c for c in numeric_cols if c in data.columns]
    data[numeric_cols] = data[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Downsample
    if len(data) > 0:
        numeric_data = data[numeric_cols]
        downsampled = numeric_data.groupby(data.index // 3).mean()
        downsampled['timestamp'] = data['timestamp'].iloc[::3].reset_index(drop=True)
        data = downsampled

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Left Axis (Selected Fields)
    for field in valid_fields:
        fig.add_trace(
            go.Scatter(x=data['timestamp'], y=data[field], name=field, mode='lines'),
            secondary_y=False,
        )

    # Right Axis (RPM)
    if 'rpm' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data['timestamp'], 
                y=data['rpm'], 
                name="RPM", 
                mode='lines',
                # opacity=0.0,
                # line=dict(color='black', width=1, dash='dot')
            ),
            secondary_y=True,
        )

    # fig.update_layout(
    #     title=f"{category_name} vs RPM",
    #     # legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    #     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    #     margin=dict(l=10, r=10, t=80, b=10),
    #     height=400,
    #     hovermode="x unified"
    # )

    fig.update_layout(
        title=f"{category_name} vs RPM",
        legend=dict(
            orientation="h",     # Horizontal
            yanchor="bottom",    # Anchored at the bottom of the legend box
            y=1.05,              # Pushed slightly higher above the plot (1.02 to 1.05)
            xanchor="center",    # Anchor point is the middle of the legend
            x=0.5                # Positioned at 50% of the plot width
        ),
        margin=dict(l=10, r=10, t=80, b=10), # Increased top margin (t) to make room for the legend
        height=450,                          # Slightly increased height to accommodate legend
        hovermode="x unified"
    )

    fig.update_yaxes(title_text="Value", secondary_y=False)
    fig.update_yaxes(title_text="RPM", secondary_y=True, showgrid=False)

    return fig

def plotting_controls():
    """
    Handles the UI for selecting standard Categories OR Custom Fields.
    """
    st.markdown("### 2. Plotting")
    
    # Toggle for Custom Mode
    custom_mode = st.toggle("Enable Custom Plot Selection", value=False)
    st.session_state.custom_mode = custom_mode

    if custom_mode:
        st.caption("Select specific fields to combine into a custom chart. RPM is always included.")
        
        # Grid layout for all individual fields
        cols = st.columns(6)
        custom_selection = []
        
        for i, field in enumerate(ALL_FIELDS):
            col = cols[i % 6]
            with col:
                if st.checkbox(field, key=f"custom_{field}"):
                    custom_selection.append(field)
        
        st.session_state.custom_selection = custom_selection
        st.session_state.selected_groups = [] # Clear groups to avoid confusion

    else:
        st.caption("Select standard data groups.")
        cols = st.columns(len(FIELD_GROUPS))
        selected_groups = []
        
        for i, (group_name, fields) in enumerate(FIELD_GROUPS.items()):
            col = cols[i % 3]
            with col:
                if st.checkbox(group_name, key=f"group_{i}"):
                    selected_groups.append((group_name, fields))
        
        st.session_state.selected_groups = selected_groups
        st.session_state.custom_selection = []

# --- Main Logic ---
async def main_async():
    st.title("Engine Data Comparison Tool")
    
    # 1. Configuration Section
    st.markdown("### 1. Run Selection")
    if 'available_dbs' not in st.session_state:
        st.session_state.available_dbs = await get_database_names()

    config_cols = st.columns(3)
    slots = [1, 2, 3]

    for i, col in zip(slots, config_cols):
        with col:
            st.info(f"**Selection {i}**")
            selected_db = st.selectbox("Database", ["None"] + st.session_state.available_dbs, key=f"db_{i}")
            selected_col = None
            if selected_db and selected_db != "None":
                collections = await get_collection_names(selected_db)
                selected_col = st.selectbox("Collection", collections, key=f"col_{i}")
                st.session_state.slot_configs[i] = {'db': selected_db, 'col': selected_col}
            else:
                 st.session_state.slot_configs[i] = None

    if st.button("Fetch All Data", type="primary", use_container_width=True):
        tasks = []
        with st.spinner("Fetching..."):
            for i in slots:
                config = st.session_state.slot_configs[i]
                if config and config.get('db') and config.get('col'):
                    tasks.append(fetch_data_wrapper(config['db'], config['col'], i))
                else:
                    st.session_state.data_slots[i] = None
            if tasks:
                results = await asyncio.gather(*tasks)
                for slot_index, df in results:
                    st.session_state.data_slots[slot_index] = df
                st.success("Data Updated")

    # --- Visualization Section ---
    
    # Identify active slots
    active_slot_ids = []
    for i in slots:
        df = st.session_state.data_slots.get(i)
        if df is not None and not df.empty:
            active_slot_ids.append(i)

    if active_slot_ids:
        st.divider()
        plotting_controls() # Shows Categories OR Custom Grid based on Toggle
        st.divider()
        
        # Responsive Columns
        dynamic_cols = st.columns(len(active_slot_ids))
        
        for slot_id, col in zip(active_slot_ids, dynamic_cols):
            with col:
                df = st.session_state.data_slots.get(slot_id)
                config = st.session_state.slot_configs.get(slot_id)
                col_name = config.get('col', 'Unknown')
                
                st.subheader(f"Run {slot_id}: {col_name}")
                
                # BRANCH A: Custom Mode
                if st.session_state.get('custom_mode', False):
                    custom_fields = st.session_state.get('custom_selection', [])
                    if custom_fields:
                        fig = generate_dual_axis_plot(df, "Custom Selection", custom_fields)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No data for selected custom fields.")
                    else:
                        st.info("Select fields above to generate custom plot.")

                # BRANCH B: Standard Categories
                else:
                    groups = st.session_state.get('selected_groups', [])
                    if groups:
                        for group_name, fields in groups:
                            fig = generate_dual_axis_plot(df, group_name, fields)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning(f"No fields found for {group_name}")
                    else:
                        st.info("Select a category above.")
    else:
        st.info("Please select databases and fetch data to begin.")

if __name__ == "__main__":
    asyncio.run(main_async())