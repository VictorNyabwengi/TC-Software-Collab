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
import requests
import math

# st.set_page_config(layout="wide", page_title="Select Engine Screen", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")
st.set_page_config(layout="wide",
                   page_title="Engine Selection", 
                   page_icon=st.session_state.get("page_icon", ":small_airplane:"), 
                   initial_sidebar_state="collapsed")

# Pages File Paths
main_page_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\st_main.py"
dashboard_page_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\pages\st_dashboard.py"

# JSON File Paths
engine_json_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\Engine Configuration.json"
propeller_json_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\Propeller Config.json"
adjustable_json_path = r"C:\Users\KieranCalder\Code\AerotecTestCell\3 Blade Adjustable Propeller Logs.json"

# sys.path.insert(0, r"C:\Users\KieranCalder\Code\AerotecTestCell")

# Ensure the user has selected an engine
if 'logo' not in st.session_state: #or st.session_state.selected_engine is None:
    st.warning("Initialization incomplete. Redirecting to main page...")
    time.sleep(1)
    st.switch_page(main_page_path)  # Redirect back to engine selection

elif 'page_icon' not in st.session_state:
    st.warning("Initialization incomplete. Redirecting to main page...")
    time.sleep(1)
    st.switch_page(main_page_path)  # Redirect back to engine selection


# Sensor min/max reference map
sensor_reference = {
    "TIT": {"abs_min": 0, "abs_max": 1650, "unit": "°F", "is_float": False},
    "CHT": {"abs_min": 0, "abs_max": 525, "unit": "°F", "is_float": False},
    "EGT": {"abs_min": 0, "abs_max": 1650, "unit": "°F", "is_float": False},
    "OilTemp": {"abs_min": 0, "abs_max": 120, "unit": "°C", "is_float": False},
    "IAT": {"abs_min": -40, "abs_max": 40, "unit": "°C", "is_float": False},
    "CDT": {"abs_min": 0, "abs_max": 200, "unit": "°F", "is_float": False},
    "HP": {"abs_min": 0, "abs_max": 200, "unit": "n/a", "is_float": False},
    "RPM": {"abs_min": 0, "abs_max": 2800, "unit": "n/a", "is_float": False},
    "MP": {"abs_min": 0, "abs_max": 45, "unit": "inHg", "is_float": True},
    "MeteredFuelPressure": {"abs_min": 0, "abs_max": 30, "unit": "PSI", "is_float": True},
    "UnmeteredFuelPressure": {"abs_min": 0, "abs_max": 60, "unit": "PSI", "is_float": True},
    "BoostPressure": {"abs_min": 0, "abs_max": 12, "unit": "PSI", "is_float": True},
    "RearOilPressure": {"abs_min": 0, "abs_max": 120, "unit": "PSI", "is_float": False},
    "FrontOilPressure": {"abs_min": 0, "abs_max": 120, "unit": "PSI", "is_float": False},
    "MagDrop": {"abs_min": 0, "abs_max": 300, "unit": "n/a", "is_float": False},
    "FuelFlow": {"abs_min": 0, "abs_max": 25, "unit": "GPH", "is_float": True}
}


# st_autorefresh(3000, key="select_screen_refresh")  # Refresh at a specified interval

# st.set_page_config(layout="wide", page_title="Select Engine Screen", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")
st.logo(st.session_state.logo)

def get_beaver_bank_weather():
    # global time_step
    """
    Fetches the current temperature for Beaver Bank, NS.
    Returns the temperature as a string (Celsius).
    """
    # We use 'format=j1' to get the response in a searchable JSON format
    url = "https://wttr.in/Beaver+Bank,Nova+Scotia?format=j1"

    # time_step = time.time()
    
    try:
        response = requests.get(url)
        # Raise an exception if the request failed (e.g., 404 or 500 error)
        response.raise_for_status()
        
        data = response.json()

        
        # Accessing the current temperature from the JSON structure
        # wttr.in puts the current stats in the 'current_condition' list
        temp_c = data['current_condition'][0]['temp_C']
        
        return temp_c

    except Exception as e:
        return f"Error: {e}"

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
    """Generate fields dynamically from the configuration keys.
       Filters out nominal/high values and pairs min/max keys.    
    """
    fields = []
    for key in config.keys():
        # Hide nominal and high values form the operator
        # if "nominal" in key.lower() or "high" in key.lower():
        #     continue
        label = generate_label_from_key(key)
        fields.append((label, key))
    return fields

