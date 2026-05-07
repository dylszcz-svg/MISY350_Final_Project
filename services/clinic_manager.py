import uuid
 
 
class ClinicManager:
    def __init__(self, users, slots, appointments):
        self.users = users
        self.slots = slots
        self.appointments = appointments
 
    # user methods
    def find_user(self, email, password):
        for user in self.users:
            if user["email"].strip().lower() == email.strip().lower() and user["password"] == password:
                return user
        return None
 
    def email_exists(self, email):
        for user in self.users:
            if user["email"].strip().lower() == email.strip().lower():
                return True
        return False
 
    def register_user(self, name, email, password, role):
        new_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "full_name": name,
            "password": password,
            "role": role
        }
        self.users.append(new_user)
        return new_user
 
    # --- slot methods ---
    def create_slot(self, doctor_email, date, time_str):
        new_slot_id = "SLOT" + str(len(self.slots) + 1)
        new_slot = {
            "slot_id": new_slot_id,
            "doctor_email": doctor_email,
            "date": str(date),
            "time": time_str,
            "status": "Available"
        }
        self.slots.append(new_slot)
        return new_slot
 
    def get_available_slots(self):
        available = []
        for slot in self.slots:
            if slot["status"] == "Available":
                available.append(slot)
        return available
 
    def count_available_slots(self):
        count = 0
        for slot in self.slots:
            if slot["status"] == "Available":
                count += 1
        return count
 
    # --- appointment methods ---
    def book_appointment(self, slot_id, patient_email, patient_name, notes):
        selected_slot = None
        for slot in self.slots:
            if slot["slot_id"] == slot_id:
                selected_slot = slot
                break
 
        if not selected_slot:
            return None
 
        new_appt = {
            "appointment_id": "APT-" + str(uuid.uuid4())[:8],
            "slot_id": slot_id,
            "patient_email": patient_email,
            "patient_name": patient_name,
            "date": selected_slot["date"],
            "time": selected_slot["time"],
            "status": "Booked",
            "notes": notes
        }
        self.appointments.append(new_appt)
        selected_slot["status"] = "Booked"
        return new_appt
 
    def get_patient_appointments(self, patient_email):
        my_appts = []
        for appt in self.appointments:
            if appt["patient_email"] == patient_email:
                my_appts.append(appt)
        return my_appts
 
    def get_booked_appointments(self, patient_email):
        booked = []
        for appt in self.appointments:
            if appt["patient_email"] == patient_email and appt["status"] == "Booked":
                booked.append(appt)
        return booked
 
    def update_appointment_status(self, appointment_id, new_status, notes):
        for appt in self.appointments:
            if appt["appointment_id"] == appointment_id:
                appt["status"] = new_status
                appt["notes"] = notes
                return True
        return False
 
    def cancel_appointment(self, appointment_id):
        for appt in self.appointments:
            if appt["appointment_id"] == appointment_id:
                appt["status"] = "Cancelled"
                for slot in self.slots:
                    if slot["slot_id"] == appt["slot_id"]:
                        slot["status"] = "Available"
                        break
                return True
        return False
