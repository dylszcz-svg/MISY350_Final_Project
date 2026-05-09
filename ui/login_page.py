import streamlit as st 
import time 


def render_login(manager, user_store): 
    st.title("Clinic Appointment Tracker") 
    st.caption("A scheduling portal for patients and doctors")
    st.divider() 

    # show test account
    with st.container(border=True):
        st.markdown("**Test Accounts**")
        col1,col2 = st.columns(2)
        with col1:
            st.markdown("Doctor: `doctor@clinic.com` / `doc123`") 
        with col2: 
            st.markdown("Patient: `patient@clinic.com` / `pat123`") 

    tab_login, tab_register = st.tabs(["Log In", "Create Account"])   

    with tab_login: 
        st.subheader("Log In") 
        with st.container(border=True): 
            email_input = st.text_input("Email", key="login_email", 
                                        placeholder="Enter your email") 
            password_input = st.text_input("Password", type="password", key = "login_password")

            if st.button("Log In", type = "primary", use_container_width=True, key = "login_btn"):
                if not email_input or not password_input:
                    st.warning("Please Enter Your Email and Password")
                else:
                    with st.spinner("Logging in..."):
                        time.sleep(2)

                        found_user = manager.find_user(email_input, password_input)

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
            
            if st.button("Create Account", key="register_btn", use_container_width=True):
                if not new_name or not new_email or not new_password:
                    st.warning("Please fill out all fields.")
                else:
                    with st.spinner("Creating account..."):
                        time.sleep(2)

                        if manager.email_exists(new_email):
                            st.error("This email is already registered.")
                        else:
                            manager.register_user(new_name, new_email, new_password, new_role)
                            user_store.save(manager.users)

                            st.success("Account created! You can now log in.")
                            time.sleep(2)
                            st.rerun()