# def generate_fields_from_config(config):
#     """Generate fields dynamically from the configuration keys."""
#     fields = []
#     for key in config.keys():
#         label = generate_label_from_key(key)  # Generate label dynamically
#         fields.append((label, key))  # Append as (label, key) tuple
#     return fields




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

# def apply_threshold_logic(config):
#     """
#     Background calculations: Find min/max pairs and fills in nominal/high.
#     Standard: Norminal = 50% of range, High = 80% of range
#     """
#     # # Find all unique sensor bases (e.g. if 'minOilP' exists, base is 'OilP')
#     # bases = set()
#     # for key in config.keys():
#     #     if key in config.keys():
#     #         bases.add(key[3:])

#     # for base in bases:
#     #     min_key = f"min{base}"
#     #     nom_key = f"nominal{base}"
#     #     high_key = f"high{base}"
#     #     max_key = f"max{base}"

#     #     if min_key in config and max_key in config:
#     #         val_min = config[min_key]
#     #         val_max = config[max_key]

#     #         # Calculate standard spreads
#     #         config[nom_key] = round(val_min + (val_max-val_min) * 0.5, 2)
#     #         config[high_key] = round(val_min + (val_max - val_min) * 0.8, 2)

#     # return config

#     # Find bases like 'RPM', 'MP'
#     bases = [k[3:] for k in config.keys() if k.startswith("min") and isinstance(config[k], (int, float))]

#     for b in bases:
#         mn_key, mx_key = f"min{b}", f"max{b}"
#         if mn_key in config and mx_key in config:
#             mn, mx = config[mn_key], config[mx_key]
#             config[f"nominal{b}"] = round(mn + (mx - mn) * 0.5)
#             config[f"high{b}"] = round(mn + (mx - mn) * 0.8)

#     return config

