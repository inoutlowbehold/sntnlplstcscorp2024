import streamlit as st
import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
from PIL import Image
import cv2

st.set_page_config(layout="wide")

# this is for styling
st.markdown(f"""
    <style>
        /* Main background color */
        .main {{
            background-color: #b3cf99;
        }}

        /* Text styling for markdown, text inputs, and number inputs */
        .stMarkdown, .stTextInput, .stNumberInput {{
            color: #2d5128;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Heading styling */
        h1, h2, h3, h4, h5, h6 {{
            color: #262730;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Button styling */
        .stButton button {{
            background-color: #2d5128;
            color: white;
            border-color: #2d5128;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Secondary container background color */
        .secondary-container {{
            background-color: #e0e0ef;
        }}

        /* Custom text size */
        .custom-text {{
            font-size: 24px;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Specific styling for class 'css-1d391kg' */
        .css-1d391kg, .css-1d391kg * {{
            background-color: #2d5128 !important;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Optional additional styling for overall text and layout consistency */
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #2d5128;
        }}
        .sidebar .sidebar-content {{
            background-color: #e0e0ef;
            color: #2d5128;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}
    </style>
""", unsafe_allow_html=True)


# sidebar
img = Image.open("sentinel-logo-removebg-preview.png")
st.sidebar.image(
    img ,
    width= 280,
    channels= "RGB"
)
# write here what your webpage is about
st.sidebar.info("""
Streamlines inventory tracking, pallet positioning, and stock management.
""")

with st.sidebar:
    page = option_menu(
        menu_title="DATA ENTRY FORMS",
        options=["RECEIVE FORM", "RELEASE FORM", "RECEIVE PALLET POSITION", "RELEASE PALLET POSITION", 'LOCATOR'],
        icons=["caret-right-fill", "caret-right-fill", "caret-right-fill", "caret-right-fill", "search"],
        menu_icon="menu-button-wide-fill",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#c2d5aa"},
            "icon": {"color": "#5c7650", "font-size": "13px"}, 
            "nav-link": {
                "font-size": "13px",
                "text-align": "left",
                "margin": "1px",
                "--hover-color": "#e1dace",
            },
            "nav-link-selected": {"background-color": "#bbc9c0"},
            "menu-title": {"font-size": "18px", "font-weight": "bold"},
        },
    )

# if we click receive form
if page == "RECEIVE FORM":
    # Display Title and Description with center alignment and design
    st.markdown(
        """
        <h2 style="text-align: center; font-size: 24px; font-weight: bold; color: #333; margin-top: 20px;">WAREHOUSE MANAGEMENT PORTAL</h2>
        <h4 style="text-align: center; font-size: 18px; font-weight: normal; color: #666;">RECEIVED STOCK DATA ENTRY</h4>
        """, 
        unsafe_allow_html=True
    )
    url = "1w_4eJdKW5l5WeSk5F4yAKARFxUhZVbx9j3_ujeS_BZ0"

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing data from the specified worksheet
    existing_data = conn.read(spreadsheet=url, usecols=list(range(7)), ttl=100)
    existing_data = existing_data.dropna(how="all")

    # st.dataframe(existing_data)

    products = ["Armchair", "Trolley", "Pallets"]
    color = ["orange", "black", "green"]

    with st.form(key="received_form"):
        production_id_text = st.text_input("Production ID* (Enter a number)", placeholder="e.g., 000-0-00000")
        product_type = st.selectbox("Product Received*", options=products, index=None)
        color_type = st.selectbox("Color*", options=color, index=None)
        quantity = st.number_input("Quantity*", value=0, step=1, format="%d")
        onboarding_date = st.date_input(label="Date")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not product_type or not color_type or not quantity or not onboarding_date:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                received_data = pd.DataFrame(
                    [
                        {
                            "PRODUCTION CODE": production_id_text,
                            "DATE": onboarding_date.strftime("%m-%d-%Y"),
                            "PRODUCT": product_type,
                            "COLOR": color_type,
                            "ITEM CODE": None,
                            "QUANTITY": quantity,
                            "STATUS": "RECEIVED"
                            
                        }
                    ]
                )    
                updated_df = pd.concat([existing_data, received_data], ignore_index=True)
                st.dataframe(updated_df)
                st.success("Received Details successfully submitted!")

                # Use gspread to update the Google Sheets
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("received-form-data-entry-fe281fc8d580.json", scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}").sheet1

                # Convert the new data to a list of lists
                new_row = received_data.values.tolist()[0]

                # Append the new row to the sheet
                sheet.append_row(new_row)


