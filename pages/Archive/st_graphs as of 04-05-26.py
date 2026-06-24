# import streamlit as st
# import pymongo
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# import time
# import motor.motor_asyncio
# from motor.motor_asyncio import AsyncIOMotorClient
# import asyncio
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# # Ensure the user has selected an engine
# if 'logo' not in st.session_state: #or st.session_state.selected_engine is None:
#     st.warning("Initialization incomplete. Redirecting to main page...")
#     time.sleep(1)
#     st.switch_page(r"C:\Users\KieranCalder\Code\AerotecTestCell\pages\st_main.py")  # Redirect back to engine selection

# elif 'page_icon' not in st.session_state:
#     st.warning("Initialization incomplete. Redirecting to main page...")
#     time.sleep(1)
#     st.switch_page(r"C:\Users\KieranCalder\Code\AerotecTestCell\pages\st_main.py")  # Redirect back to engine selection

# st.logo(st.session_state.logo)

# # # Check id db_name and collection_name are in session state
# # if 'db_name' not in st.session_state:
# #     st.session_state.db_name = None
# # elif 'collection_name' not in st.session_state:
# #     st.session_state.collection_name = None


# # MongoDB Local Database Connection
# uri = "mongodb://localhost:27017/"
# client = motor.motor_asyncio.AsyncIOMotorClient(uri)
# # global databases
# # databases = client.list_database_names()
# # db = client['RTDO']
# # db_str = str(st.session_state.db_name)
# # db = client[db_str]

# # Single collection for all data points
# # collection = db['Data']
# # collection_str = str(st.session_state.collection_name)
# # collection = db[collection_str]

# # Global variable to hold the fetched data
# global fetched_data
# fetched_data = None

# # Initialize a single event loop
# # loop = asyncio.get_event_loop()


# # Function to get list of databases
# async def get_database_names():
#     # return client.list_database_names()
#     return await client.list_database_names()

# # Function to get list of collections
# async def get_collection_names(db):
#     database = client[db]
#     # return database.list_collection_names()
#     return await database.list_collection_names()

# # Function to create index on the timestamp field
# async def create_index(collection):
#     await collection.create_index([("timestamp", pymongo.ASCENDING)])

# async def fetch_data(collection):
#     global fetched_data  # Access the global variable
    
#     # # Check if data has already been fetched for the specified interval
#     # if fetched_data is not None:
#     #     return fetched_data#, start_time_str, end_time_str

#     # start_time = start_time_str
#     # end_time = end_time_str

#     # MongoDB query to fetch data within time range
#     pipeline = [
#         # {
#         #     "$match": {
#         #         "timestamp": {
#         #             "$gte": start_time,
#         #             "$lte": end_time
#         #         }
#         #     }
#         # },
#         {"$sort": {"timestamp": 1}},  # Sort by timestamp, oldest first
#         {
#             "$project": {
#                 "timestamp": 1,
#                 "volts": "$fields.volts",
#                 "manifold_pressure": "$fields.manifold_pressure",
#                 "rpm": "$fields.rpm",
#                 "hp": "$fields.hp",
#                 "fuel_flow": "$fields.fuel_flow",
#                 "fuel_pressure": "$fields.fuel_pressure",
#                 "front_oil_p": "$fields.front_oil_p",
#                 "rear_oil_p": "$fields.rear_oil_p",
#                 "oil_temperature": "$fields.oil_temperature",
#                 "amps": "$fields.amps",
#                 "cdt": "$fields.cdt",
#                 "tit": "$fields.tit",
#                 "iat_carb": "$fields.iat_carb",
#                 "oat": "$fields.oat",
#                 "mag_drop": "$fields.mag_drop",
#                 "egt_1": "$fields.egt_1",
#                 "egt_2": "$fields.egt_2",
#                 "egt_3": "$fields.egt_3",
#                 "egt_4": "$fields.egt_4",
#                 "egt_5": "$fields.egt_5",
#                 "egt_6": "$fields.egt_6",
#                 "cht_1": "$fields.cht_1",
#                 "cht_2": "$fields.cht_2",
#                 "cht_3": "$fields.cht_3",
#                 "cht_4": "$fields.cht_4",
#                 "cht_5": "$fields.cht_5",
#                 "cht_6": "$fields.cht_6",
#             }
#         }
#     ]

