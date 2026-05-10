import streamlit as st
import time
import os
from openai import OpenAI
from dotenv import load_dotenv
 
 
def get_ai_response(client, messages, context):
    prompt = (
        "You are a helpful clinic assistant for a medical appointment app. "
        "Answer patient questions about appointments, scheduling, and clinic info. "
        "Keep responses short and helpful. "
        f"Here is the patient context: {context}"
    )
 
    system_message = [{"role": "system", "content": prompt}]
    full_messages = system_message + messages
 
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=full_messages,
        temperature=1
    )
    return response.choices[0].message.content
 
 
def render_patient(manager, slot_store, appt_store):
 
    # sidebar navigation
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
 
    # home page
    if st.session_state["page"] == "home":
        st.title("Patient Dashboard")
        st.markdown(f"Welcome, **{st.session_state['user']['full_name']}**!")
        st.divider()
 
        patient_email = st.session_state["user"]["email"]
        my_appts = manager.get_patient_appointments(patient_email)
 
        col1, col2 = st.columns(2)
        with col1:
            st.metric("My Appointments", len(my_appts))
        with col2:
            st.metric("Available Slots", manager.count_available_slots())
 
    # book appointment page with ai chatbot
    elif st.session_state["page"] == "book":
        st.title("Book an Appointment")
        st.divider()
 
        col1, col2 = st.columns([3, 2])
 
        with col1:
            available_slots = manager.get_available_slots()
 
            if len(available_slots) == 0:
                st.warning("No available time slots right now.")
            else:
                with st.container(border=True):
                    selected_slot = st.selectbox(
                        "Select a Time Slot",
                        options=available_slots,
                        format_func=lambda x: f"{x['date']} at {x['time']}",
                        key="book_slot_select"
                    )
 
                    patient_notes = st.text_area(
                        "Notes for the Doctor (optional)",
                        placeholder="Describe your symptoms...",
                        key="book_notes_input")
 
                    if st.button("Book This Slot", type="primary",
                                 use_container_width=True,
                                 key="book_appt_btn"):
                        with st.spinner("Booking..."):
                            time.sleep(2)
 
                            manager.book_appointment(
                                selected_slot["slot_id"],
                                st.session_state["user"]["email"],
                                st.session_state["user"]["full_name"],
                                patient_notes
                            )
 
                            appt_store.save(manager.appointments)
                            slot_store.save(manager.slots)
 
                            st.success("Appointment booked!")
                            st.balloons()
                            time.sleep(3)
                            st.rerun()
 
        # ai chatbot
        with col2:
            st.subheader("Clinic Assistant")
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.caption("Ask about appointments or scheduling")
            with col_b:
                if st.button("Clear Chat", key="clear_chat_btn"):
                    st.session_state["messages"] = [
                        {"role": "assistant",
                         "content": "Hi! I am your Clinic Assistant. How can I help?"}
                    ]
                    st.rerun()
 
            with st.container(border=True, height=300):
                for message in st.session_state["messages"]:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
 
            user_input = st.chat_input("Ask a question...",
                                       key="chat_input")
            if user_input:
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {"role": "user", "content": user_input}
                    )
 
                    # build context from patient data
                    patient_email = st.session_state["user"]["email"]
                    my_appts = manager.get_patient_appointments(patient_email)
                    available_count = manager.count_available_slots()
                    context = (
                        f"Patient name: {st.session_state['user']['full_name']}. "
                        f"Their appointments: {my_appts}. "
                        f"Available slots: {available_count}."
                    )
 
                    # call openai
                    load_dotenv()
                    api_key = os.getenv("OPENAI_API_KEY")
 
                    if api_key:
                        client = OpenAI(api_key=api_key)
                        ai_response = get_ai_response(
                            client,
                            st.session_state["messages"],
                            context
                        )
                    else:
                        ai_response = "AI assistant is not configured. Please add your OpenAI API key."
 
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": ai_response}
                    )
                    time.sleep(1)
                    st.rerun()
 
    # my appointments page with cancel
    elif st.session_state["page"] == "my_appointments":
        st.title("My Appointments")
        st.divider()
 
        patient_email = st.session_state["user"]["email"]
        my_appointments = manager.get_patient_appointments(patient_email)
 
        if len(my_appointments) == 0:
            st.info("You have no appointments yet.")
        else:
            st.dataframe(my_appointments)
 
            st.divider()
            with st.container(border=True):
                st.subheader("Cancel an Appointment")
 
                booked_appts = manager.get_booked_appointments(patient_email)
 
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
 
                            manager.cancel_appointment(
                                cancel_appt["appointment_id"]
                            )
 
                            appt_store.save(manager.appointments)
                            slot_store.save(manager.slots)
 
                            st.success("Appointment cancelled.")
                            time.sleep(2)
                            st.rerun()
 