@st.fragment
def render_threshold_fragement(base, engine_type, engine_config, sensor_ref):
    with st.container(border=True):
        # Fetch reference data
        ref = sensor_reference.get(base, {"abs_min": 0, "abs_max": 100, "unit": "", "is_float": False})
        is_float = ref["is_float"]
        step = 0.1 if is_float else 1.0
        fmt = ".1f" if is_float else ".0f"
        slider_fmt = "%.1f" if is_float else "%.0f"
        abs_min = float(ref["abs_min"])
        abs_max = float(ref["abs_max"])
        unit = ref["unit"]
        span = abs_max - abs_min
        
        label = generate_label_from_key(base)
        st.markdown(f"**{label},  {unit}**")


        # Current values from config
        v_min = float(engine_config.get(f"min{base}", 0))
        v_nom = float(engine_config.get(f"nominal{base}", 0))
        v_high = float(engine_config.get(f"high{base}", 0))
        v_max = float(engine_config.get(f"max{base}", 0))

        # If all values are 0, apply smart defaults to avoid error
        if v_min == v_nom == v_high == v_max:
            v_min = abs_min
            v_max = abs_max
            v_nom = abs_min + (span * 0.7)
            v_high = abs_min + (span * 0.85)

        # Logic to round up to the nearest 10's
        if abs_max > 120:
        # Function to ceiling-round to nearest 10
            def ceil_10(n):
                return math.ceil(n / 10.0) * 10

            step = 10 # For max values > 10 we are snapping to 10s, the slider step should be 10
            fmt = ".0f"
            slider_fmt = "%.0f"
            
            abs_min = int(ceil_10(abs_min))
            abs_max = int(ceil_10(abs_max))
            v_min = int(ceil_10(v_min),)
            v_nom = int(ceil_10(v_nom))
            v_high = int(ceil_10(v_high))
            v_max = int(ceil_10(v_max))
        else:
            # Low scale: strictly enforce ALL slider parameters as floats
            is_float = ref.get("is_float", False)
            step = 0.1 if is_float else 1.0
            fmt = ".1f" if is_float else ".0f"
            slider_fmt = "%.1f" if is_float else "%.0f"
            
            abs_min = float(abs_min)
            abs_max = float(abs_max)
            v_min = float(v_min)
            v_nom = float(v_nom)
            v_high = float(v_high)
            v_max = float(v_max)

        # Define the total scale (e.g. 1.5x max for headroom)
        total_max = int(v_max * 1.5) if v_max > 0 else 100

        col1, col2 = st.columns(2)
        with col1:
            # Lower Range: Min -> Nominal (Upper Limit is current High)
            lower_range = st.slider(
                        "Min -> Nom",
                        abs_min, v_high, (v_min, v_nom),
                        step=step,
                        format=slider_fmt,
                        key=f"Low_{engine_type}_{base}"
            )
            

        with col2:
            # Lower Range: High -> Maximum (Lower Limit is current Nominal)
            higher_range = st.slider(
                        "High -> Max",
                        v_nom, abs_max, (v_high, v_max),
                        step=step,
                        format=slider_fmt,
                        key=f"High_{engine_type}_{base}"
            )
            
        engine_config[f"min{base}"], engine_config[f"nominal{base}"] = lower_range
        engine_config[f"high{base}"], engine_config[f"max{base}"] = higher_range
        # This makes the bar physically shorter if the Max is lower than Total Max
        
        # --- FIX: Calculate visual layout parameters using the UPDATED values ---
        up_min = float(engine_config[f"min{base}"])
        up_nom = float(engine_config[f"nominal{base}"])
        up_high = float(engine_config[f"high{base}"])
        up_max = float(engine_config[f"max{base}"])
        
        # container_width = (engine_config[f"max{base}"] / total_max) * 100
        container_width = (up_max / total_max) * 100

        # --- 2. Recalculate percentages relative to the ACTUAL MAX (Max = 100%) ---
        # We use max(..., 1) to avoid division by zero
        actual_max = max(engine_config[f"max{base}"], 1)

        def get_pct(val):
            return min(max((val - abs_min) / span * 100, 0), 100)


        p_min = get_pct(up_min)
        p_nom = get_pct(up_nom)
        p_high = get_pct(up_high)
        p_max = get_pct(up_max)
        
        
        # If base is EGT use blue else use green
        is_egt = "EGT" in base
        # color_picker = "#007bff" if "EGT" in base else "#28a745"

        # Oil pressure exception
        is_oil_p = "OilPressure" in base
        
        if is_oil_p:
            grad = f"""
                #dc3545 0%, #dc3545 {p_nom}%, 
                #ffc107 {p_nom}%, #ffc107 {p_high}%, 
                #28a745 {p_high}%, #28a745 {p_max}%,
                #dc3545 {p_max}%, #dc3545 100%
            """
        # Note: If you want the bar to turn Red again immediately at MAX:
        # Change the Green end from 100% to {p_max}% and add #dc3545 from {p_max}% to 100%
        else:
            # Standard Gradient (Green or Blue based on CHT)
            # color_picker = "#007bff" if is_egt else "#28a745"
            color_picker = "#28a745" if is_egt else "#28a745"
            grad = f"""
                #dc3545 0%, #dc3545 {p_min}%, 
                {color_picker} {p_min}%, {color_picker} {p_nom}%, 
                #ffc107 {p_nom}%, #ffc107 {p_high}%, 
                #dc3545 {p_high}%, #dc3545 100%
            """
        
        # --- 3. Determine Labels ---
        # We'll use a helper to swap labels for Oil Pressure
        label_min = engine_config[f"min{base}"]
        label_nom = engine_config[f"nominal{base}"]
        label_high = engine_config[f"high{base}"]
        label_max = engine_config[f"max{base}"]


        if is_oil_p:
            # OIL PRESSURE SPECIFIC MARKDOWN
            progress_html = f"""
                <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
                    <div style="width: {container_width}%; min-width: 200px; height: 30px; border-radius: 4px; border: 1px solid #ddd; background: linear-gradient(to right, {grad}); margin: 10px 0;"></div>
                    <div style="position: relative; width: {container_width}%; min-width: 200px; height: 35px; font-family: monospace; font-size: 0.75rem; line-height: 1.2;">
                        <span style="position: absolute; left: 0;"></span>
                        <span style="position: absolute; left: {p_nom}%; transform: translateX(-50%); color: #dc3545; text-align: center;">{label_nom:{fmt}}<br>IDLE</span>
                        <span style="position: absolute; left: {p_high}%; transform: translateX(-50%); color: #28a745; text-align: center;">{label_high:{fmt}}<br>SPEC MIN</span>
                        <span style="position: absolute; left: {p_max}%; transform: translateX(-50%); color: #dc3545; text-align: center;">{label_max:{fmt}}<br>SPEC MAX</span>
                    </div>
                </div>
            """
        else:
            # STANDARD MARKDOWN (Your original code)
            progress_html = f"""
                <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
                    <div style="width: {container_width}%; min-width: 200px; height: 30px; border-radius: 4px; border: 1px solid #ddd; background: linear-gradient(to right, {grad}); margin: 10px 0;"></div>
                    <div style="position: relative; width: {container_width}%; min-width: 200px; height: 20px; font-family: monospace; font-size: 0.75rem;">
                        <span style="position: absolute; left: 0;"></span>
                        <span style="position: absolute; left: {p_min}%; transform: translateX(-50%); color: #666;">{label_min:{fmt}}</span>
                        <span style="position: absolute; left: {p_nom}%; transform: translateX(-50%); color: #28a745;">{label_nom:{fmt}}</span>
                        <span style="position: absolute; left: {p_high}%; transform: translateX(-50%); color: #ffc107;">{label_high:{fmt}}</span>
                        <span style="position: absolute; left: 100%; transform: translateX(-100%); color: #dc3545;">{label_max:{fmt}}</span>
                    </div>
                </div>
            """

        # --- 3. Render the chosen version ---
        st.markdown(progress_html, unsafe_allow_html=True)