#     cursor = collection.aggregate(pipeline)
#     # cursor = collection.find({})
#     data_list = []
#     async for document in cursor:
#         data_list.append(document)

#     # Convert to pandas DataFrame and store it globally
#     fetched_data = pd.DataFrame(data_list)
#     return fetched_data#, start_time, end_time

# # Function to run async tasks and fetch data
# async def run_fetch(selected_db, selected_collection):
#     collection = client[selected_db][selected_collection]
#     await create_index(collection)
#     fetched_data = await fetch_data(collection)
#     return fetched_data


# # Function to plot selected fields
# # @st.fragment(run_every=1)
# def plot_fields(fetched_data, selected_fields):
#     # st.title("Engine Data Plot")

#     start_time = time.time()  # Start timer
    
#     with st.spinner("Please Wait...."):

#         # Use the fetched data directly instead of calling fetch_data()
#         data = fetched_data
#         # Format the timestamp to datetime
#         data['timestamp'] = pd.to_datetime(data['timestamp'])
        
#         # Filter to retain only the timestamp and selected fields
#         filtered_data = data[['timestamp'] + selected_fields]  # Keep only the timestamp and selected fields
        
#         # Sort data by timestamp to ensure ascending order
#         filtered_data = filtered_data.sort_values(['timestamp'], ascending=True)

#         # Convert all fields except 'timestamp' to numeric, errors='coerce' will convert invalid parsing to NaN
#         filtered_data.loc[:, filtered_data.columns != 'timestamp'] = filtered_data.loc[:, filtered_data.columns != 'timestamp'].apply(pd.to_numeric, errors='coerce')

#         # Group the data for downsampling (e.g., grouping by 3 rows and taking the mean)
#         numeric_data = filtered_data.loc[:, filtered_data.columns != 'timestamp']  # Exclude timestamp from the mean operation

#         # Perform the aggregation, grouping by the index
#         filtered_data = numeric_data.groupby(filtered_data.index // 3).mean()  # Adjust the downsampling factor as needed

#         # Reattach the 'timestamp' to the filtered data, downsample it separately
#         filtered_data['timestamp'] = data['timestamp'].iloc[::3].reset_index(drop=True)

#         # st.write(selected_fields)
        
#         if not filtered_data.empty:
#             fig = px.line(filtered_data,
#                            x='timestamp',
#                            y=selected_fields,
#                            title=f"Engine Data over Time. Timestamp: {st.session_state.selected_collection}")
            
#             # Update layout and styling
#             fig.update_layout(
#                 xaxis=dict(
#                     title="Timestamp",
#                     autorange = True,
#                     # range=[df_indexed['timestamp'].iloc[0], df_indexed['timestamp'].iloc[-1]],  # Autoscale x-axis
#                 ),
#                 yaxis=dict(
#                     title="Values",
#                     autorange = True,
#                     # range=[y_min, y_max]  # Consistent y-axis range
#                 )
#             )
            
#             st.plotly_chart(fig)
#         else:
#             st.warning("No data found between the specified times.")
        
#     end_time = time.time()  # End timer
#     time_taken = end_time - start_time
#     # st.write(f"Data fetched and plotted in {time_taken:.2f} seconds.")


# # Replay functionality with batch fetching and dynamic field selection
# # @st.fragment
# # def replay_plot(fetched_data, selected_fields):
# #     # Start the timer to track performance
# #     start_time = time.time()

# #     with st.spinner("Please Wait..."):
# #         # Check if fetched_data is empty
# #         data = fetched_data

# #         # st.write(data)
        
# #         if data.empty:
# #             st.warning("No data available for the selected time period.")
# #             return
        
# #         # Format the timestamp to datetime
# #         data['timestamp'] = pd.to_datetime(data['timestamp'])
        
# #         # Filter to retain only the timestamp and selected fields
# #         filtered_data = data[['timestamp'] + selected_fields]  # Keep only the timestamp and selected fields
        
# #         # Sort data by timestamp to ensure ascending order
# #         filtered_data = filtered_data.sort_values(['timestamp'], ascending=True)

# #         # Downsample the data
# #         downsample_factor = 2  # Adjust this factor as needed
# #         # filtered_data = filtered_data.iloc[::downsample_factor]