if page == "RELEASE FORM":
    # Display Title and Description with center alignment and design
    st.markdown(
        """
        <h2 style="text-align: center; font-size: 24px; font-weight: bold; color: #333; margin-top: 20px;">WAREHOUSE MANAGEMENT PORTAL</h2>
        <h4 style="text-align: center; font-size: 18px; font-weight: normal; color: #666;">RELEASED STOCK DATA ENTRY</h4>
        """, 
        unsafe_allow_html=True
    )
    url = "18qFvLbwSkQg3f-A87sLsLq6h7R3nWam0ZAjRPu5rujc"

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing data from the specified worksheet
    existing_data = conn.read(spreadsheet=url, usecols=list(range(7)), ttl=100)
    existing_data = existing_data.dropna(how="all")

    # st.dataframe(existing_data)

    products = ["Armchair", "Trolley", "Pallets"]
    color = ["orange", "black", "green"]

    with st.form(key="released_form"):
        production_id_text = st.text_input("Production ID* (Enter a number)", placeholder="e.g., 000-0-00000")
        product_type = st.selectbox("Product Released*", options=products, index=None)
        color_type = st.selectbox("Color*", options=color, index=None)
        quantity = st.number_input("Quantity*", value=0, step=1, format="%d")
        onboarding_date = st.date_input(label="Date")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not product_type or not color_type or not quantity or not onboarding_date:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                received_data = pd.DataFrame(
                    [
                        {
                            "PRODUCTION CODE": production_id_text,
                            "DATE": onboarding_date.strftime("%m-%d-%Y"),
                            "PRODUCT": product_type,
                            "COLOR": color_type,
                            "ITEM CODE": None,
                            "QUANTITY": quantity,
                            "STATUS": "RELEASED"
                            
                        }
                    ]
                )    
                updated_df = pd.concat([existing_data, received_data], ignore_index=True)
                st.dataframe(updated_df)
                st.success("Received Details successfully submitted!")

                # Use gspread to update the Google Sheets
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("released-form-data-entry-36bcab03209d.json", scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}").sheet1

                # Convert the new data to a list of lists
                new_row = received_data.values.tolist()[0]

                # Append the new row to the sheet
                sheet.append_row(new_row)

if page == "RECEIVE PALLET POSITION":
    st.markdown(
        """
        <h2 style="text-align: center; font-size: 24px; font-weight: bold; color: #333; margin-top: 20px;">WAREHOUSE MANAGEMENT PORTAL</h2>
        <h4 style="text-align: center; font-size: 18px; font-weight: normal; color: #666;">PALLET RECEIVE DATA ENTRY</h4>
        """, 
        unsafe_allow_html=True
    )
    url= "1c9wqNXrRX5xrYcJlphQeAQNbbX5vZj9czWbNtnGxf7I"

    # Set up the credentials and client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("pallet-receive-form-data-entry-900b02a7c13d.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheets document by URL and select the 'LOCATOR' sheet
    sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}/edit?gid=25345550#gid=25345550")
    worksheet = sheet.worksheet("PALLET RECEIVE")

    data = worksheet.get('A:I')

    existing_data = pd.DataFrame(data[3:], columns=data[2])

    products = ["Armchair", "Trolley", "Pallets"]
    color = ["orange", "black", "green"]

    with st.form(key="received_form"):
        production_id_text = st.text_input("Production ID* (Enter a number)", placeholder="e.g., 000-0-00000")
        product_type = st.selectbox("Product Received*", options=products, index=None)
        color_type = st.selectbox("Color*", options=color, index=None)
        quantity = st.number_input("Quantity*", value=0, step=1, format="%d")
        onboarding_date = st.date_input(label="Date")
        pallet_position = st.text_input("Position No.*", placeholder="e.g., P001")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not product_type or not color_type or not quantity or not onboarding_date:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                received_data = pd.DataFrame(
                    [
                        {
                            "PRODUCTION CODE": production_id_text,
                            "DATE": onboarding_date.strftime("%m-%d-%Y"),
                            "PRODUCT": product_type,
                            "COLOR": color_type,
                            "ITEM CODE": None,
                            "QUANTITY": quantity,
                            "POSITION NO.": pallet_position,
                            "STATUS": "RECEIVED"
                            
                        }
                    ]
                )    
                updated_df = pd.concat([existing_data, received_data], ignore_index=True)
                st.dataframe(updated_df)
                st.success("Received Details successfully submitted!")

                # Use gspread to update the Google Sheets
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("pallet-receive-form-data-entry-900b02a7c13d.json", scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}").sheet1

                # Convert the new data to a list of lists
                new_row = received_data.values.tolist()[0]

                # Append the new row to the sheet
                sheet.append_row(new_row)


