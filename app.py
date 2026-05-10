import streamlit as st
import time
from pathlib import Path
 
from data.data_manager import DataManager
from services.clinic_manager import ClinicManager
from ui.login_page import render_login
from ui.doctor_ui import render_doctor
from ui.patient_ui import render_patient
 
 
# page config
st.set_page_config(
    page_title="Clinic Appointment Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
 
# session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
 
if "user" not in st.session_state:
    st.session_state["user"] = None
 
if "role" not in st.session_state:
    st.session_state["role"] = None
 
if "page" not in st.session_state:
    st.session_state["page"] = "login"
 
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant",
         "content": "Hi! I am your Clinic Assistant. How can I help you?"}
    ]
 
 
# load data using data layer
user_store = DataManager("users.json")
slot_store = DataManager("slots.json")
appt_store = DataManager("appointments.json")
 
users = user_store.load()
slots = slot_store.load()
appointments = appt_store.load()
 
# if no users exist, add default test accounts
if len(users) == 0:
    users = [
        {
            "id": "1",
            "email": "doctor@clinic.com",
            "full_name": "Dr. Smith",
            "password": "doc123",
            "role": "Doctor"
        },
        {
            "id": "2",
            "email": "patient@clinic.com",
            "full_name": "Jane Doe",
            "password": "pat123",
            "role": "Patient"
        }
    ]
    user_store.save(users)
 
# if no slots exist, add sample slots
if len(slots) == 0:
    slots = [
        {"slot_id": "SLOT1", "doctor_email": "doctor@clinic.com",
         "date": "2026-05-15", "time": "9:00 AM", "status": "Available"},
        {"slot_id": "SLOT2", "doctor_email": "doctor@clinic.com",
         "date": "2026-05-15", "time": "10:00 AM", "status": "Booked"},
        {"slot_id": "SLOT3", "doctor_email": "doctor@clinic.com",
         "date": "2026-05-16", "time": "1:00 PM", "status": "Available"},
        {"slot_id": "SLOT4", "doctor_email": "doctor@clinic.com",
         "date": "2026-05-16", "time": "3:00 PM", "status": "Available"}
    ]
    slot_store.save(slots)
 
# if no appointments exist, add sample appointment
if len(appointments) == 0:
    appointments = [
        {"appointment_id": "APT-sample1", "slot_id": "SLOT2",
         "patient_email": "patient@clinic.com",
         "patient_name": "Jane Doe",
         "date": "2026-05-15", "time": "10:00 AM",
         "status": "Booked", "notes": "Annual checkup"}
    ]
    appt_store.save(appointments)
 
 
# create manager object from service layer
manager = ClinicManager(users, slots, appointments)
 
 
# role based routing
if st.session_state["role"] == "Doctor":
    render_doctor(manager, slot_store, appt_store)
 
elif st.session_state["role"] == "Patient":
    render_patient(manager, slot_store, appt_store)
 
else:
    render_login(manager, user_store)
 
 
# sidebar
with st.sidebar:
    st.markdown("### Clinic Manager")
    if st.session_state["logged_in"]:
        user = st.session_state["user"]
        st.markdown(f"Logged in as: **{user['full_name']}**")
        st.markdown(f"Role: **{st.session_state['role']}**")
        st.divider()
 
        if st.button("Log Out", type="primary",
                     use_container_width=True, key="logout_btn"):
            with st.spinner("Logging out..."):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                time.sleep(2)
                st.rerun()
    else:
        st.info("Please log in to continue.")
 