# #         # Convert all fields except 'timestamp' to numeric, errors='coerce' will convert invalid parsing to NaN
# #         filtered_data.loc[:, filtered_data.columns != 'timestamp'] = filtered_data.loc[:, filtered_data.columns != 'timestamp'].apply(pd.to_numeric, errors='coerce')

# #         # Group the data for downsampling (e.g., grouping by 3 rows and taking the mean)
# #         numeric_data = filtered_data.loc[:, filtered_data.columns != 'timestamp']  # Exclude timestamp from the mean operation

# #         # Perform the aggregation, grouping by the index
# #         filtered_data = numeric_data.groupby(filtered_data.index // 3).mean()  # Adjust the downsampling factor as needed

# #         # Reattach the 'timestamp' to the filtered data, downsample it separately
# #         filtered_data['timestamp'] = data['timestamp'].iloc[::3].reset_index(drop=True)

# #         # st.write(len(data))
# #         # st.write(data)
        

# #         # Prepare a DataFrame to hold the indexed replay data
# #         df_indexed = pd.DataFrame()
# #         # df_indexed = filtered_data
# #         # df_indexed['frame'] = np.arange(len(df_indexed))

# #         # st.write(len(df_indexed))
# #         # st.write(df_indexed)

# #         # Create cumulative data for animation
# #         for frame_number in range(len(filtered_data)):
# #             # Select all rows up to the current frame number
# #             df_frame = filtered_data.iloc[:frame_number + 1].copy()
# #             df_frame['frame'] = frame_number  # Add frame number
# #             df_indexed = pd.concat([df_indexed, df_frame])

# #         # st.write(len(df_indexed))
# #         # st.write(df_indexed)

# #         index_end = time.time()
# #         index_time = index_end - start_time
# #         # st.write(f"Indexing duration was: {index_time:.2f} seconds")

# #         plot_start = time.time()

# #         # Ensure that selected_fields contains valid column names
# #         if isinstance(selected_fields, list) and all(field in data.columns for field in selected_fields):
# #             # Get the minimum and maximum values across all selected fields
# #             y_min = data[selected_fields].min().min()  # Min across all selected fields
# #             y_max = data[selected_fields].max().max()  # Max across all selected fields

# #         # Plot using Plotly Express for the line plot
# #         fig = px.line(
# #             df_indexed,
# #             x='timestamp',
# #             y=selected_fields,  # Dynamic selection of y fields
# #             animation_frame='frame',
# #             title=f"Engine Data Replay. Timestamp: {st.session_state.selected_collection}",
# #             range_x=[df_indexed['timestamp'].iloc[0], df_indexed['timestamp'].iloc[-1]],
# #             range_y=[y_min, y_max]
# #         )

# #         # Set the animation speed (frame duration in milliseconds)
# #         fig.update_layout(updatemenus=[dict(
# #             type='buttons',
# #             showactive=False,
# #             buttons=[
# #                 dict(label='Play',
# #                         method='animate',
# #                         args=[None, dict(frame=dict(duration=1), mode='immediate', redraw=True)]),
# #                 dict(label='Pause',
# #                         method='animate',
# #                         args=[[None], dict(mode='immediate', frame=dict(duration=0), redraw=True)])  # Stops the animation
# #             ]
# #         )])

# #         fig.update_layout(

# #         )

# #         # Update layout and styling
# #         fig.update_layout(
# #             xaxis=dict(
# #                 title="Timestamp",
# #                 # autorange = True,
# #                 range=[df_indexed['timestamp'].iloc[0], df_indexed['timestamp'].iloc[-1]],  # Autoscale x-axis
# #             ),
# #             yaxis=dict(
# #                 title="Values",
# #                 autorange = True,
# #                 # range=[y_min, y_max]  # Consistent y-axis range
# #             )
# #         )

# #     # Display the plot
# #     st.plotly_chart(fig)

# #     # End the timer and display the time taken for fetching and plotting
# #     end_time = time.time()
# #     plot_time = end_time - plot_start



