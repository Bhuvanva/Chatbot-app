import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, Request, Form
from starlette.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

router = APIRouter()

session = {} 

national_lab_names = set()

try:
    with open("National_Lab.txt", "r", encoding="utf-8") as file:
        national_lab_names = set(line.strip().lower() for line in file if line.strip())
except FileNotFoundError:
    print("⚠️ National_Lab.txt not found. National lab filtering will be skipped.")

        
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
                "Address", "PreferredDate",
                "PreferredTime",
                "PaymentStatus", "BookingStatus"            
            ])
        writer.writerow([
            datetime.now().isoformat(), phone, step, user_message,
            pincode, test_name, lab_name,
            patient_name, patient_age, patient_gender,
            adress, preferred_date, preferred_time,
            payment_status, booking_status            
        ])


@router.post("/whatsapp")

async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form("")
):

    print("Incoming WhatsApp message!")   
    msg = Body.strip().lower()
    user_number = From.strip()
    response = MessagingResponse()
    reply = response.message()

            
    if not user_number.startswith("whatsapp:"):
        user_number = f"whatsapp:{user_number}"

# Check for new/expired session
    current_time = datetime.now().timestamp()
    if user_number not in session or current_time - session[user_number].get("timestamp", 0) > 1800:
        session[user_number] = {
            "step": "start",
            "timestamp": current_time
        }
    else:
        session[user_number]["timestamp"] = current_time

    state = session[user_number]

        # Trigger starting message if it's a new session
    if state["step"] == "start":
        state["step"] = "main_menu"  
        log_user_state(From, Body, state)
        reply.body(
            "Hi! 👋 Welcome to LabBuddy – your trusted partner in diagnostics.\n"
            "I'm Buddy, your smart lab assistant.\n"
            "How can I assist you today?\n\n"
            "To continue, select:\n"
            "1.  Book a Lab Test\n"
            "2.  Talk to a Diagnostic Expert\n"
        )
        state["step"] = "main_menu"
    
    elif msg.strip().lower() == "restart":
        reply.body(
            "Hi! 👋 Welcome to LabBuddy – your trusted partner in diagnostics.\n"
            "I'm Buddy, your smart lab assistant.\n"
            "How can I assist you today?\n\n"
            "To continue, select:\n"
            "1.  Book a Lab Test\n"
            "2.  Talk to a Diagnostic Expert\n"
            "👉 Please reply with 1 or 2."
        )
        log_user_state(From, Body, state)
        state["step"] = "main_menu"

    elif state["step"] == "main_menu":
        if msg == "1":
            reply.body(
                "Let’s get your test booked.\n"
                "How would you like to proceed?\n"
                "1.  Book with National Labs\n"
                "2.  Book with Local Labs near me\n"
                "3.  Search by Test Name"
            )
            state["step"] = "book_menu"
        elif msg == "2":
            reply.body("Our expert will help you understand your tests and guide you accordingly with care and clarity.\n"
                        "Please keep your medical report or prescription ready as we connect you with your diagnostic expert.")
            state["step"] = "thank_you"       
            
        else:
            reply.body("❗ Please reply with 1 or 2.")
        log_user_state(From, Body, state)

    elif state["step"] == "thank_you":
        reply.body("Thank you for trusting LabBuddy.\n"
                "We're always here to support your health journey.\n"
                "If you have more questions or need assistance, say, 'Hi' to connect with our 24*7 customer support team.\n"
                "Have a healthy day!")
        state["step"] = "end"
        log_user_state(From, Body, state)


    elif state["step"] == "book_menu":
        if msg == "1":
            state["lab_type"] = "national"
            reply.body("Kindly provide your PIN code to find national labs near you.")
            state["step"] = "get_n_pincode"
        elif msg == "2":
            state["lab_type"] = "local"
            reply.body("Kindly provide your PIN code to find local labs near you.")
            state["step"] = "get_l_pincode"
        elif msg == "3":
            state["lab_type"] = "both"
            reply.body("Please specify the test you wish to book.\n"
                    "e.g., CBC, Thyroid Panel, etc.")
            state["step"] = "get_b_pincode"
        else:
            reply.body("❗ Please reply with 1, 2, or 3.")
        
        log_user_state(From, Body, state)
    
    elif state["step"] == "get_n_pincode":
        state["pincode"] = msg
        reply.body("Please specify the test you wish to book.\n"
                    "e.g., CBC, Thyroid Panel, etc.")
        state["step"] = "get_n_test"
        
        log_user_state(From, Body, state)


    elif state["step"] == "get_n_test":
        state["test_name"] = msg.upper()
        reply.body("Select collection type:\n"
                    "1. Home Collection\n"
                    "2. Centre Visit")
        state["step"] = "get_n_collection_type"
        
        log_user_state(From, Body, state)
    
    elif state["step"] == "get_n_collection_type":
        state["Collection_Type"] = msg.strip()
        if msg == "1":
            state[""] = msg.upper()
            try:
                async with httpx.AsyncClient() as client:
                    api_url = f"http://localhost:8000/api/v1/labs/nearby-labs/{state['pincode']}?test_name={state['test_name']}"
                    res = await client.get(api_url)
                    if res.status_code == 200:
                        labs = res.json()
                    # ✅ Filter for national labs only
                        labs = [
                            lab for lab in labs
                            if lab.get("lab_name", "").strip().lower() in national_lab_names
                        ]
                        top_labs = labs[:3]

                        if top_labs:
                            lab_list = ""
                            for idx, lab in enumerate(top_labs, 1):
                                lab_list += f"{idx}. {lab['lab_name']} - {lab['address']}, {lab['city']}\n"

                            reply.body(
                                f"Here are the labs for *{state['test_name']}*:\n\n{lab_list}"
                                "\nPlease enter the number of your selected option (e.g., 1)"
                            )
                            state["labs"] = top_labs
                            state["step"] = "choose_lab"
                        else:
                            reply.body("No national labs found for that test and PIN.\n"
                                    "👉 To go back to the previous menu, type *0*.")
                            state["step"] = "back_to_menu_wait"
                    else:
                        reply.body("Error fetching labs. Please type 'Restart' to start again.")
                        state["step"] = "get_n_test"
            except Exception as e:
                reply.body(f"Something went wrong: {str(e)}")
                state["step"] = "get_n_test"    
                

        elif msg == "2":
            state["Collection_Type"] = msg.strip()
            state[""] = msg.upper()
            try:
                async with httpx.AsyncClient() as client:
                    api_url = f"http://localhost:8000/api/v1/labs/nearby-labs/{state['pincode']}?test_name={state['test_name']}"
                    res = await client.get(api_url)
                    if res.status_code == 200:
                        labs = res.json()
                    # ✅ Filter for national labs only
                        labs = [
                            lab for lab in labs
                            if lab.get("lab_name", "").strip().lower() in national_lab_names
                        ]
                        top_labs = labs[:3]

                        if top_labs:
                            lab_list = ""
                            for idx, lab in enumerate(top_labs, 1):
                                lab_list += f"{idx}. {lab['lab_name']} - {lab['address']}, {lab['city']}\n"

                            reply.body(
                                f"Here are the labs for *{state['test_name']}*:\n\n{lab_list}"
                                "\nPlease enter the number of your selected option (e.g., 1)"
                            )
                            state["labs"] = top_labs
                            state["step"] = "choose_lab"
                        else:
                            reply.body("No national labs found for that test and PIN.\n"
                                    "👉 To go back to the previous menu, type *0*.")
                            state["step"] = "back_to_menu_wait"
                    else:
                        reply.body("Error fetching labs. Please try again later.")
                        state["step"] = "get_n_test"
            except Exception as e:
                reply.body(f"Something went wrong: {str(e)}")
                state["step"] = "get_n_test"  
                 
        log_user_state(From, Body, state)
                           
    elif state["step"] == "back_to_menu_wait":
        if msg.strip().lower() == "0":
            reply.body(
                "Let’s get your test booked.\n"
                "How would you like to proceed?\n"
                "1.  Book with National Labs\n"
                "2.  Book with Local Labs near me\n"
                "3.  Search by Test Name"
            )
            state["step"] = "book_menu"
        else:
            reply.body("Please type *0* to return to the previous menu.")
            
        log_user_state(From, Body, state)

    elif state["step"] == "get_l_pincode":
        state["pincode"] = msg
        reply.body("Please specify the test you wish to book.\n"
                    "e.g., CBC, Thyroid Panel, etc.")
        state["step"] = "get_l_test"
        
        log_user_state(From, Body, state)

    elif state["step"] == "get_l_test":
        state["test_name"] = msg.upper()
        reply.body("Select collection type:\n"
                    "1. Home Collection\n"
                    "2. Centre Visit")
        state["step"] = "get_l_collection_type"
        
        log_user_state(From, Body, state)
    
    elif state["step"] == "get_l_collection_type":
        state["Collection_Type"] = msg.strip()
        if msg == "1":
            state[""] = msg.upper()
            try:
                async with httpx.AsyncClient() as client:
                    api_url = f"http://localhost:8000/api/v1/labs/nearby-labs/{state['pincode']}?test_name={state['test_name']}"
                    res = await client.get(api_url)
                    if res.status_code == 200:
                        labs = res.json()
                        # ✅ Filter for local labs (exclude national)
                        labs = [
                            lab for lab in labs
                            if lab.get("lab_name", "").strip().lower() not in national_lab_names
                        ]
                        top_labs = labs[:3]

                        if top_labs:
                            lab_list = ""
                            for idx, lab in enumerate(top_labs, 1):
                                lab_list += f"{idx}. {lab['lab_name']} - {lab['address']}, {lab['city']}\n"

                            reply.body(
                                f"Here are the labs for *{state['test_name']}*:\n\n{lab_list}"
                                "\nPlease enter the number of your selected option (e.g., 1)"
                            )
                            state["labs"] = top_labs
                            state["step"] = "choose_lab"
                        else:
                            reply.body("No local labs found for that test and PIN.\n"
                                    "👉 To go back to the previous menu, type *0*.")
                            state["step"] = "back_to_menu_wait"
                    else:
                        reply.body("Error fetching labs. Please type 'Restart' to start again.")
                        state["step"] = "get_l_test"
            except Exception as e:
                reply.body(f"Error occurred: {str(e)}")
                state["step"] = "get_l_test"
            
            log_user_state(From, Body, state)
            
        elif msg == "2":
            state["Collection_Type"] = msg.strip()
            state[""] = msg.upper()
            try:
                async with httpx.AsyncClient() as client:
                    api_url = f"http://localhost:8000/api/v1/labs/nearby-labs/{state['pincode']}?test_name={state['test_name']}"
                    res = await client.get(api_url)
                    if res.status_code == 200:
                        labs = res.json()
                        # ✅ Filter for local labs (exclude national)
                        labs = [
                            lab for lab in labs
                            if lab.get("lab_name", "").strip().lower() not in national_lab_names
                        ]
                        top_labs = labs[:3]

                        if top_labs:
                            lab_list = ""
                            for idx, lab in enumerate(top_labs, 1):
                                lab_list += f"{idx}. {lab['lab_name']} - {lab['address']}, {lab['city']}\n"

                            reply.body(
                                f"Here are the labs for *{state['test_name']}*:\n\n{lab_list}"
                                "\nPlease enter the number of your selected option (e.g., 1)"
                            )
                            state["labs"] = top_labs
                            state["step"] = "choose_lab"
                        else:
                            reply.body("No local labs found for that test and PIN.\n"
                                    "👉 To go back to the previous menu, type *0*.")
                            state["step"] = "back_to_menu_wait"
                    else:
                        reply.body("Error fetching labs. Please type 'Restart' to start again.")
                        state["step"] = "get_l_test"
            except Exception as e:
                reply.body(f"Error occurred: {str(e)}")
                state["step"] = "get_l_test"
            
            log_user_state(From, Body, state)


    elif state["step"] == "get_b_pincode":
        state["test_name"] = msg.upper()
        reply.body("Kindly provide your PIN code to find the labs near you.")
        state["step"] = "get_b_test"
        
        log_user_state(From, Body, state)


    elif state["step"] == "get_b_test":
        state["pincode"] = msg.strip()
        reply.body("Select collection type:\n"
                    "1. Home Collection\n"
                    "2. Centre Visit")
        state["step"] = "get_b_collection_type"
        
        log_user_state(From, Body, state)
        
    elif state["step"] == "get_b_collection_type":
        state["Collection_Type"] = msg.strip()
        if msg == "1":
            state[""] = msg.upper()
            try:
                async with httpx.AsyncClient() as client:
                    api_url = f"http://localhost:8000/api/v1/labs/nearby-labs/{state['pincode']}?test_name={state['test_name']}"
                    res = await client.get(api_url)
                    if res.status_code == 200:
                        labs = res.json()
                        top_labs = labs[:3]

                        if top_labs:
                            lab_list = ""
                            for idx, lab in enumerate(top_labs, 1):
                                lab_list += f"{idx}. {lab['lab_name']} - {lab['address']}, {lab['city']}\n"

                            reply.body(
                                f"Here are the labs for *{state['test_name']}*:\n\n{lab_list}"
                                "\nPlease enter the number of your selected option (e.g., 1)"
                            )
                            state["labs"] = top_labs
                            state["step"] = "choose_lab"
                        else:
                            reply.body("No labs found for your test and PIN.\n"
                                    "👉 To go back to the previous menu, type *0*.")
                            state["step"] = "back_to_menu_wait"
                    else:
                        reply.body("Error fetching labs. Please type 'Restart' to start again.")
                        state["step"] = "get_b_test"
            except Exception as e:
                reply.body(f"Something went wrong: {str(e)}")
                state["step"] = "get_b_test"
            
        elif msg == "2":
            state["Collection_Type"] = msg.strip()
            state[""] = msg.upper()
            try:
                async with httpx.AsyncClient() as client:
                    api_url = f"http://localhost:8000/api/v1/labs/nearby-labs/{state['pincode']}?test_name={state['test_name']}"
                    res = await client.get(api_url)
                    if res.status_code == 200:
                        labs = res.json()
                        top_labs = labs[:3]

                        if top_labs:
                            lab_list = ""
                            for idx, lab in enumerate(top_labs, 1):
                                lab_list += f"{idx}. {lab['lab_name']} - {lab['address']}, {lab['city']}\n"

                            reply.body(
                                f"Here are the labs for *{state['test_name']}*:\n\n{lab_list}"
                                "\nPlease enter the number of your selected option (e.g., 1)"
                            )
                            state["labs"] = top_labs
                            state["step"] = "choose_lab"
                        else:
                            reply.body("No labs found for your test and PIN.\n"
                                    "👉 To go back to the previous menu, type *0*.")
                            state["step"] = "back_to_menu_wait"
                    else:
                        reply.body("Error fetching labs. Please type 'Restart' to start again.")
                        state["step"] = "get_b_test"
            except Exception as e:
                reply.body(f"Something went wrong: {str(e)}")
                state["step"] = "get_b_test"
            
            log_user_state(From, Body, state)

        
    elif state["step"] == "choose_lab":
        try:
            lab_idx = int(msg) - 1
            selected_lab = state["labs"][lab_idx]
            state["lab"] = selected_lab["lab_name"]
            reply.body("Kindly provide the patient's *name* to continue with the booking:")
            state["step"] = "get_patient_name"
        except (ValueError, IndexError):
            reply.body("Invalid selection. Please reply with the number of the lab you want to book.")
            
        log_user_state(From, Body, state)

    elif state["step"] == "get_patient_name":
        state["patient_name"] = msg.strip()
        reply.body("Kindly enter the *age*:")
        state["step"] = "get_patient_age"
        
        log_user_state(From, Body, state)

    elif state["step"] == "get_patient_age":
        state["patient_age"] = msg.strip()
        reply.body("Please specify *gender* (Male/ Female/ Other):")
        state["step"] = "get_patient_gender"
        
        log_user_state(From, Body, state)

    # Replace this with your actual next step
    

    elif state["step"] == "get_patient_gender":
        state["patient_gender"] = msg.strip()

        # Generate date options in both cases
        today = datetime.today()
        dates = [(today + timedelta(days=i)).strftime("%d/%m/%Y") for i in range(1, 4)]
        state["date_options"] = dates

        if state.get("Collection_Type") == "1":
            # Home Collection → Ask for address first
            reply.body("Please provide your complete address.")
            state["step"] = "address"

        elif state.get("Collection_Type") == "2":
            # Centre Visit → Skip address, go straight to date selection
            reply.body("Please choose a preferred date for your test:\n"
                    f"1. {dates[0]}\n"
                    f"2. {dates[1]}\n"
                    f"3. {dates[2]}\n\n"
                    "Reply with the option number (1, 2 or 3)")
            state["step"] = "date"
            
        log_user_state(From, Body, state)

              
    elif state["step"] == "address":
        state["address"] = msg.strip()
        dates = state["date_options"]

        reply.body("Please choose a preferred date for your test:\n"
                    f"1. {dates[0]}\n"
                    f"2. {dates[1]}\n"
                    f"3. {dates[2]}\n\n"
                    "Reply with the option number (1, 2 or 3)")
        state["step"] = "date"
        
        log_user_state(From, Body, state)

 
    elif state["step"] == "date":
        if msg.strip() in ["1", "2", "3"]:
            selected_date = state["date_options"][int(msg) - 1]
            state["date"] = selected_date
            state["step"] = "time"
    
            reply.body("Please choose a preferred time slot:\n"
                        "1. Morning Slot (9 AM - 12 PM)\n"
                        "2. Afternoon Slot (12 PM - 3 PM)\n"
                        "3. Evening Slot (3 PM - 6 PM)\n\n"
                        "Reply with 1, 2 or 3")
        else:
            reply.body("Please reply with 1, 2 or 3 to select a valid date.")
            
        log_user_state(From, Body, state)
    
    elif state["step"] == "time":
        time_slots = {
            "1": "Morning Slot (9 AM - 12 PM)",
            "2": "Afternoon Slot (12 PM - 3 PM)",
            "3": "Evening Slot (3 PM - 6 PM)"
        }

        if msg.strip() in time_slots:
            state["time"] = time_slots[msg.strip()]
            state["step"] = "schedule"
            reply.body("To confirm your booking, please complete the payment using the link below:\n"
                    "[Secure Payment Link] 🔒\n"
                    "Once payment is successful, you’ll receive your confirmation.")
            state["step"] = "confirmation"
        else:
            reply.body("Please reply with 1, 2 or 3 to choose a valid time slot.")
            
        log_user_state(From, Body, state)


    elif state["step"] == "confirmation":
        reply.body(
            f"{state.get('patient_name').title()}, Your Booking is Confirmed!\n\n"
            f"Lab: {state.get('lab').title()}\n"
            f"Test: {state.get('test_name').upper()}\n"
            f"Patient: {state.get('patient_name').title()}\n"
            f"Date & Time: {state['date']} {state['time']}\n\n"
            f"- 📚 Test Guide:\n"
            "• Fasting required\n"
            "• Fasting time\n"
            "• Description\n\n"
            "Thank you for trusting LabBuddy.\n"
                "We’re always here to support your health journey.\n"
                "If you have more questions or need assistance, just say Hi anytime.\n"
                "Have a healthy day! "
        )
        state["step"]= "end"
        
        log_user_state(From, Body, state)

    
    elif state["step"] == "end":
        reply.body("Thank you for connecting with us!\n\n"
                "You can type *Hi* anytime to start over.")
        state.clear()
        state["step"]="start"  # Reset the conversation state
        
        log_user_state(From, Body, state)

             
    else:
        reply.body("⚠️ Something went wrong. Please type 'Restart' to restart.")
        state.clear()
        state["step"]="start"
        
        log_user_state(From, Body, state)




    session[user_number] = state
      # Now it contains parsed data

  
    
    return Response(content=str(response), media_type="application/xml")