def display_engine_config_parameters(engine_type, engine_config):
    """Display and edit engine configuration with automated background logic."""
    st.markdown(f"### Edit {engine_type} Parameters")

    with st.expander(""):
        # Create form block to prevent screen darkening during inputs
        # Key the form to an engine_type to avoid key errors
        # with st.form(key=f"engine_config_form_{engine_type}", clear_on_submit=False):

        # Categorize and filter out background values first
        # visible_keys = [k for k in engine_config.keys() if not any(x in k.lower() for x in ["nominal", "high"])]
        visible_keys = list(engine_config.keys())
        system_controls = [k for k in visible_keys if isinstance(engine_config[k], bool) or k == 'cylinders']

        # Find numeric bases
        range_bases = []
        for k in visible_keys:
            if k.startswith("min"):
                base = k[3:]
                # Check if the base has the required threshold set for the dual-slider logic
                if all(f"{p}{base}" in engine_config for p in ["min", "nominal", "high", "max"]):
                    range_bases.append(base)
            # if k.startswith("min") and f"max{k[3:]}" in engine_config:
            #     range_bases.append(k[3:])

        # Specs are anything not a boolean and not part of a min/max pair
        range_keys = []
        for b in range_bases:
            range_keys.extend([f"min{b}", f"nominal{b}", f"high{b}", f"max{b}"])
        # range_keys = [f"min{b}" for b in range_bases] + [f"max{b}" for b in range_bases]
        specs = [k for k in visible_keys if k not in system_controls and k not in range_keys]

        # Define dependencies, ensure the strings match JSON keys exactly
        dependencies = {
            "TIT": "turbo", 
            "CDT": "turbo",
            "BoostPressure": "turbo",
            "IAT": "inletAirTemp",
            "RearOilPressure": "rearOilPressure",
            "FrontOilPressure": "frontOilPressure",
            "MeteredFuelPressure": "meteredFuelPressure",
            "UnmeteredFuelPressure": "unmeteredFuelPressure"
        }

        # Render System Switches
        st.divider()
        st.subheader("System Configuration")
        if system_controls:
            cols = st.columns(3)
            for i, key in enumerate(system_controls):
                with cols[i % 3]:
                    label = generate_label_from_key(key)
                    # Handle cylinders
                    if key == 'cylinders':
                        engine_config[key] = st.radio(label,
                                                    [4, 6],
                                                    index=0 if engine_config[key] == 4 else 1,
                                                    key=f"rad_{engine_type}_{key}"
                                                    )
                        # Standard Boolean Switchs
                    else:
                        engine_config[key] = st.radio(label, 
                                                    [True, False], 
                                                    index=0 if engine_config[key] else 1,
                                                    key=f"rad_{engine_type}_{key}"
                                                    )
        
        # Render Range Sliders from Grouped Min/Max
        st.divider()
        st.subheader("Thresholds (Min - Max)")

        # Filter range_bases based on dependencies
        active_range_bases = []
        for base in range_bases:
            # If the base is in our dependency map, check the boolean value
            if base in dependencies:
                required_toggle = dependencies[base]
                if engine_config.get(required_toggle, False):
                    active_range_bases.append(base)
            else:
                # If no dependency is defined show it by default
                active_range_bases.append(base)

        if active_range_bases:
            r_cols = st.columns(3)
            # st.write(active_range_bases)
            # We process active_range_bases one by one to give room for the visual bar
            # for base in active_range_bases:
            for i, base in enumerate(active_range_bases):
                with r_cols[i % 3]:
                    render_threshold_fragement(base, engine_type, engine_config, sensor_reference)

        # Render Engine Specs
        st.divider()
        st.subheader("Engine Spec Values")
        if specs:
            sp_cols = st.columns(3)
            for i, key in enumerate(specs):
                with sp_cols[i % 3]:
                    label = generate_label_from_key(key)
                    val = engine_config[key]

                    # if key == 'cylinders':
                    #     engine_config[key] = st.selectbox(label,
                    #                                     [4, 6],
                    #                                     index=0 if val == 4 else 1, 
                    #                                     key=f"sel_{key}")
                    if isinstance(val, (int, float)):
                        engine_config[key] = st.number_input(label, 
                                                            value=float(val), 
                                                            key=f"num_{engine_type}_{key}")
                    else:
                        engine_config[key] = st.text_input(label, 
                                                        value=str(val), 
                                                        key=f"txt_{engine_type}_{key}")
                        
        
        st.markdown("---")
        submit_btn = st.button(
            label=f"Save {engine_type} Configuration",
            type="primary",
            use_container_width=True
        )
        if submit_btn:
            # updated_config = apply_threshold_logic(engine_config)

            save_engine_config(engine_config, engine_type)
            engine_config_saved = st.success(f"Configuration for {engine_type} updated. Nominal and High thresholds auto-calculated")
            time.sleep(1.5)
            # engine_config_saved.empty()
            st.rerun()