# # @st.fragment(run_every=0.5)
# def checkboxes():
#     # User selects fields to plot
#     field_options = [
#         "volts", "manifold_pressure", "rpm", "hp", "fuel_flow", 
#         "fuel_pressure", "front_oil_p", "rear_oil_p", "oil_temperature", 
#         "amps", "cdt", "tit", "iat_carb", "oat", "mag_drop", "cht_1",
#         "cht_2", "cht_3", "cht_4", "cht_5", "cht_6", "egt_1", "egt_2",
#         "egt_3", "egt_4", "egt_5", "egt_6"  
#     ]

#     st.write("Select the fields you want to plot:")

#     row1 = st.columns(6, vertical_alignment='center')
#     row2 = st.columns(6, vertical_alignment='center')
#     row3 = st.columns(6, vertical_alignment='center')
#     row4 = st.columns(6, vertical_alignment='center')
#     row5 = st.columns(6, vertical_alignment='center')
#     row6 = st.columns(6, vertical_alignment='center')

#     # Combine all columns into a single list
#     all_columns = row1 + row2 + row3 + row4 + row5 + row6 #+ row7 + row8

#     selected_fields = []
#     # selected_fields = st.multiselect("Select fields to plot:", field_options)
#     # st.write(f"Field Options", field_options)
    
#     for i, field in enumerate(field_options):
#         # Place checkboxes within the grid
#         col = all_columns[i % len(all_columns)]
#         with col.container(height=60):
#             if st.checkbox(field, value=False, key=f'fieldsCheck{i}'):
#                 selected_fields.append(field)

#     st.session_state.selected_fields = selected_fields

# # Asynchronous main logic
# async def main_async():
#     if st.session_state.get('databases') is None:
#         # databases = await get_database_names()
#         # st.session_state.databases = databases
#         st.session_state.databases = await get_database_names()
        

#     st.session_state.selected_db = st.selectbox("Kindly Choose a Database", st.session_state.databases)

#     if st.session_state.selected_db:
#         # if st.session_state.get('collections') is None:
#         st.session_state.collections = await get_collection_names(st.session_state.selected_db)
#             # collections = await get_collection_names(selected_db)
#             # st.session_state.collections = collections

#         st.session_state.selected_collection = st.selectbox("Kindly select a collection", st.session_state.collections)
#         # selected_collection = st.selectbox("Kindly select a collection", st.session_state.collections)

#         if st.session_state.selected_collection:
#             if st.button("Fetch Data"):
#                 st.session_state.collection = client[st.session_state.selected_db][st.session_state.selected_collection]
#                 await create_index(st.session_state.collection)
#                 st.session_state.fetched_data = await fetch_data(st.session_state.collection)
#                 # collection = client[selected_db][selected_collection]
#                 # st.session_state.collection = collection
#                 # await create_index(collection)
#                 # fetched_data = await fetch_data(collection)
#                 # st.session_state.fetched_data = fetched_data
#                 # st.write(st.session_state.fetched_data)

#             checkboxes()
#                 # st.write(st.session_state.selected_fields)
            
                        
#             col1, col2, col3 = st.columns([0.001, 1, 0.001])
#             # # st.write(f"Selected Fields", selected_fields)
#             if st.session_state.selected_fields:  # Proceed only if fields are selected
#             # if st.button("Refresh Plots"):
#                 with col2:
#                     with st.container(height=550):
#                         # Call plot task with selected fields
#                         # await plot_fields(st.session_state.fetched_data, st.session_state.selected_fields)  # Await directly here
#                         plot_fields(st.session_state.fetched_data, st.session_state.selected_fields)

#                 # with col3:
#                 #     with st.container(height=550):
#                 #         # await replay_plot(st.session_state.fetched_date, st.session_state.selected_fields)  # Await directly here
#                 #         # replay_plot(st.session_state.fetched_data, st.session_state.selected_fields)
#                 #         await asyncio.gather(replay_plot(st.session_state.fetched_data, st.session_state.selected_fields))

#             else:
#                 st.warning("Please select at least one field to plot.")
        
        

# if __name__ == "__main__":
#     asyncio.run(main_async())
#     # main()


# import streamlit as st
# import pymongo
# import pandas as pd
# import plotly.express as px
# import motor.motor_asyncio
# import asyncio
# import time

