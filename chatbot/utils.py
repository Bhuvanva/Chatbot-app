import os
import csv
from datetime import datetime

def save_user_data(
    phone_raw,
    step,
    user_message,
    pincode="",
    test_name="",
    lab_name="",
    patient_name="",
    patient_age="",
    patient_gender="",
    adress="",
    preferred_date="",
    preferred_time="",
    payment_status="",
    booking_status=""
):
    phone = phone_raw.replace("whatsapp:", "").replace("+", "")
    file_name = os.path.join("responses", f"user_responses_{phone}.csv")

    os.makedirs("responses", exist_ok=True)
    is_new_file = not os.path.exists(file_name)

    with open(file_name, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow([
                "Timestamp", "Phone", "Step", "UserMessage",
                "Pincode", "TestName", "LabName",
                "PatientName", "Age", "Gender",
                "Address", "PreferredDate", "PreferredTime",
                "PaymentStatus", "BookingStatus"
            ])
        writer.writerow([
            datetime.now().isoformat(), phone_raw, step, user_message,
            pincode, test_name, lab_name,
            patient_name, patient_age, patient_gender,
            adress, preferred_date, preferred_time,
            payment_status, booking_status
        ])

def log_user_state(phone, body, state):
    save_user_data(
        phone_raw=phone,
        step=state.get("step", ""),
        user_message=body,
        pincode=state.get("pincode", ""),
        test_name=state.get("test_name", ""),
        lab_name=state.get("lab", ""),
        patient_name=state.get("patient_name", ""),
        patient_age=state.get("patient_age", ""),
        patient_gender=state.get("patient_gender", ""),
        adress=state.get("address", ""),
        preferred_date=state.get("date", ""),
        preferred_time=state.get("time", ""),
        payment_status="Unpaid",
        booking_status="Pending",
    )