# def display_engine_config_parameters(engine_type, engine_config):
#     """Display and edit engine configuration with automated background logic."""
#     st.markdown(f"### Edit {engine_type} Parameters")

#     with st.expander("", expanded=True):
#         visible_keys = list(engine_config.keys())
#         system_controls = [k for k in visible_keys if isinstance(engine_config[k], bool) or k == 'cylinders']

#         # Find numeric bases
#         range_bases = []
#         for k in visible_keys:
#             if k.startswith("min"):
#                 base = k[3:]
#                 if all(f"{p}{base}" in engine_config for p in ["min", "nominal", "high", "max"]):
#                     range_bases.append(base)

#         range_keys = []
#         for b in range_bases:
#             range_keys.extend([f"min{b}", f"nominal{b}", f"high{b}", f"max{b}"])
#         specs = [k for k in visible_keys if k not in system_controls and k not in range_keys]

#         dependencies = {
#             "TIT": "turbo", 
#             "CDT": "turbo",
#             "BoostPressure": "turbo",
#             "IAT": "inletAirTemp",
#             "RearOilPressure": "rearOilPressure",
#             "FrontOilPressure": "frontOilPressure",
#             "MeteredFuelPressure": "meteredFuelPressure",
#             "UnmeteredFuelPressure": "unmeteredFuelPressure"
#         }

#         # --- Render System Switches ---
#         st.divider()
#         st.subheader("System Configuration")
#         if system_controls:
#             cols = st.columns(3)
#             for i, key in enumerate(system_controls):
#                 with cols[i % 3]:
#                     label = generate_label_from_key(key)
#                     if key == 'cylinders':
#                         engine_config[key] = st.radio(
#                             label, [4, 6],
#                             index=0 if engine_config[key] == 4 else 1,
#                             key=f"rad_{engine_type}_{key}"
#                         )
#                     else:
#                         engine_config[key] = st.radio(
#                             label, [True, False], 
#                             index=0 if engine_config[key] else 1,
#                             key=f"rad_{engine_type}_{key}"
#                         )
        
#         # --- Render Range Sliders and Visual Bars ---
#         st.divider()
#         st.subheader("Thresholds (Min - Max)")

#         active_range_bases = []
#         for base in range_bases:
#             if base in dependencies:
#                 required_toggle = dependencies[base]
#                 if engine_config.get(required_toggle, False):
#                     active_range_bases.append(base)
#             else:
#                 active_range_bases.append(base)

#         if active_range_bases:
#             r_cols = st.columns(3)
#             for i, base in enumerate(active_range_bases):
#                 with r_cols[i % 3]:
#                     with st.container(border=True):
#                         # Fetch reference data
#                         ref = sensor_reference.get(base, {"abs_min": 0, "abs_max": 100, "unit": "", "is_float": False})
#                         abs_min = float(ref["abs_min"])
#                         abs_max = float(ref["abs_max"])
#                         unit = ref["unit"]
#                         span = abs_max - abs_min
                        
#                         label = generate_label_from_key(base)
#                         st.markdown(f"**{label}, {unit}**")

#                         # Pull current values
#                         v_min = float(engine_config.get(f"min{base}", 0))
#                         v_nom = float(engine_config.get(f"nominal{base}", 0))
#                         v_high = float(engine_config.get(f"high{base}", 0))
#                         v_max = float(engine_config.get(f"max{base}", 0))