# # --- Page Config & Navigation Checks ---
# # (Keeping your original checks, though distinct file paths might need adjustment on different machines)
# if 'logo' not in st.session_state:
#     # Fallback to avoid crashing if run independently for testing
#     st.session_state.logo = None 
#     # st.warning("Initialization incomplete. Redirecting...")
#     # time.sleep(1)
#     # st.switch_page(r"C:\Users\KieranCalder\Code\AerotecTestCell\pages\st_main.py")

# # --- MongoDB Connection ---
# uri = "mongodb://localhost:27017/"
# client = motor.motor_asyncio.AsyncIOMotorClient(uri)

# # --- Global State Initialization ---
# if 'data_slots' not in st.session_state:
#     # We will store data for up to 3 slots here: {1: df, 2: df, 3: df}
#     st.session_state.data_slots = {} 

# if 'slot_configs' not in st.session_state:
#     # Stores which DB/Collection is selected for which slot
#     st.session_state.slot_configs = {1: {}, 2: {}, 3: {}}

# # --- Helper Functions ---

# async def get_database_names():
#     return await client.list_database_names()

# async def get_collection_names(db_name):
#     database = client[db_name]
#     return await database.list_collection_names()

# async def create_index(collection):
#     await collection.create_index([("timestamp", pymongo.ASCENDING)])

# async def fetch_data_for_slot(db_name, col_name, slot_index):
#     """
#     Fetches data for a specific slot. 
#     Returns a tuple: (slot_index, DataFrame)
#     """
#     try:
#         collection = client[db_name][col_name]
#         await create_index(collection)

#         # Pipeline: Flatten fields and sort
#         pipeline = [
#             {"$sort": {"timestamp": 1}},
#             {
#                 "$project": {
#                     "timestamp": 1,
#                     "volts": "$fields.volts",
#                     "manifold_pressure": "$fields.manifold_pressure",
#                     "rpm": "$fields.rpm",
#                     "hp": "$fields.hp",
#                     "fuel_flow": "$fields.fuel_flow",
#                     "fuel_pressure": "$fields.fuel_pressure",
#                     "front_oil_p": "$fields.front_oil_p",
#                     "rear_oil_p": "$fields.rear_oil_p",
#                     "oil_temperature": "$fields.oil_temperature",
#                     "amps": "$fields.amps",
#                     "cdt": "$fields.cdt",
#                     "tit": "$fields.tit",
#                     "iat_carb": "$fields.iat_carb",
#                     "oat": "$fields.oat",
#                     "mag_drop": "$fields.mag_drop",
#                     "egt_1": "$fields.egt_1", "egt_2": "$fields.egt_2",
#                     "egt_3": "$fields.egt_3", "egt_4": "$fields.egt_4",
#                     "egt_5": "$fields.egt_5", "egt_6": "$fields.egt_6",
#                     "cht_1": "$fields.cht_1", "cht_2": "$fields.cht_2",
#                     "cht_3": "$fields.cht_3", "cht_4": "$fields.cht_4",
#                     "cht_5": "$fields.cht_5", "cht_6": "$fields.cht_6",
#                 }
#             }
#         ]
        
#         cursor = collection.aggregate(pipeline)
#         data_list = await cursor.to_list(length=None) # More efficient asyncio method
        
#         if not data_list:
#             return slot_index, pd.DataFrame()

#         df = pd.DataFrame(data_list)
#         return slot_index, df

#     except Exception as e:
#         st.error(f"Error fetching data for Dataset {slot_index}: {e}")
#         return slot_index, pd.DataFrame()


# # def plot_fields(fetched_data, selected_fields):
# #     # st.title("Engine Data Plot")

# #     start_time = time.time()  # Start timer
    
# #     with st.spinner("Please Wait...."):

# #         # Use the fetched data directly instead of calling fetch_data()
# #         data = fetched_data
# #         # Format the timestamp to datetime
# #         data['timestamp'] = pd.to_datetime(data['timestamp'])
        
# #         # Filter to retain only the timestamp and selected fields
# #         filtered_data = data[['timestamp'] + selected_fields]  # Keep only the timestamp and selected fields
        
# #         # Sort data by timestamp to ensure ascending order
# #         filtered_data = filtered_data.sort_values(['timestamp'], ascending=True)

