import streamlit as st
import commentjson as json
import sys
# from st_main import pages
import re
from collections import OrderedDict
import time
import os
import json
import pandas as pd
from datetime import date

# Pages File Paths
main_page_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\st_main.py"
dashboard_page_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\pages\st_dashboard.py"

# JSON File Paths
engine_json_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\Engine Configuration.json"
propeller_json_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\Propeller Config.json"
adjustable_json_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\3 Blade Adjustable Propeller Logs.json"

# sys.path.insert(0, r"C:\Users\KieranCalder\Code\AerotecTestCell")

# st.set_page_config(layout="wide", page_title="Select Engine Screen", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")
st.set_page_config(layout="wide", page_title="Engine Selection", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")

# Ensure the user has selected an engine
if 'logo' not in st.session_state: #or st.session_state.selected_engine is None:
    st.warning("Initialization incomplete. Redirecting to main page...")
    time.sleep(1)
    st.switch_page(main_page_path)  # Redirect back to engine selection

elif 'page_icon' not in st.session_state:
    st.warning("Initialization incomplete. Redirecting to main page...")
    time.sleep(1)
    st.switch_page(main_page_path)  # Redirect back to engine selection


# st_autorefresh(3000, key="select_screen_refresh")  # Refresh at a specified interval

# st.set_page_config(layout="wide", page_title="Select Engine Screen", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")
st.logo(st.session_state.logo)

def load_engine_config():
    """Load JSON configuration file."""
    if os.path.exists(engine_json_path):
        with open(engine_json_path, "r") as f:
            return json.load(f, object_pairs_hook=OrderedDict) # Use OrderedDict to maintain order
    
def load_propeller_config():
    """Load JSON configuration file"""
    if os.path.exists(propeller_json_path):
        with open(propeller_json_path, "r") as f:
            return json.load(f)

def load_adjustable_config():
    if os.path.exists(adjustable_json_path):
        with open(adjustable_json_path, "r") as f:
            return json.load(f)

def save_engine_config(updated_engine_config, engine_type):
    """Save updated engine configuration to the JSON file."""
    with open(engine_json_path, "r") as f:
        engine_config_data = json.load(f)

    # Update the configuration for the selected engine type
    engine_config_data[engine_type] = updated_engine_config

    with open(engine_json_path, "w") as f:
        json.dump(engine_config_data, f, indent=4)

    st.rerun()

def save_propeller_config(propeller_data):
    """Save updated propeller configuration to the JSON file."""
    with open(propeller_json_path, "w") as f:
        json.dump(propeller_data, f, indent=4)

def save_adjustable_config(adjustable_data):
    """Save updated ajustable configuration to the JSON file"""
    with open(adjustable_json_path, "w") as f:
        json.dump(adjustable_data, f, indent=4)

def authenticate(password, engine_type):
    """Authenticate the user with a predefined common password for all engines except 'Configurable 4 Cylinder'."""
    # Define a common password for all engines that need authentication
    common_password = '00100'  # Replace with the actual secure password

    # Engine type that does NOT require authentication
    no_auth_engine = 'Configurable Parameters'

    # Check if the engine type requires authentication
    if engine_type != no_auth_engine:
        return password == common_password  # Return True if password matches
    else:
        return True  # No authentication needed for 'Configurable 4 Cylinder'
    

def generate_label_from_key(key):
    """Generate a label by adding spaces before capital letters in the key."""
    # Insert space before each capital letter except when two capital letters are consecutive
    formatted_key = re.sub(r'(?<!^)(?<![A-Z])(?=[A-Z])', ' ', key)
    # Capitalize only the first letter of the entire string
    formatted_key = formatted_key[0].upper() + formatted_key[1:]
    return formatted_key

def generate_fields_from_config(config):
    """Generate fields dynamically from the configuration keys."""
    fields = []
    for key in config.keys():
        label = generate_label_from_key(key)  # Generate label dynamically
        fields.append((label, key))  # Append as (label, key) tuple
    return fields

# Function to initialize engine parameters in st.session_state
def initialize_engine_parameters(engine_type, config):
    """
    Initialize engine parameters in Streamlit's session state.
    
    Args:
    - engine_type (str): The type of engine.
    - config (dict): The loaded configuration dictionary.
    """

    # Ensure that the engine_type exists in the config
    if engine_type not in config:
        st.error(f"Engine type '{engine_type}' not found in configuration.")
        return

    # Loop through the parameters of the specified engine type
    engine_parameters = config[engine_type]
    for key, value in engine_parameters.items():
        # Set the parameters in session_state
        # if key not in st.session_state:
        st.session_state[key] = value

def display_engine_config_parameters(engine_type, engine_config):
    """Display and edit engine configuration json file"""
    st.markdown(f"### Edit {engine_type} Configuration")
    with st.expander(""):
        # col1, col2, col3 = st.columns([2.4, 0.8, 2])
        # with col2:
        #     # Save button to save the configuration
        #     if st.button("Save Configuration"):
        #         save_config(config, engine_type)
        #         st.success("Configuration saved successfully")

        # Create rows of columns
        row1 = st.columns(6)
        row2 = st.columns(6)
        row3 = st.columns(6)
        row4 = st.columns(6)
        row5 = st.columns(6)
        row6 = st.columns(6)
        # row7 = st.columns(6)
        # row8 = st.columns(6)

        # Combine all columns into a single list
        all_columns = row1 + row2 + row3 + row4 + row5 + row6 #+ row7 + row8

        # Generate fields dynamically from the JSON config
        fields = generate_fields_from_config(engine_config)

        changes_detected = False # Track if any changes are made

        # Dynamically populate the grid with input fields
        for index, (label, key) in enumerate(fields):
            # st.write(f"{fields}")
            col = all_columns[index % len(all_columns)]  # Determine the column to place the input
            with col.container(height=100):
                # Determine the input type based on the key or value
                if key == 'turbo':  # Special handling for the 'turbo' field
                    # Use radio buttons for mutually exclusive selection
                    turbo_option = st.radio(
                        "Turbocharged", 
                        [True, False], 
                        index=0 if engine_config[key] else 1,
                        key=f"{engine_type}_{key}_radio"
                    )

                    # Detect changes
                    if turbo_option != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = turbo_option # Update the 'turbo' field based on radio button selection

                if key == 'rearOil':  # Special handling for the 'rearOil' field
                    # Use radio buttons for mutually exclusive selection
                    rear_oil_option = st.radio(
                        "Rear Oil Pressure", 
                        [True, False], 
                        index=0 if engine_config[key] else 1,
                        key=f"{engine_type}_{key}_radio"
                    )

                    # Detect changes
                    if rear_oil_option != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = rear_oil_option # Update the 'rearOil' field based on radio button selection

                if key == 'frontOil':  # Special handling for the 'frontOil' field
                    # Use radio buttons for mutually exclusive selection
                    front_oil_option = st.radio(
                        "Front Oil Pressure", 
                        [True, False], 
                        index=0 if engine_config[key] else 1,
                        key=f"{engine_type}_{key}_radio"
                    )

                    # Detect changes
                    if front_oil_option != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = front_oil_option # Update the 'frontOil' field based on radio button selection

                if key == 'meteredFuel':  # Special handling for the 'frontOil' field
                    # Use radio buttons for mutually exclusive selection
                    metered_fuel_option = st.radio(
                        "Metered Fuel Pressure", 
                        [True, False], 
                        index=0 if engine_config[key] else 1,
                        key=f"{engine_type}_{key}_radio"
                    )

                    # Detect changes
                    if metered_fuel_option != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = metered_fuel_option # Update the 'frontOil' field based on radio button selection

                if key == 'unmeteredFuel':  # Special handling for the 'frontOil' field
                    # Use radio buttons for mutually exclusive selection
                    unmetered_fuel_option = st.radio(
                        "Unmetered Fuel Pressure", 
                        [True, False], 
                        index=0 if engine_config[key] else 1,
                        key=f"{engine_type}_{key}_radio"
                    )

                    # Detect changes
                    if unmetered_fuel_option != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = unmetered_fuel_option # Update the 'frontOil' field based on radio button selection
                    
                    # config[key] = turbo_option # "Turbo"
                
                elif key == 'cylinders':  # Special handling for the 'cylinders' field
                    # Use radio buttons for selecting cylinder count
                    cylinders_option = st.radio(
                        "Number of Cylinders",
                        [4, 6],  # Only allow selection between 4 and 6 cylinders
                        index=0 if engine_config[key] == 4 else 1,
                        key=f"{engine_type}_{key}_radio"
                    )

                    # Detect changes
                    if cylinders_option != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = cylinders_option # Update the 'cylinders' field based on radio button selection
                    
                    
                    # config[key] = cylinders_option

                elif isinstance(engine_config[key], (int, float)):  # Handle numerical fields with number_input
                    
                    new_value = st.number_input(label, value=engine_config[key], key=f"{engine_type}_{key}")

                    # Detect changes
                    if new_value != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = new_value

                elif isinstance(engine_config[key], (str)): # Handle text fields with text_input
                    
                    new_value = st.text_input(label, value=engine_config[key], key=f"{engine_type}_{key}")

                    # Detect changes
                    if new_value != engine_config[key]:
                        changes_detected = True
                        engine_config[key] = new_value

                else:
                    # Add more field types if needed
                    pass

        if st.button(f"Save {engine_type} Configuration", key=f"btn_save_{engine_type}", type="primary", use_container_width=True):
            save_engine_config(engine_config, engine_type)
            
            # st.write(st.session_state.get('minMP'))
            engine_config_saved = st.success(f"{engine_type} Configuration Saved Successfully") 
            time.sleep(2)
            engine_config_saved.empty()                



# @st.fragment()
# def edit_engine_config(engine_type, engine_config):
#     """Display input fields for configuration settings in a grid layout."""

#     display_engine_config_parameters(engine_type, engine_config)

#     # with st.expander(f"Edit {engine_type}"):
#     #     # col1, col2, col3 = st.columns([2.4, 0.8, 2])
#     #     # with col2:
#     #     #     # Save button to save the configuration
#     #     #     if st.button("Save Configuration"):
#     #     #         save_config(config, engine_type)
#     #     #         st.success("Configuration saved successfully")

#     #     # Create rows of columns
#     #     row1 = st.columns(6)
#     #     row2 = st.columns(6)
#     #     row3 = st.columns(6)
#     #     row4 = st.columns(6)
#     #     row5 = st.columns(6)
#     #     row6 = st.columns(6)
#     #     # row7 = st.columns(6)
#     #     # row8 = st.columns(6)

#     #     # Combine all columns into a single list
#     #     all_columns = row1 + row2 + row3 + row4 + row5 + row6 #+ row7 + row8

#     #     # Generate fields dynamically from the JSON config
#     #     fields = generate_fields_from_config(engine_config)

#     #     changes_detected = False # Track if any changes are made

#     #     # Dynamically populate the grid with input fields
#     #     for index, (label, key) in enumerate(fields):
#     #         # st.write(f"{fields}")
#     #         col = all_columns[index % len(all_columns)]  # Determine the column to place the input
#     #         with col.container(height=100):
#     #             # Determine the input type based on the key or value
#     #             if key == 'turbo':  # Special handling for the 'turbo' field
#     #                 # Use radio buttons for mutually exclusive selection
#     #                 turbo_option = st.radio(
#     #                     "Turbocharged", 
#     #                     [True, False], 
#     #                     index=0 if engine_config[key] else 1,
#     #                     key=f"{engine_type}_{key}_radio"
#     #                 )

#     #                 # Detect changes
#     #                 if turbo_option != engine_config[key]:
#     #                     changes_detected = True
#     #                     engine_config[key] = turbo_option # Update the 'turbo' field based on radio button selection
                    
                    
#     #                 # config[key] = turbo_option # "Turbo"
#     #             elif key == 'cylinders':  # Special handling for the 'cylinders' field
#     #                  # Use radio buttons for selecting cylinder count
#     #                 cylinders_option = st.radio(
#     #                     "Number of Cylinders",
#     #                     [4, 6],  # Only allow selection between 4 and 6 cylinders
#     #                     index=0 if engine_config[key] == 4 else 1,
#     #                     key=f"{engine_type}_{key}_radio"
#     #                 )

#     #                 # Detect changes
#     #                 if cylinders_option != engine_config[key]:
#     #                     changes_detected = True
#     #                     engine_config[key] = cylinders_option # Update the 'cylinders' field based on radio button selection
                    
                    
#     #                 # config[key] = cylinders_option

#     #             elif isinstance(engine_config[key], (int, float)):  # Handle numerical fields with number_input
                    
#     #                 new_value = st.number_input(label, value=engine_config[key], key=f"{engine_type}_{key}")

#     #                 # Detect changes
#     #                 if new_value != engine_config[key]:
#     #                     changes_detected = True
#     #                     engine_config[key] = new_value

#     #             elif isinstance(engine_config[key], (str)): # Handle text fields with text_input
                    
#     #                 new_value = st.text_input(label, value=engine_config[key], key=f"{engine_type}_{key}")

#     #                 # Detect changes
#     #                 if new_value != engine_config[key]:
#     #                     changes_detected = True
#     #                     engine_config[key] = new_value

#     #             else:
#     #                 # Add more field types if needed
#     #                 pass

#     # If changes are detected, remind the user to save
#     # if changes_detected:
#     #     st.toast("Changes made to the configuration! Don't forget to review & save")

#     # if st.button("Save Engine Configuration", type="primary", use_container_width=True):
#     #         save_engine_config(engine_config, engine_type)
            
#     #         # st.write(st.session_state.get('minMP'))
#     #         engine_config_saved = st.success("Configuration saved successfully") 
#     #         time.sleep(2)
#     #         engine_config_saved.empty()


def edit_propeller_config():
    """Display expander to edit propeller json file"""

    st.markdown("### Add New Propeller Type")

    with st.popover("", use_container_width=True):
        new_prop_name = st.text_input("New Propeller Name")
        target_blade_count = st.radio("Enter Number of Blades", [2, 3, 4], horizontal=True)

        if st.button("Save New Propeller", type="primary",use_container_width=True):
            if new_prop_name:
                target_key = str(target_blade_count)
            
            # Update session state
            if new_prop_name not in st.session_state.prop_catalog[target_key]:
                st.session_state.prop_catalog[target_key].append(new_prop_name)

                # Update the JSON file
                save_propeller_config(st.session_state.prop_catalog)

                prop_save_success = st.success(f"'{new_prop_name}' saved to config file")
                time.sleep(2)
                prop_save_success.empty()
                st.rerun()
            else:
                st.warning("This model already exists in the catalog.")
        else:
            st.info("Please enter a name before saving")

def add_engine_to_engine_config(engine_config):
    """Display expander to add engine to json file"""

    st.markdown("### Add New Engine Configuration")

    with st.popover("",use_container_width=True):
        # Get new engine name
        new_engine_make = st.selectbox("Engine Manufacture", options=["Lycoming", "Continental", "TCM"])
        if not new_engine_make:
            st.info("Please select a manufacturer to begin configuration")
            return
        new_engine_model = st.text_input("Enter Engine Model", placeholder="e.g IO-240-B")
        if not new_engine_model:
            st.info("Please enter a model name to continue configuration")
            return

        new_engine = new_engine_make + " " + new_engine_model

        if new_engine in engine_config:
            st.warning(f"An engine named '{new_engine}' already exists!")

        # Define a default template to ensure the new engine has all the necessary keys
        if "template" not in st.session_state:
            # Assuming 'engine_config' is not empty use configurable parameters as template
            configurable_params_key = list(engine_config.keys())[1]
            st.session_state.template = engine_config[configurable_params_key].copy()
            # Reset values to defaults
            for key in st.session_state.template:
                if isinstance(st.session_state.template[key], (int, float)):
                    st.session_state.template[key] = 0
                elif isinstance(st.session_state.template[key], bool):
                    st.session_state.template[key] = False
                else:
                    st.session_state.template[key] = ""

        # Reuse edit_engine_config display logic
        display_engine_config_parameters(new_engine, st.session_state.template)

        # Save new engine config
        # if st.button("Create and Save New Engine", type="primary", use_container_width=True):

        #     save_engine_config(st.session_state.template, new_engine)

        #     # Cleanup
        #     del st.session_state.template
        #     new_engine_success = st.success(f"Successfully added {new_engine} to configuration")
        #     time.sleep(2)
        #     new_engine_success.empty()
        #     st.rerun()

def display_adjustable_prop_form(prop_name):
    """Display data editor/inputs for selected 3 Blade Adjustable Prop"""

    st.markdown("### 3 Blade Adjustable Propeller Settings")
    form_info = st.info("Add a new row at the bottom of the table for each new entry")
    time.sleep(2)
    form_info.empty()

    adjustable_logs = load_adjustable_config()
    # st.write(adjustable_logs)

    raw_data = adjustable_logs.get(prop_name, [])

    # Initialize with specific column names to ensure they always exist
    # default_rows = ["Work Order", "Engine Model", "Horsepower", "Date", "Length"]
    
    if not raw_data:
        df = pd.DataFrame([{
            "Work Order": "",
            "Engine Model": "", 
            "Horsepower": 0,
            "Date": date.today(), 
            "Length": 0.0
        }])
    else:
        df = pd.DataFrame(raw_data)
        # Ensure 'Date' is actually datetime object for the Ui picker to work
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.date


    # with st.popover("", use_container_width=True):
    edited_df = st.data_editor(
        df, 
        column_config={
            "Work Order": st.column_config.TextColumn("Work Order", width="medium"),
            "Engine Model": st.column_config.TextColumn("Engine Model"),
            "Horsepower": st.column_config.NumberColumn("Horsepower", min_value=0),
            "Date": st.column_config.DateColumn("Date",
                                                min_value=date(2001, 1, 1),
                                                max_value=date(2100, 1, 1),
                                                format="YYYY-MM-DD",
                                                required=True),
            "Length": st.column_config.NumberColumn("Length (inches)")
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=f"setting_editor_{prop_name}"
    )

    
    if st.button(f"Update Log for {prop_name}", type="primary", use_container_width=True):
        # Convert date objects to strings for JSON compatibility
        # Preventing errors when trying to save 'datetime.date' objects to JSON
        final_df = edited_df.copy()
        
        # Safe data conversion: Only conver if the column exists and has data
        if "Date" in final_df.columns:
            # Use pd.to_datetime to handle potential None/Null values
            final_df["Date"] = final_df["Date"].astype(str)
    
        # Save back to main dictionary
        adjustable_logs[prop_name] = final_df.to_dict('records')
        save_adjustable_config(adjustable_logs)
        adjustable_save_success = st.success("Done")
        st.session_state.prop_log_finalized = True
        time.sleep(2)
        adjustable_save_success.empty()
        st.rerun()
        
def main():

    # CSS for styling tiles (buttons)
    st.markdown(
        """
        <style>
        .tile-button {
            background-color: #f0f2f6;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            width: 200px;
            margin: 10px;
            cursor: pointer;
            display: inline-block;
            font-size: 16px;
        }
        .tile-button:hover {
            background-color: #e0e4e8;
        }
        .tile-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("Engine and Propeller Selection/Editing")

    # Load engine configuration
    engine_config = load_engine_config()
    if 'prop_catalog' not in st.session_state:
        st.session_state.prop_catalog = load_propeller_config()

    # Initialize button tracking flags
    if "prop_log_finalized" not in st.session_state:
        st.session_state.prop_log_finalized = False
    
    st.divider()
    st.markdown("### Engine and Propeller Selection")
    
    # Dropdown to select an engine type
    # engine_type = st.selectbox("Engine Type", list(engine_config.keys()))
    # st.session_state.selected_engine = engine_type  # Store selected engine in session state
    # st.session_state.get("selected_engine")

    column1, column2, column3, column4 = st.columns(4)

    with column1:
         # Dropdown to select an engine type
        engine_type = st.selectbox("Engine Type", list(engine_config.keys()))
        st.session_state.selected_engine = engine_type  # Store selected engine in session state
        st.session_state.get("selected_engine")
    with column2:
        # Dropdown to select number of propeller blades
        num_blades = st.selectbox("Number of Blades", options=[2, 3, 4])
        str_blades = str(num_blades)
        st.session_state.selected_blades = num_blades
        st.session_state.get("selected_blades")
    with column3:
        # Dropdown to select maximum rpm
        max_rpm = st.selectbox("Maximum RPM", options=[2400, 2700])
        st.session_state.selected_rpm = max_rpm
        st.session_state.get("selected_rpm")
    with column4:
       # Filter based on persistent data
        available_options = st.session_state.prop_catalog.get(str_blades, [])
        # Dropdown to select propeller type
        prop_type = st.selectbox("Propeller Type", options=available_options)
        st.session_state.selected_prop = prop_type
        st.session_state.get("selected_prop")
    
    # Reset flag is the prop has changed
    if "last_prop" not in st.session_state:
        st.session_state.last_prop = prop_type
    if prop_type != st.session_state.last_prop:
        st.session_state.prop_log_finalized = False
        st.session_state.last_prop = prop_type


    # Display Logic
    is_3_blade = (str_blades == "3")
    if is_3_blade and prop_type:
        display_adjustable_prop_form(prop_type)
    
    # Button visibility logic
    # Show "Confirm" only if:
    # 1. It's NOT a 3-blade prop
    # OR
    # 2. It's a 3 blade prop and the user clicked the 'Update Log' button
    show_confirm = not is_3_blade or st.session_state.prop_log_finalized
        
    # Load engine configuration based on selected type
    selected_config = engine_config[engine_type]
    if show_confirm:
        st.divider()
        # Confirm button for selecting an engine type
        if st.button(f"Confirm", type = "primary", use_container_width=True):
            # st.session_state.selected_engine = engine_type  # Store selected engine in session state
            
            st.success(f"{engine_type} confirmed")
            # Navigate to the dashboard page
            
            # st.write(st.session_state.get('minMP'))
            initialize_engine_parameters(engine_type, engine_config)
            st.switch_page(dashboard_page_path)
    else:
        hidden_btn_warning = st.warning("Please save the adjustable propeller log to enable the Confirm button")

    
    # prop_type = st.selectbox("Prop Type", ("4 Blade (Wooden)", "2 Blade (Yellow Tipped)"))
    # st.session_state.selected_prop = prop_type
    # st.session_state.get("selected_prop")

    

    # with col4:
        # Save button to save the configuration
        # if st.button("Save Configuration"):
        #     save_config(config, engine_type)
            
        #     # st.write(st.session_state.get('minMP'))
        #     st.success("Configuration saved successfully")    
    
# Add new propeller
   
    st.divider() 
    st.markdown("### Add or Edit Engine and Propeller Parameters")

    # Password input for other engine types
    password = st.text_input("Enter Password for Editing (Press Enter Key When Done)", type="password")
    if password:
        if authenticate(password, engine_type):
            correct_pass = st.success("Authenticated Successfully!")
            time.sleep(2)
            correct_pass.empty()
            st.divider()
            edit_propeller_config()
            st.divider()
            display_engine_config_parameters(engine_type, selected_config)
            st.divider()
            add_engine_to_engine_config(engine_config)
        else:
            wrong_pass = st.error("Incorrect Password. Please try again.")
            time.sleep(2)
            wrong_pass.empty()

    # Display configuration inputs based on engine type
    # if engine_type == "Configurable Parameters":
    #     st.divider()
    #     edit_engine_config(engine_type, config)
    #     st.divider()
    #     edit_propeller_config()
    # elif engine_type == "Data Only":
    #     st.divider()
    #     edit_propeller_config()
    #     return
    # # elif engine_type == "  ":
    # #     return
    # else:
    #     # Password input for other engine types
    #     password = st.text_input("Enter Password for Editing (Press Enter Key When Done)", type="password")
    #     if password:
    #         if authenticate(password, engine_type):
    #             st.success("Authenticated Successfully!")
    #             st.divider()
    #             edit_engine_config(engine_type, config)
    #             st.divider()
    #             edit_propeller_config()
    #         else:
    #             st.error("Incorrect Password. Please try again.")

    # if st.button("Save Configuration"):
    #         save_engine_config(config, engine_type)
            
    #         # st.write(st.session_state.get('minMP'))
    #         st.success("Configuration saved successfully") 
 
    

# Call main() only if this script is run directly
if __name__ == "__main__":
    main()

