import streamlit as st
import json
from pathlib import Path
import uuid
import time


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


# load users
users = [
    {
        "id": "1",
        "email": "doctor@clinic.com",
        "full_name": "Dr. Smith",
        "password": "doc123",
        "role": "Doctor"
    }
]

json_path_users = Path("users.json")
if json_path_users.exists():
    with open(json_path_users, "r") as f:
        users = json.load(f)


# load slots
slots = []

json_path_slots = Path("slots.json")
if json_path_slots.exists():
    with open(json_path_slots, "r") as f:
        slots = json.load(f)


# load appointments
appointments = []

json_path_appointments = Path("appointments.json")
if json_path_appointments.exists():
    with open(json_path_appointments, "r") as f:
        appointments = json.load(f)


# role based routing
if st.session_state["role"] == "Doctor":
    st.markdown("## Doctor Dashboard - Coming Soon")

elif st.session_state["role"] == "Patient":
    st.markdown("## Patient Dashboard - Coming Soon")

else:
# guest view
    st.title("Clinic Appointment Tracker")
    st.caption("A scheduling portal for patients and doctors")
    st.divider()
    st.info("Login and Registration coming next!")