# #         # Convert all fields except 'timestamp' to numeric, errors='coerce' will convert invalid parsing to NaN
# #         filtered_data.loc[:, filtered_data.columns != 'timestamp'] = filtered_data.loc[:, filtered_data.columns != 'timestamp'].apply(pd.to_numeric, errors='coerce')

# #         # Group the data for downsampling (e.g., grouping by 3 rows and taking the mean)
# #         numeric_data = filtered_data.loc[:, filtered_data.columns != 'timestamp']  # Exclude timestamp from the mean operation

# #         # Perform the aggregation, grouping by the index
# #         filtered_data = numeric_data.groupby(filtered_data.index // 3).mean()  # Adjust the downsampling factor as needed

# #         # Reattach the 'timestamp' to the filtered data, downsample it separately
# #         filtered_data['timestamp'] = data['timestamp'].iloc[::3].reset_index(drop=True)

# #         # st.write(selected_fields)
        
# #         if not filtered_data.empty:
# #             fig = px.line(filtered_data,
# #                            x='timestamp',
# #                            y=selected_fields,
# #                            title=f"Engine Data over Time. Timestamp: {st.session_state.selected_collection}")
            
# #             # Update layout and styling
# #             fig.update_layout(
# #                 xaxis=dict(
# #                     title="Timestamp",
# #                     autorange = True,
# #                     # range=[df_indexed['timestamp'].iloc[0], df_indexed['timestamp'].iloc[-1]],  # Autoscale x-axis
# #                 ),
# #                 yaxis=dict(
# #                     title="Values",
# #                     autorange = True,
# #                     # range=[y_min, y_max]  # Consistent y-axis range
# #                 )
# #             )
            
# #             st.plotly_chart(fig)
# #         else:
# #             st.warning("No data found between the specified times.")
        
# #     end_time = time.time()  # End timer
# #     time_taken = end_time - start_time
# #     # st.write(f"Data fetched and plotted in {time_taken:.2f} seconds.")


# def plot_fields(dataframe, selected_fields, title_suffix):
#     """
#     Generates a Plotly figure for the given dataframe and selected fields.
#     """
#     if dataframe.empty or not selected_fields:
#         st.warning("No data available.")
#         return

#     # Data Processing
#     data = dataframe.copy()
#     data['timestamp'] = pd.to_datetime(data['timestamp'])
    
#     # Filter columns
#     cols_to_keep = ['timestamp'] + [f for f in selected_fields if f in data.columns]
#     data = data[cols_to_keep]
    
#     # Sort
#     data = data.sort_values('timestamp')

#     # Numeric Conversion
#     numeric_cols = data.columns.drop('timestamp')
#     data[numeric_cols] = data[numeric_cols].apply(pd.to_numeric, errors='coerce')

#     # Downsampling (Mean of every 3 rows) - Preserving your logic
#     if len(data) > 0:
#         numeric_data = data[numeric_cols]
#         downsampled = numeric_data.groupby(data.index // 3).mean()
#         downsampled['timestamp'] = data['timestamp'].iloc[::3].reset_index(drop=True)
#         data = downsampled

#     if data.empty:
#         st.warning("Data empty after processing.")
#         return

#     # Plotting
#     fig = px.line(
#         data,
#         x='timestamp',
#         y=cols_to_keep[1:], # Exclude timestamp from y
#         title=f"Dataset: {title_suffix}"
#     )

#     fig.update_layout(
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         ),
#         margin=dict(l=20, r=20, t=60, b=20),
#         xaxis_title="Time",
#         yaxis_title="Value"
#     )
    
#     # Use container width to fit in columns
#     st.plotly_chart(fig, use_container_width=True)


# def checkboxes():
#     """
#     Master Control: Select fields once, apply to all graphs.
#     """
#     field_options = [
#         "volts", "manifold_pressure", "rpm", "hp", "fuel_flow", 
#         "fuel_pressure", "front_oil_p", "rear_oil_p", "oil_temperature", 
#         "amps", "cdt", "tit", "iat_carb", "oat", "mag_drop", "cht_1",
#         "cht_2", "cht_3", "cht_4", "cht_5", "cht_6", "egt_1", "egt_2",
#         "egt_3", "egt_4", "egt_5", "egt_6"  
#     ]

