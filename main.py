import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="SUL Transfer Tracker", layout="wide")

DATA_FILE = "transfer_data.csv"

st.title("🚌 SUL Transfer Tracker")

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Date", "Day", "Centre", "Transfer Type", "Agency", "Nationality",
            "Grp/Ind", "Pax", "Meet & Greet", "Check In", "Flight / Train Number",
            "Pick Up", "Drop Off", "Terminal", "ETD",
            "ETA 1", "ETD 1", "ETA 2",
            "GL Nr", "Main GL / Ind Name", "GL / Ind Mobile Nr"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

centres = ["-- Select --", "University of Worcester", "Taunton School", "St. Felix School", "Shebbear College", "UCL London"]
airports_stations = ["-- Select --", "Heathrow Airport", "Gatwick Airport", "Stansted Airport", "Luton Airport", "London City Airport", "St Pancras Station"]
nationalities = ["-- Select --", "Afghanistan", "Albania", "Algeria", "United States", "Andorra", "Brazil", "China", "France", "Germany", "India", "Italy", "Japan", "Portugal", "South Korea", "Spain", "United Kingdom"]
country_codes = ["-- Select --", "+44 (United Kingdom)", "+1 (United States)", "+33 (France)", "+49 (Germany)", "+39 (Italy)", "+34 (Spain)", "+351 (Portugal)", "+86 (China)", "+91 (India)", "+81 (Japan)"]

transfer_type_selection = st.selectbox("Transfer Type", ["-- Select --", "Arrival", "Departure"])
transfer_type = transfer_type_selection
show_eta = transfer_type == "Arrival"
show_etd = transfer_type == "Departure"

# Date + Day before the form
selected_date = st.date_input("Date", datetime.today())
day_of_week = selected_date.strftime("%A")
st.markdown(f"**Day:** {day_of_week}")

drop_off_location_selection = st.selectbox("Drop Off Location", centres + ["Other (type manually)"])
if drop_off_location_selection == "Other (type manually)":
    drop_off_location = st.text_input("Enter custom Drop Off Location")
else:
    drop_off_location = drop_off_location_selection

centre_addresses = {
    "Taunton School": "Staplegrove Road, Taunton, Somerset, TA2 6AD",
    "University of Worcester": "St John's Campus, Henwick Grove, St John's, Worcester, WR2 6AJ",
    "St. Felix School": "Halesworth Road, Reydon, Southwold, IP18 6SD, England",
    "Shebbear College": "Shebbear, Beaworthy EX21 5HJ",
    "UCL London": "Taviton Street, London, WC1H 0BX"
}
auto_address = centre_addresses.get(drop_off_location, "")
drop_off_address = st.text_input("Drop Off Address (auto-filled or editable)", value=auto_address if auto_address else "", key="live_drop_off_address")

with st.form("transfer_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        selected_centre = st.selectbox("Centre", centres)
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

        if transfer_type == "Arrival":
            pick_up = st.selectbox("Pick Up (Airport / Train Station)", airports_stations)
        elif transfer_type == "Departure":
            pick_up = selected_centre
            st.markdown(f"**Pick Up Location:** {pick_up}")
            pick_up_address = st.text_input("Pick Up Address", value=centre_addresses.get(pick_up, ""))
            drop_off = st.selectbox("Drop Off (Airport / Train Station)", airports_stations)

        terminal = st.text_input("Terminal")

        etd = ""
        eta_1, etd_1, eta_2 = "", "", ""
        if show_eta:
            st.markdown("#### UK Arrival Timing")
            eta_1 = st.time_input("ETA 1 – Arrival in the UK")
            etd_1 = st.time_input("ETD 1 – Departure from Airport/Station")
            eta_2 = st.time_input("ETA 2 – Arrival at Centre")
        elif show_etd:
            etd = st.time_input("ETD", key="etd")

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
        if pick_up == "-- Select --":
            errors.append("Please select Pick Up location.")
        if drop_off_location.strip() == "":
            errors.append("Please select or enter a Drop Off Location.")
        if terminal.strip() == "":
            errors.append("Please enter Terminal.")
        if show_eta:
            if not eta_1:
                errors.append("Please enter ETA 1.")
            if not etd_1:
                errors.append("Please enter ETD 1.")
            if not eta_2:
                errors.append("Please enter ETA 2.")
        if show_etd and not etd:
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
                "Pick Up": pick_up,
                "Drop Off": drop_off_location,
                "Terminal": terminal,
                "ETD": etd,
                "ETA 1": eta_1,
                "ETD 1": etd_1,
                "ETA 2": eta_2,
                "GL Nr": gl_number,
                "Main GL / Ind Name": full_name,
                "GL / Ind Mobile Nr": full_mobile
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("✅ Transfer submitted and saved.")
            st.rerun()
