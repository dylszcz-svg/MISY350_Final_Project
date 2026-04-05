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

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role" : "assistant",
            "content" : "Hi! I am your Clinic Assistant. How can I help you?"
        }
    ]


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
                    key="slot_time_input")
            
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

    # view appointments page (with update)
    elif st.session_state["page"] == "view_appointments":
        st.title("Patient Appointments")
        st.divider()
 
        if len(appointments) == 0:
            st.info("No appointments booked yet.")
        else:
            col1, col2 = st.columns([3, 2])
 
            with col1:
                st.dataframe(appointments)
 
            with col2:
                with st.container(border=True):
                    st.subheader("Update Status")
 
                    selected_appt = st.selectbox(
                        "Select Appointment",
                        options=appointments,
                        format_func=lambda x: f"{x['patient_name']} - {x['date']}",
                        key="doc_select_appt"
                    )
 
                    if selected_appt:
                        st.markdown(f"**Current Status:** {selected_appt['status']}")
                        st.markdown(f"**Patient Notes:** {selected_appt['notes']}")
 
                        new_status = st.selectbox(
                            "Change Status To",
                            ["Booked", "Completed", "No-Show", "Cancelled"],
                            key="doc_status_select")
 
                        doctor_note = st.text_area("Doctor Notes",
                            placeholder="Add notes...",
                            key="doc_note_input")
 
                        if st.button("Update Status",
                                     type="primary",
                                     use_container_width=True,
                                     key="doc_update_btn"):
                            with st.spinner("Updating..."):
                                time.sleep(2)
 
                                # find and update the appointment
                                for appt in appointments:
                                    if appt["appointment_id"] == selected_appt["appointment_id"]:
                                        appt["status"] = new_status
                                        appt["notes"] = doctor_note
                                        break
 
                                # save to json
                                with open(json_path_appointments, "w") as f:
                                    json.dump(appointments, f)
 
                                st.success("Status updated!")
                                time.sleep(2)
                                st.rerun()



elif st.session_state["role"] == "Patient":

    # patient sidebar navigation
    with st.sidebar:
        st.divider()
        if st.button("Home", key="pat_home_btn",
                     use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()

        if st.button("Book Appointment", key="pat_book_btn",
                     use_container_width=True):
            st.session_state["page"] = "book"
            st.rerun()

        if st.button("My Appointments", key="pat_myappts_btn",
                     use_container_width=True):
            st.session_state["page"] = "my_appointments"
            st.rerun()

    # patient home page
    if st.session_state["page"] == "home":
        st.title("Patient Dashboard")
        st.markdown(f"Welcome, **{st.session_state['user']['full_name']}**!")
        st.divider()

        # count this patients appointments
        my_appt_count = 0
        for appt in appointments:
            if appt["patient_email"] == st.session_state["user"]["email"]:
                my_appt_count += 1

        col1, col2 = st.columns(2)
        with col1:
            st.metric("My Appointments", my_appt_count)
        with col2:
            available_count = 0
            for slot in slots:
                if slot["status"] == "Available":
                    available_count += 1
            st.metric("Available Slots", available_count)

    
    # book appointment page

    elif st.session_state["page"] == "book":
        st.title("Book an Appointment")
        st.divider()

        
        col1, col2 = st.columns([3,2])

        with col1:
            available_slots = []
            for slot in slots:
                if slot["status"] == "Available":
                    available_slots.append(slot)
            
            if len(available_slots) == 0:
                st.warning("No available time slots right now.")
            else:
                with st.container(border = True):
                    selected_slot = st.selectbox(
                        "Select a Time Slot", options = available_slots,
                        format_func = lambda x: f"{x["date"]} at {x["time"]}", key = "book_slot_select"
                    )
                    
                    patient_notes = st.text_area(
                        "Notes for the Dcoctor (Optional)", placeholder = "Describe your symptoms...",
                        key = "book_notes_input"
                    )

                    if st.button("Book This Slot", type = "primary", use_container_width = True, key = "book_apt_btn"):
                        with st.spinner("Booking..."):
                            time.sleep(2)

                            # record appointments
                            appointments.append(
                                {
                                    "appointment_id" : "APT-" + str(uuid.uuid4())[:8],
                                    "slot_id" : selected_slot["slot_id"],
                                    "patient_email" : st.session_state["user"]["email"],
                                    "patient_name" : st.session_state["user"]["full_name"],
                                    "date" : selected_slot["date"],
                                    "time" : selected_slot["time"],
                                    "status" : "Booked",
                                    "notes" : patient_notes
                                }
                            )

                            # marking booked slots
                            for slot in slots:
                                if slot["slot_id"] == selected_slot["slot_id"]:
                                    slot["status"] = "Booked"
                                    break
                            
                            # save to json
                            with open(json_path_appointments, "w") as f:
                                json.dump(appointments, f)
                            with open(json_path_slots, "w") as f:
                                json.dump(slots, f)
                            
                            st.success("Appointment Booked!")
                            st.balloons()
                            time.sleep(3)
                            st.rerun()
        
        # chatbot

        with col2:
            


 
    elif st.session_state["page"] == "my_appointments":
        st.title("My Appointments")
        st.divider()

      
        my_appointments = []
        for appt in appointments:
            if appt["patient_email"] == st.session_state["user"]["email"]:
                my_appointments.append(appt)

        if len(my_appointments) == 0:
            st.info("You have no appointments yet.")
        else:
            st.dataframe(my_appointments)
                        
            st.divider()
            with st.container(border=True):
                st.subheader("Cancel an Appointment")
 
                
                booked_appts = []
                for appt in my_appointments:
                    if appt["status"] == "Booked":
                        booked_appts.append(appt)
 
                if len(booked_appts) == 0:
                    st.info("No active appointments to cancel.")
                else:
                    cancel_appt = st.selectbox(
                        "Select Appointment to Cancel",
                        options=booked_appts,
                        format_func=lambda x: f"{x['date']} at {x['time']}",
                        key="cancel_appt_select")
 
                    if st.button("Cancel This Appointment",
                                 type="primary",
                                 use_container_width=True,
                                 key="cancel_appt_btn"):
                        with st.spinner("Cancelling..."):
                            time.sleep(2)
 
                           
                            for appt in appointments:
                                if appt["appointment_id"] == cancel_appt["appointment_id"]:
                                    appt["status"] = "Cancelled"
                                    break
 
                            
                            for slot in slots:
                                if slot["slot_id"] == cancel_appt["slot_id"]:
                                    slot["status"] = "Available"
                                    break
 
                            
                            with open(json_path_appointments, "w") as f:
                                json.dump(appointments, f)
 
                            with open(json_path_slots, "w") as f:
                                json.dump(slots, f)
 
                            st.success("Appointment cancelled.")
                            time.sleep(2)
                            st.rerun()



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