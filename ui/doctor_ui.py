import streamlit as st
import time


def render_doctor(manager, slot_store, appt_store):

    # sidebar navigation

    with st.sidebar: 
        st.divider()
        if st.button("Home", key="doc_home_btn",
                     use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()

        if st.button("Manage Slots", key="doc_slots_btn",
                     use_container_width=True):
            st.session_state["page"] = "manage_slots"
            st.rerun()

        if st.button("View Appointments", key="doc_appts_btn",
                     use_container_width=True):
            st.session_state["page"] = "view_appointments"
            st.rerun()

  
    # home page

    if st.session_state["page"] == "home":
        st.title("Doctor Dashboard")
        st.markdown(f"Welcome, **{st.session_state['user']['full_name']}**!")
        st.divider()


        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Slots", len(manager.slots))

        with col2:
            st.metric("Available Slots", manager.count_available_slots()) 

        with col3:
            st.metric("Total Appointments", len(manager.appointments))

    # manage slots page

    elif st.session_state["page"] == "manage_slots":
        st.title("Manage Time Slots")
        st.divider()

        tab1, tab2 = st.tabs(["View All Slots", "Add New Slot"])



        with tab1:
            if len(manager.slots) > 0:
                st.dataframe(manager.slots)
            else:
                st.warning("No time slots created yet.")

        with tab2:
            st.subheader("Add a New Time Slot")

            with st.container(border=True):
                slot_date = st.date_input("Date", key="slot_date_input")
                slot_time = st.selectbox("Time",
                    ["9:00 AM", "10:00 AM", "11:00 AM",
                     "1:00 PM", "2:00 PM", "3:00 PM",
                     "4:00 PM"], key="slot_time_input")

                if st.button("Create Slot", key="create_slot_btn",
                             type="primary", use_container_width=True):
                    with st.spinner("Creating slot..."):
                        time.sleep(2)

                        manager.create_slot(st.session_state["user"]["email"], slot_date, slot_time)
                        slot_store.save(manager.slots)
                        st.success("New time slot created!")
                        time.sleep(2)
                        st.rerun()

    # view appointments page with update

    elif st.session_state["page"] == "view_appointments":
        st.title("Patient Appointments")
        st.divider()


        if len(manager.appointments) == 0:
            st.info("No appointments booked yet.")
        else:
            col1, col2 = st.columns([3, 2])

            with col1:
                st.dataframe(manager.appointments)

            with col2:
                with st.container(border=True):
                    st.subheader("Update Status")

                    selected_appt = st.selectbox(
                        "Select Appointment",
                        options=manager.appointments,
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

                        if st.button("Update Status", type="primary",
                                     use_container_width=True,
                                     key="doc_update_btn"):
                            with st.spinner("Updating..."):
                                time.sleep(2)

                                manager.update_appointment_status(
                                    selected_appt["appointment_id"],
                                    new_status, doctor_note
                                )

                                appt_store.save(manager.appointments)


                                st.success("Status updated!")
                                time.sleep(2)
                                st.rerun()