#                         if v_min == v_nom == v_high == v_max:
#                             v_min, v_max = abs_min, abs_max
#                             v_nom = abs_min + (span * 0.7)
#                             v_high = abs_min + (span * 0.85)

#                         # --- NEW SMART ROUNDING LOGIC FOR HIGH VALUES ---
#                         if abs_max > 120:
#         # High scale: strictly enforce ALL slider parameters as integers
#                             step = 1
#                             fmt = ".0f"
#                             slider_fmt = "%.0f"
                            
#                             abs_min = int(abs_min)
#                             abs_max = int(abs_max)
#                             v_min = int(round(v_min),)
#                             v_nom = int(round(v_nom))
#                             v_high = int(round(v_high))
#                             v_max = int(round(v_max))
#                         else:
#                             # Low scale: strictly enforce ALL slider parameters as floats
#                             is_float = ref.get("is_float", False)
#                             step = 0.1 if is_float else 1.0
#                             fmt = ".1f" if is_float else ".0f"
#                             slider_fmt = "%.1f" if is_float else "%.0f"
                            
#                             abs_min = float(abs_min)
#                             abs_max = float(abs_max)
#                             v_min = float(v_min)
#                             v_nom = float(v_nom)
#                             v_high = float(v_high)
#                             v_max = float(v_max)

#                         total_max = int(v_max * 1.5) if v_max > 0 else 100

#                         # Dual Slider Controls
#                         col1, col2 = st.columns(2)
#                         with col1:
#                             lower_range = st.slider(
#                                 "Min -> Nom",
#                                 min_value=abs_min,
#                                 max_value=v_high,
#                                 value=(v_min, v_nom),
#                                 step=step,
#                                 format=slider_fmt,
#                                 key=f"Low_{engine_type}_{base}"
#                             )
#                         with col2:
#                             higher_range = st.slider(
#                                 "High -> Max",
#                                 min_value=v_nom,
#                                 max_value=abs_max,
#                                 value=(v_high, v_max),
#                                 step=step,
#                                 format=slider_fmt,
#                                 key=f"High_{engine_type}_{base}"
#                             )
                            
#                         # Update config dictionary from user movements
#                         engine_config[f"min{base}"], engine_config[f"nominal{base}"] = lower_range
#                         engine_config[f"high{base}"], engine_config[f"max{base}"] = higher_range

#                         # --- FIX: Calculate visual layout parameters using the UPDATED values ---
#                         up_min = float(engine_config[f"min{base}"])
#                         up_nom = float(engine_config[f"nominal{base}"])
#                         up_high = float(engine_config[f"high{base}"])
#                         up_max = float(engine_config[f"max{base}"])

#                         container_width = (up_max / total_max) * 100

#                         def get_pct(val):
#                             return min(max((val - abs_min) / span * 100, 0), 100)

#                         p_min = get_pct(up_min)
#                         p_nom = get_pct(up_nom)
#                         p_high = get_pct(up_high)
#                         p_max = get_pct(up_max)
                        
#                         # Set context flags for specialized color signatures
#                         is_oil_p = "oilpressure" in base.lower()
#                         is_egt = "egt" in base.lower()
#                         is_cht = "cht" in base.lower()

#                         # --- Dynamic Gradient Configurations ---
#                         if is_oil_p:
#                             grad = f"""
#                                 #dc3545 0%, #dc3545 {p_nom}%, 
#                                 #ffc107 {p_nom}%, #ffc107 {p_high}%, 
#                                 #28a745 {p_high}%, #28a745 {p_max}%,
#                                 #dc3545 {p_max}%, #dc3545 100%
#                             """
#                         else:
#                             # Standard fields default to Green; CHT has a cold Blue limit zone
#                             color_picker = "#28a745" #if is_cht else "#28a745"
#                             grad = f"""
#                                 #dc3545 0%, #dc3545 {p_min}%, 
#                                 {color_picker} {p_min}%, {color_picker} {p_nom}%, 
#                                 #ffc107 {p_nom}%, #ffc107 {p_high}%, 
#                                 #dc3545 {p_high}%, #dc3545 100%
#                             """
                        
