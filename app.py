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
    
    # dr. sidebar
    with st.sidebar:
        st.divider()
        if st.button("Home", key = "doc_home_btn", use_container_width = True):
            st.session_state["page"] = 'home'
            st.rerun()
        
        if st.button("Manage Slots", key = "doc_slots_btn", use_container_width = True):
            st.session_state["page"] = "manage_slots"
            st.rerun()
        
        if st.button("View Appointments", key = "doc_appts_btn", use_container_width = True):
            st.session_state["page"] = "view_appointments"
            st.rerun()


    # dr. home page

    if st.session_state["page"] == "home":
        st.title("Doctor Dashboard")
        st.markdown(f"Welcome, **{st.session_state['user']['full_name']}**!")
        st.divider()

        # display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Slots", len(slots))
        with col2:
            # counts and shows available slots
            available_count = 0
            for slot in slots:
                if slot["status"] == "Available":
                    available_count += 1
            st.metric("Available Slots", available_count)
        with col3:
            st.metric("Total Appointments", len(appointments))

    # manage slots page for dr.
    elif st.session_state["page"] == "manage_slots":
        st.title("Manage Time Slots")
        st.divider()

        tab1, tab2 = st.tabs(["View All Slots", "Add New Slots"])

        with tab1:
            if len(slots) > 0:
                st.dataframe(slots)
            else:
                st.warning("No time slots created yet.")
        
        with tab2:
            st.subheader("Add a New Time Slot")
            with st.container(border = True):
                slot_date = st.date_input("Date", key = "slot_date_input")
                slot_time = st.selectbox("Time",
                    ["9:00 AM", "10:00 AM", "11:00 AM",
                     "1:00 PM", "2:00 PM", "3:00 PM",
                     "4:00 PM"],
                    key="slot_time_input"),
            
                if st.button("Create Slot", key = "create_slot_btn", type = "primary",
                             use_container_width = True):
                    with st.spinner("Creating slot..."):
                        time.sleep(2)

                        # generate id
                        new_slot_id = "SLOT" + str(len(slots) + 1)

                        # add to list
                        slots.append(
                            {
                                "slot_id" : new_slot_id,
                                "doctor_email" : st.session_state["user"]["email"],
                                "date" : str(slot_date),
                                "time" : slot_time,
                                "status" : "Available"
                            }
                        )

                        # save to json
                        with open (json_path_slots, "w") as f:
                            json.dump(slots, f)
                        
                        st.success("New time slot created!")
                        time.sleep(2)
                        st.rerun()

    # View appointment page

    elif st.session_state["page"] == "view_appointments":
        st.title("Patient Appointments")
        st.divider()

        if len(appointments) > 0:
            st.dataframe(appointments)
        else:
            st.info("No appointments booked yet.")


elif st.session_state["role"] == "Patient":
    st.markdown("## Patient Dashboard - Coming Soon")

else:
    # guest view
    st.title("Clinic Appointment Tracker")
    st.caption("A scheduling portal for patients and doctors")
    st.divider()

    tab_login, tab_register = st.tabs(["Log In", "Create Account"])

    with tab_login:
        st.subheader("Log In")
        with st.container(border=True):
            email_input = st.text_input("Email", key="login_email",
                                        placeholder="Enter your email")
            password_input = st.text_input("Password", type="password",
                                           key="login_password")

            if st.button("Log In", type="primary",
                         use_container_width=True, key="login_btn"):
                if not email_input or not password_input:
                    st.warning("Please enter your email and password.")
                else:
                    with st.spinner("Logging in..."):
                        time.sleep(2)

                        # search for user
                        found_user = None
                        for user in users:
                            if user["email"].strip().lower() == email_input.strip().lower() and user["password"] == password_input:
                                found_user = user
                                break

                        if found_user:
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = found_user
                            st.session_state["role"] = found_user["role"]
                            st.session_state["page"] = "home"

                            st.success(f"Welcome back, {found_user['full_name']}!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

    with tab_register:
        st.subheader("Create a New Account")
        with st.container(border=True):
            new_name = st.text_input("Full Name", key="register_name",
                                     placeholder="Enter your full name")
            new_email = st.text_input("Email", key="register_email",
                                      placeholder="Enter your email")
            new_password = st.text_input("Password", type="password",
                                         key="register_password")
            new_role = st.radio("I am a...", ["Patient", "Doctor"],
                                key="register_role", horizontal=True)

            if st.button("Create Account", key="register_btn",
                         use_container_width=True):
                if not new_name or not new_email or not new_password:
                    st.warning("Please fill out all fields.")
                else:
                    with st.spinner("Creating account..."):
                        time.sleep(2)

                        # check if email exists
                        email_exists = False
                        for user in users:
                            if user["email"].strip().lower() == new_email.strip().lower():
                                email_exists = True
                                break

                        if email_exists:
                            st.error("This email is already registered.")
                        else:
                            users.append({
                                "id": str(uuid.uuid4()),
                                "email": new_email,
                                "full_name": new_name,
                                "password": new_password,
                                "role": new_role
                            })

                            with open(json_path_users, "w") as f:
                                json.dump(users, f)

                            st.success("Account created! You can now log in.")
                            time.sleep(2)
                            st.rerun()


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