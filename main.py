import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="SUL Transfer Tracker", layout="wide")

DATA_FILE = "transfer_data.csv"

st.title("🚌 SUL Transfer Tracker")

# --- Load or create CSV
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Date", "Day", "Centre", "Transfer Type", "Agency", "Nationality",
            "Grp/Ind", "Pax", "Meet & Greet", "Check In", "Flight / Train Number",
            "Airport / Train Station", "Terminal", "ETA", "ETD",
            "GL Nr", "Main GL / Ind Name", "GL / Ind Mobile Nr"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- Country options for nationality (no codes)
nationalities = ["-- Select --", "Afghanistan", "Albania", "Algeria", "United States", "Andorra", "Brazil", "China", "France", "Germany", "India", "Italy", "Japan", "Portugal", "South Korea", "Spain", "United Kingdom"]

# --- Country codes for phone numbers
country_codes = ["-- Select --", "+44 (United Kingdom)", "+1 (United States)", "+33 (France)", "+49 (Germany)", "+39 (Italy)", "+34 (Spain)", "+351 (Portugal)", "+86 (China)", "+91 (India)", "+81 (Japan)"]

# --- Transfer Entry Form
st.header("➕ Add New Transfer")

with st.form("transfer_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        selected_date = st.date_input("Date", datetime.today())
        day_of_week = selected_date.strftime("%A")
        st.markdown(f"**Day of the Week:** {day_of_week}")
        selected_centre = st.selectbox("Centre", ["-- Select --", "University of Worcester", "Taunton School", "St. Felix School", "Shebbear College", "UCL London"])
        transfer_type = st.selectbox("Transfer Type", ["-- Select --", "Arrival", "Departure"])
        agency_name = st.text_input("Agency Name (or type 'Direct enrolment')")
        nationality = st.selectbox("Nationality", nationalities)
        group_type = st.selectbox("Grp/Ind", ["-- Select --", "Group", "Individual"])
        pax = st.number_input("Pax", min_value=1)
        meet_and_greet = st.selectbox("Meet & Greet", ["-- Select --", "Yes", "No"])

        show_check_in = (transfer_type == "Departure" and group_type == "Individual")
        if show_check_in:
            check_in = st.selectbox("Check In (only for Ind. Departures)", ["-- Select --", "Yes", "No"])
        else:
            check_in = "N/A"

        flight_number = st.text_input("Flight / Train Number")
        airport_station = st.text_input("Airport / Train Station")
        terminal = st.text_input("Terminal")

        eta, etd = "", ""
        if transfer_type == "Arrival":
            eta = st.time_input("ETA")
        elif transfer_type == "Departure":
            etd = st.time_input("ETD")

    with col2:
        gl_number = st.number_input("GL Nr (number of group leaders)", min_value=0)
        st.markdown("**Main GL / Ind Name**")
        gl_first_name = st.text_input("First Name")
        gl_last_name = st.text_input("Surname")
        st.markdown("**GL / Ind Mobile Nr**")
        selected_code = st.selectbox("Country Code", country_codes)
        gl_mobile_number = st.text_input("Mobile Number")

    submitted = st.form_submit_button("Submit Transfer")

    if submitted:
        errors = []
        if selected_centre == "-- Select --":
            errors.append("Please select a Centre.")
        if transfer_type == "-- Select --":
            errors.append("Please select a Transfer Type.")
        if agency_name.strip() == "":
            errors.append("Please enter the Agency Name or type 'Direct enrolment'.")
        if nationality == "-- Select --":
            errors.append("Please select a Nationality.")
        if group_type == "-- Select --":
            errors.append("Please select Group or Individual.")
        if gl_first_name.strip() == "" or gl_last_name.strip() == "":
            errors.append("Please enter the Main GL / Ind First and Last Name.")
        if selected_code == "-- Select --" or gl_mobile_number.strip() == "":
            errors.append("Please select a country code and enter a mobile number.")
        if meet_and_greet == "-- Select --":
            errors.append("Please select Meet & Greet option.")
        if check_in == "-- Select --" and show_check_in:
            errors.append("Please select Check In option.")
        if flight_number.strip() == "":
            errors.append("Please enter Flight / Train Number.")
        if airport_station.strip() == "":
            errors.append("Please enter Airport / Train Station.")
        if terminal.strip() == "":
            errors.append("Please enter Terminal.")
        if transfer_type == "Arrival" and not eta:
            errors.append("Please enter ETA for arrival.")
        if transfer_type == "Departure" and not etd:
            errors.append("Please enter ETD for departure.")

        if errors:
            for err in errors:
                st.warning(err)
        else:
            full_mobile = f"{selected_code.split()[0]} {gl_mobile_number.strip()}"
            full_name = f"{gl_first_name.strip()} {gl_last_name.strip()}"

            new_row = {
                "Date": selected_date.strftime("%Y-%m-%d"),
                "Day": day_of_week,
                "Centre": selected_centre,
                "Transfer Type": transfer_type,
                "Agency": agency_name,
                "Nationality": nationality,
                "Grp/Ind": group_type,
                "Pax": pax,
                "Meet & Greet": meet_and_greet,
                "Check In": check_in,
                "Flight / Train Number": flight_number,
                "Airport / Train Station": airport_station,
                "Terminal": terminal,
                "ETA": eta,
                "ETD": etd,
                "GL Nr": gl_number,
                "Main GL / Ind Name": full_name,
                "GL / Ind Mobile Nr": full_mobile
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("✅ Transfer submitted and saved.")
            st.rerun()

# --- Import Existing CSV
st.header("📁 Import Existing Transfers (CSV)")
uploaded_file = st.file_uploader("Upload a CSV file to add transfers", type="csv")
if uploaded_file:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
        df = pd.concat([df, uploaded_df], ignore_index=True).drop_duplicates()
        save_data(df)
        st.success("✅ Transfers imported successfully.")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Could not import CSV: {e}")

# --- Export CSV
st.header("📤 Export All Transfers")
@st.cache_data
def convert_df_for_download(df):
    return df.to_csv(index=False).encode('utf-8')

csv_download = convert_df_for_download(df)
st.download_button("Download Transfers as CSV", csv_download, "all_transfers.csv", "text/csv")

# --- Filter and Display Transfers
st.header("📋 All Transfers")
selected_nationality = st.selectbox("Filter by Nationality", ["All"] + sorted(df["Nationality"].dropna().unique().tolist()))
if selected_nationality != "All":
    df = df[df["Nationality"] == selected_nationality]

st.dataframe(df.sort_values("Date"), use_container_width=True)