#                         # --- Dynamic Label Generation ---
#                         if is_oil_p:
#                             progress_html = f"""
#                                 <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
#                                     <div style="width: {container_width}%; min-width: 200px; height: 30px; border-radius: 4px; border: 1px solid #ddd; background: linear-gradient(to right, {grad}); margin: 10px 0;"></div>
#                                     <div style="position: relative; width: {container_width}%; min-width: 200px; height: 35px; font-family: monospace; font-size: 0.75rem; line-height: 1.2;">
#                                         <span style="position: absolute; left: 0;">0</span>
#                                         <span style="position: absolute; left: {p_nom}%; transform: translateX(-50%); color: #dc3545; text-align: center;">{up_nom:{fmt}}<br>IDLE</span>
#                                         <span style="position: absolute; left: {p_high}%; transform: translateX(-50%); color: #28a745; text-align: center;">{up_high:{fmt}}<br>SPEC MIN</span>
#                                         <span style="position: absolute; left: {p_max}%; transform: translateX(-50%); color: #dc3545; text-align: center;">{up_max:{fmt}}<br>SPEC MAX</span>
#                                     </div>
#                                 </div>
#                             """
#                         else:
#                             progress_html = f"""
#                                 <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
#                                     <div style="width: {container_width}%; min-width: 200px; height: 30px; border-radius: 4px; border: 1px solid #ddd; background: linear-gradient(to right, {grad}); margin: 10px 0;"></div>
#                                     <div style="position: relative; width: {container_width}%; min-width: 200px; height: 20px; font-family: monospace; font-size: 0.75rem;">
#                                         <span style="position: absolute; left: 0;">0</span>
#                                         <span style="position: absolute; left: {p_min}%; transform: translateX(-50%); color: #666;">{up_min:{fmt}}</span>
#                                         <span style="position: absolute; left: {p_nom}%; transform: translateX(-50%); color: #28a745;">{up_nom:{fmt}}</span>
#                                         <span style="position: absolute; left: {p_high}%; transform: translateX(-50%); color: #ffc107;">{up_high:{fmt}}</span>
#                                         <span style="position: absolute; left: 100%; transform: translateX(-100%); color: #dc3545;">{up_max:{fmt}}</span>
#                                     </div>
#                                 </div>
#                             """

#                         st.markdown(progress_html, unsafe_allow_html=True)

#         # --- Render Engine Specs ---
#         st.divider()
#         st.subheader("Engine Spec Values")
#         if specs:
#             sp_cols = st.columns(3)
#             for i, key in enumerate(specs):
#                 with sp_cols[i % 3]:
#                     label = generate_label_from_key(key)
#                     val = engine_config[key]

#                     if isinstance(val, (int, float)):
#                         engine_config[key] = st.number_input(
#                             label, value=float(val), 
#                             key=f"num_{engine_type}_{key}"
#                         )
#                     else:
#                         engine_config[key] = st.text_input(
#                             label, value=str(val), 
#                             key=f"txt_{engine_type}_{key}"
#                         )
                        
#         st.markdown("---")
#         if st.button(f"Save {engine_type} Configuration", type="primary", use_container_width=True):
#             save_engine_config(engine_config, engine_type)
#             engine_config_saved = st.success(f"Configuration for {engine_type} updated.")
#             time.sleep(1.5)
#             engine_config_saved.empty()
#             st.rerun()



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
                # Check for boolean fields first
                if isinstance(st.session_state.template[key], bool):
                    st.session_state.template[key] = False
                # Then check for numerical fields
                elif isinstance(st.session_state.template[key], (int, float)):
                    st.session_state.template[key] = 0
                # Strings and other fields last 
                else:
                    st.session_state.template[key] = ""
                # if isinstance(st.session_state.template[key], (int, float)):
                #     st.session_state.template[key] = 0
                # elif isinstance(st.session_state.template[key], bool):
                #     st.session_state.template[key] = False
                # else:
                #     st.session_state.template[key] = ""

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

# def display_adjustable_prop_form(prop_name):
#     """Display data editor/inputs for selected 3 Blade Adjustable Prop"""

#     st.markdown("### 3 Blade Adjustable Propeller Settings")
#     form_info = st.info("Add a new row at the bottom of the table for each new entry")
#     time.sleep(2)
#     form_info.empty()

#     adjustable_logs = load_adjustable_config()
#     # st.write(adjustable_logs)

#     raw_data = adjustable_logs.get(prop_name, [])

#     # Initialize with specific column names to ensure they always exist
#     # default_rows = ["Work Order", "Engine Model", "Horsepower", "Date", "Length"]
    
#     if not raw_data:
#         df = pd.DataFrame([{
#             "Work Order": "",
#             "Engine Model": "", 
#             "Horsepower": 0,
#             "Date": date.today(), 
#             "Length": 0.0
#         }])
#     else:
#         df = pd.DataFrame(raw_data)
#         # Ensure 'Date' is actually datetime object for the Ui picker to work
#         if "Date" in df.columns:
#             df["Date"] = pd.to_datetime(df["Date"]).dt.date


