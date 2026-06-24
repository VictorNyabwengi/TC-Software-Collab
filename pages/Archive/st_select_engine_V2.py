import streamlit as st
import commentjson as json
from st_main import pages
import re
from collections import OrderedDict
import time

# Ensure the user has selected an engine
if 'logo' not in st.session_state: #or st.session_state.selected_engine is None:
    st.warning("Initialization incomplete. Redirecting to main page...")
    time.sleep(1)
    st.switch_page(r"C:\Users\theca\Documents\Victor\Aerotec\MVP 50\Code\AerotecTestCell\st_main.py")  # Redirect back to engine selection
else:
    # st.title(f"Dashboard for {st.session_state.selected_engine}")
    # Display the dashboard content for the selected engine
    st.write("Kindly select an engine")

# st_autorefresh(3000, key="select_screen_refresh")  # Refresh at a specified interval

# st.set_page_config(layout="wide", page_title="Select Engine", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")

def load_config():
    """Load JSON configuration file."""
    with open(r"C:\Users\theca\Documents\Victor\Aerotec\MVP 50\Code\AerotecTestCell\4 Cyl Dashboard Config.json", "r") as f:
        return json.load(f, object_pairs_hook=OrderedDict) # Use OrderedDict to maintain order

@st.fragment()
def save_config(updated_config, engine_type):
    """Save updated configuration to the JSON file."""
    with open(r"C:\Users\theca\Documents\Victor\Aerotec\MVP 50\Code\AerotecTestCell\4 Cyl Dashboard Config.json", "r") as f:
        config_data = json.load(f)

    # Update the configuration for the selected engine type
    config_data[engine_type] = updated_config

    with open(r"C:\Users\theca\Documents\Victor\Aerotec\MVP 50\Code\AerotecTestCell\4 Cyl Dashboard Config.json", "w") as f:
        json.dump(config_data, f, indent=4)

    st.rerun()

def authenticate(password, engine_type):
    """Authenticate the user with a predefined common password for all engines except 'Configurable 4 Cylinder'."""
    # Define a common password for all engines that need authentication
    common_password = '00100'  # Replace with the actual secure password

    # Engine type that does NOT require authentication
    no_auth_engine = 'Configurable 4 Cylinder'

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

def display_config_inputs(engine_type, config):
    """Display input fields for configuration settings in a grid layout."""

    with st.expander("Open to edit"):
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
        fields = generate_fields_from_config(config)

        # Dynamically populate the grid with input fields
        for index, (label, key) in enumerate(fields):
            # st.write(f"{fields}")
            col = all_columns[index % len(all_columns)]  # Determine the column to place the input
            with col.container(height=100):
                # Determine the input type based on the key or value
                if isinstance(config[key], bool):  # Handle boolean fields with checkboxes
                    config[key] = st.checkbox(label, value=config[key], key=f"{engine_type}_{key}")
                elif isinstance(config[key], (int, float)):  # Handle numerical fields with number_input
                    config[key] = st.number_input(label, value=config[key], key=f"{engine_type}_{key}")
                else:
                    # Add more field types if needed
                    pass
                # config[key] = st.number_input(label, value=config[key], key=f"{engine_type}_{key}")


def main():

    # CSS to hide the sidebar expander
#     st.markdown(
#         """
#     <style>
#         [data-testid="collapsedControl"] {
#             display: none
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
    # # Add Aerotec Logo
    # st.session_state.logo = r"C:\Users\theca\Documents\Victor\Aerotec\MVP 50\Code\AerotecTestCell\ae-logo_svg.svg"
    st.logo(st.session_state.logo)

    # # Set page icon
    # st.session_state.page_icon = r"C:\Users\theca\Documents\Victor\Aerotec\MVP 50\Code\AerotecTestCell\ae-logo_jpg.jpeg"
    # st.set_page_config(layout="wide", page_title="Select Engine", page_icon=st.session_state.page_icon, initial_sidebar_state="collapsed")
    


    # Load engine configuration
    engine_config = load_config()

    # Dropdown to select an engine type
    engine_type = st.selectbox("Engine Type", list(engine_config.keys()))

    # Confirm button for selecting an engine type
    if st.button(f"Confirm {engine_type}"):
        st.session_state.selected_engine = engine_type  # Store selected engine in session state
        st.success(f"{engine_type} confirmed")
        # Navigate to the dashboard page
        st.switch_page(pages["Dashboard"])
        # st.query_params["page"] = "dashboard"  # Update query parameters to switch page

    # Load engine configuration based on selected type
    config = engine_config[engine_type]

    # config_variables = get_config_variables(config)

    # Display configuration inputs based on engine type
    if engine_type == "Configurable 4 Cylinder":
        display_config_inputs(engine_type, config)
    elif engine_type == "Data Only Dashboard":
        return
    elif engine_type == "  ":
        return
    else:
        # Password input for other engine types
        password = st.text_input("Enter Password for Editing (Press Enter Key When Done)", type="password")
        if password:
            if authenticate(password, engine_type):
                st.success("Authenticated Successfully!")
                display_config_inputs(engine_type, config)
            else:
                st.error("Incorrect Password. Please try again.")

    # Save button to save the configuration
    if st.button("Save Configuration"):
        save_config(config, engine_type)
        st.success("Configuration saved successfully")

# Call main() only if this script is run directly
if __name__ == "__main__":
    main()