if page == "RELEASE PALLET POSITION":
    st.markdown(
        """
        <h2 style="text-align: center; font-size: 24px; font-weight: bold; color: #333; margin-top: 20px;">WAREHOUSE MANAGEMENT PORTAL</h2>
        <h4 style="text-align: center; font-size: 18px; font-weight: normal; color: #666;">PALLET RELEASE DATA ENTRY</h4>
        """, 
        unsafe_allow_html=True
    )
    url= "1c9wqNXrRX5xrYcJlphQeAQNbbX5vZj9czWbNtnGxf7I"

     # Set up the credentials and client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("pallet-release-form-data-entry-bce5f3407732.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheets document by URL and select the 'LOCATOR' sheet
    sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}/edit?gid=25345550#gid=25345550")
    worksheet = sheet.worksheet("PALLET RELEASE")

    data = worksheet.get('A:I')

    existing_data = pd.DataFrame(data[4:], columns=data[2])
    
    products = ["Armchair", "Trolley", "Pallets"]
    color = ["orange", "black", "green"]

    with st.form(key="received_form"):
        production_id_text = st.text_input("Production ID* (Enter a number)", placeholder="e.g., 000-0-00000")
        product_type = st.selectbox("Product Released*", options=products, index=None)
        color_type = st.selectbox("Color*", options=color, index=None)
        quantity = st.number_input("Quantity*", value=0, step=1, format="%d")
        onboarding_date = st.date_input(label="Date")
        pallet_position = st.text_input("Position No.*", placeholder="e.g., P001")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not product_type or not color_type or not quantity or not onboarding_date:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                received_data = pd.DataFrame(
                    [
                        {
                            "PRODUCTION CODE": production_id_text,
                            "DATE": onboarding_date.strftime("%m-%d-%Y"),
                            "PRODUCT": product_type,
                            "COLOR": color_type,
                            "ITEM CODE": None,
                            "QUANTITY": quantity,
                            "POSITION NO.": pallet_position,
                            "STATUS": "RELEASED"
                            
                        }
                    ]
                )    
                updated_df = pd.concat([existing_data, received_data], ignore_index=True)
                st.dataframe(updated_df)
                st.success("Received Details successfully submitted!")

                # Use gspread to update the Google Sheets
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("pallet-release-form-data-entry-bce5f3407732.json", scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}").sheet1

                # Convert the new data to a list of lists
                new_row = received_data.values.tolist()[0]

                # Append the new row to the sheet
                sheet.append_row(new_row)

if page == "LOCATOR":
    st.title('LOCATOR')
    url = "16_AhhQk6bqNaNy64FH6tykSXQk4ERz1K6_-brC6Aisk"

    # Set up the credentials and client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("locator-431206-96f27ecd32e2.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheets document by URL and select the 'POSITION STATUS' sheet
    sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}/edit?fbclid=IwZXh0bgNhZW0CMTEAAR2qsUQxbiuCJmeIyFht8V")
    worksheet = sheet.worksheet("POSITION STATUS")

    # Fetch the data from the 'POSITION STATUS' sheet
    data = worksheet.get_all_values()

    # Convert the data to a DataFrame
    columns = data[2]  # Assuming the first row contains headers
    rows = data[2:]    # Assuming the second row onwards contains data
    existing_data = pd.DataFrame(rows, columns=columns)

    # Define product and color options
    products = ["Armchair", "Trolley", "Pallets"]
    colors = ["orange", "black", "green"]

    # Select product and color using selectbox
    search_product = st.selectbox("Product*", options=products)
    search_color = st.selectbox("Color*", options=colors)

    # Filter the DataFrame based on the selected product and color
    filtered_data = existing_data[
        (existing_data["PRODUCT"] == search_product) &
        (existing_data["COLOR"] == search_color)
    ]

    # Initialize result
    result = 0

    # Process filtered data based on column 8
    for _, row in filtered_data.iterrows():
        if row['STATUS'] == 'RECEIVED':
            result += int(row['QUANTITY'])
        elif row['STATUS'] == 'RELEASED':
            result -= int(row['QUANTITY'])

    # Display result
    st.write(f'The net quantity for {search_product} in {search_color} is: {result}')

    # Warehouse layout data
    rows = {
        "Column 1": ["P{:03d}".format(i) for i in range(1, 13)] + [None, None],
        "Column 2": ["AISLE 1"] * 12 + [None, None],
        "Column 3": ["P{:03d}".format(i) for i in range(13, 25)] + [None, None],
        "Column 4": ["AISLE 2"] * 12 + [None, None],
        "Column 5": ["P{:03d}".format(i) for i in range(25, 37)] + [None, None],
        "Column 6": ["AISLE 3"] * 12 + [None, None],
        "Column 7": ["P{:03d}".format(i) for i in range(37, 51)],
        "Column 8": ["AISLE 4"] * 14
    }

    # Create the DataFrame for warehouse layout
    warehouse_df = pd.DataFrame(rows)

    # List of positions to highlight
    positions_to_highlight = filtered_data['POSITION NO.'].tolist()

    # Function to apply highlighting
    def highlight(val, col_index):
        if val in positions_to_highlight:
            return 'background-color: red'
        elif col_index in [1, 3, 5]:  # Highlight columns 2, 4, 6
            return 'background-color: peachpuff'
        return ''

    # Apply the highlighting function to the DataFrame
    styled_warehouse_df = warehouse_df.style.apply(
        lambda x: [highlight(v, x.index.get_loc(col)) for col, v in x.items()], axis=1
    )

    # Display the DataFrame
    st.markdown("## WAREHOUSE LAYOUT")
    st.dataframe(styled_warehouse_df)