#     # with st.popover("", use_container_width=True):
#     edited_df = st.data_editor(
#         df, 
#         column_config={
#             "Work Order": st.column_config.TextColumn("Work Order", width="medium"),
#             "Engine Model": st.column_config.TextColumn("Engine Model"),
#             "Horsepower": st.column_config.NumberColumn("Horsepower", min_value=0),
#             "Date": st.column_config.DateColumn("Date",
#                                                 min_value=date(2001, 1, 1),
#                                                 max_value=date(2100, 1, 1),
#                                                 format="YYYY-MM-DD",
#                                                 required=True),
#             "Length": st.column_config.NumberColumn("Length (inches)")
#         },
#         num_rows="dynamic",
#         use_container_width=True,
#         hide_index=True,
#         key=f"setting_editor_{prop_name}"
#     )

    
#     if st.button(f"Update Log for {prop_name}", type="primary", use_container_width=True):
#         # Convert date objects to strings for JSON compatibility
#         # Preventing errors when trying to save 'datetime.date' objects to JSON
#         final_df = edited_df.copy()
        
#         # Safe data conversion: Only conver if the column exists and has data
#         if "Date" in final_df.columns:
#             # Use pd.to_datetime to handle potential None/Null values
#             final_df["Date"] = final_df["Date"].astype(str)
    
#         # Save back to main dictionary
#         adjustable_logs[prop_name] = final_df.to_dict('records')
#         save_adjustable_config(adjustable_logs)
#         adjustable_save_success = st.success("Done")
#         st.session_state.prop_log_finalized = True
#         time.sleep(2)
#         adjustable_save_success.empty()
#         st.rerun()



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
    st.markdown("### Test Details")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        customer = st.text_input("Customer Name")
        st.session_state.customer_name = customer
        # st.session_state.get("customer_name")
    with col2:
        sn_number = st.text_input("S/N")
        st.session_state.sn_number = sn_number
        # st.session_state.get("sn_number")
    with col3:
        work_order = st.text_input("Work Order #")
        st.session_state.work_order = work_order
        # st.session_state.get("work_order")
    with col4:
        test_nature = st.text_input("Nature of Test")
        st.session_state.test_nature = test_nature
        # st.session_state.get("test_nature")

    # Check if all text fields have been filled
    details_filled = all([customer, sn_number, work_order, test_nature])
    
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
        # st.session_state.get("selected_engine")
    with column2:
        # Dropdown to select number of propeller blades
        num_blades = st.selectbox("Number of Blades", options=[2, 3, 4])
        str_blades = str(num_blades)
        st.session_state.selected_blades = num_blades
        # st.session_state.get("selected_blades")
    with column3:
        # Dropdown to select maximum rpm
        max_rpm = st.selectbox("Maximum RPM", options=[2400, 2700])
        st.session_state.selected_rpm = max_rpm
        # st.session_state.get("selected_rpm")
    with column4:
       # Filter based on persistent data
        available_options = st.session_state.prop_catalog.get(str_blades, [])
        # Dropdown to select propeller type
        prop_type = st.selectbox("Propeller Type", options=available_options)
        st.session_state.selected_prop = prop_type
        # st.session_state.get("selected_prop")
    
    # Reset flag is the prop has changed
    if "last_prop" not in st.session_state:
        st.session_state.last_prop = prop_type
    if prop_type != st.session_state.last_prop:
        st.session_state.prop_log_finalized = False
        st.session_state.last_prop = prop_type
    if 'beaver_oat' not in st.session_state:
        st.session_state.beaver_oat = get_beaver_bank_weather()
    
    


    # Display Logic
    # is_3_blade = (str_blades == "3")
    # if is_3_blade and prop_type:
    #     display_adjustable_prop_form(prop_type)
    
    # Button visibility logic
    # Show "Confirm" only if:
    # 1. It's NOT a 3-blade prop
    # OR
    # 2. It's a 3 blade prop and the user clicked the 'Update Log' button
    show_confirm = details_filled # and not is_3_blade or st.session_state.prop_log_finalized
        
    # Load engine configuration based on selected type
    selected_config = engine_config[engine_type]
    # st.write(show_confirm)
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
        # Warning if some fields are missing
        if not details_filled:
            hidden_btn_warning = st.warning("Please fill in all Test Details (Customer, S/N, Work Order, Nature of Test)")
        # elif is_3_blade and not st.session_state.prop_log_finalized:
            # hidden_btn_warning = st.warning("Please save the adjustable propeller log to enable the Confirm button")

    
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