#     st.markdown("###  Field Selection")
#     st.caption("Select fields to plot across all datasets.")

#     # Create a grid for checkboxes
#     cols = st.columns(6, vertical_alignment='center')
#     selected_fields = []
    
#     for i, field in enumerate(field_options):
#         col = cols[i % 6]
#         with col:
#              # Unique key prevents duplicates
#             if st.checkbox(field, value=False, key=f'master_field_{i}'):
#                 selected_fields.append(field)

#     st.session_state.selected_fields = selected_fields

# # --- Main Async Logic ---
# async def main_async():
#     st.title("Select the runs you would like to compare")
    
#     # 1. Configuration Section (3 Columns)
#     st.markdown("###  Run Selection")
    
#     # Get available databases once
#     if 'available_dbs' not in st.session_state:
#         st.session_state.available_dbs = await get_database_names()

#     config_cols = st.columns(3)
    
#     # Define slots (1, 2, 3)
#     slots = [1, 2, 3]

#     for i, col in zip(slots, config_cols):
#         with col:
#             st.info(f"**Run {i}**")
            
#             # Select Database
#             db_key = f"db_select_{i}"
#             selected_db = st.selectbox(
#                 "Database", 
#                 options=["None"] + st.session_state.available_dbs, 
#                 key=db_key
#             )
            
#             # Select Collection (Dynamic based on DB)
#             selected_col = None
#             if selected_db and selected_db != "None":
#                 collections = await get_collection_names(selected_db)
#                 col_key = f"col_select_{i}"
#                 selected_col = st.selectbox(
#                     "Collection", 
#                     options=collections, 
#                     key=col_key
#                 )
                
#                 # Save config to state
#                 st.session_state.slot_configs[i] = {
#                     'db': selected_db, 
#                     'col': selected_col
#                 }
#             else:
#                  st.session_state.slot_configs[i] = None

#     st.markdown("---")

#     # 2. Fetch Data Button
#     # Logic: Collect all valid configurations and fetch in parallel
#     if st.button("Fetch All Data", type="primary", use_container_width=True):
#         tasks = []
#         valid_slots = []
        
#         with st.spinner("Fetching data from all sources..."):
#             for i in slots:
#                 config = st.session_state.slot_configs[i]
#                 if config and config.get('db') and config.get('col'):
#                     tasks.append(fetch_fetch_data_for_slot(config['db'], config['col'], i))
#                 else:
#                     # clear data if selection removed
#                     st.session_state.data_slots[i] = None

#             if tasks:
#                 # Run all fetches concurrently
#                 results = await asyncio.gather(*tasks)
                
#                 # Store results
#                 for slot_index, df in results:
#                     st.session_state.data_slots[slot_index] = df
#                 st.success("Data fetched successfully!")
#             else:
#                 st.warning("Please select at least one Database and Collection.")

#     # 3. Field Selection (Master Control)
#     # Only show if we have data in at least one slot
#     has_data = any(val is not None and not val.empty for val in st.session_state.data_slots.values())
    
#     if has_data:
#         st.markdown("---")
#         checkboxes() # Renders the grid
        
#         st.markdown("---")
#         st.markdown("###  Analysis")
        
#         # 4. Plotting Section (3 Columns)
#         plot_cols = st.columns(3)
        
#         if st.session_state.selected_fields:
#             for i, col in zip(slots, plot_cols):
#                 with col:
#                     df = st.session_state.data_slots.get(i)
#                     config = st.session_state.slot_configs.get(i)
                    
#                     if df is not None and not df.empty:
#                         col_name = config.get('col', 'Unknown')
#                         plot_fields(df, st.session_state.selected_fields, title_suffix=col_name)
#                     else:
#                         st.container(height=400, border=True).write(f"No Data for Dataset {i}")
#         else:
#             st.info("Select at least one field above to generate graphs.")

# # Wrapper to handle naming conflict in the fetch loop call
# async def fetch_fetch_data_for_slot(db, col, i):
#     return await fetch_data_for_slot(db, col, i)

# if __name__ == "__main__":
#     asyncio.run(main_async())

import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import motor.motor_asyncio
import asyncio

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Engine Run Analysis", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")

# --- Constants & State ---
if 'logo' not in st.session_state:
    st.session_state.logo = None 

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