
# 🤖 LabBuddy – FastAPI WhatsApp Chatbot for Lab Test Booking

**LabBuddy** is an intelligent WhatsApp chatbot built with **FastAPI**, designed to help users book lab tests with national or local diagnostic labs.
It offers an intuitive conversational experience powered by the Twilio API, dynamic test/lab search, 
and step-by-step booking with secure payment handling.

---

## 💡 Features

- 🧪 Book lab tests with national or local labs
- 📍 Pincode-based lab search
- 🔍 Search by test name
- 🗂 View top 3 lab options for a given test and location
- 👤 Collect patient details and preferred schedule
- 💳 Provide a payment link for confirmation
- ✅ Confirmation message with full test details
- 🩺 Option to talk to a diagnostic expert
- 📁 User response history stored in CSV

---

## 🧠 Technologies Used

- **FastAPI** – for backend logic and routing
- **Twilio WhatsApp API** – for two-way messaging
- **httpx** – to call external lab data APIs
- **dotenv** – for managing environment variables
- **CSV** – to store user interactions

---

## 🗂 Project Structure

LabBuddy-Chatbot/
├── app/
│ ├── routes/
│ │ ├── lab_routes.py
│ │ └── test_routes.py
├── responses/ # Saved user interactions (CSV)
├── National_Lab.txt # List of national lab names
├── main.py # Main FastAPI application
├── requirements.txt
├── .gitignore
└── README.md # This file


---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/labbuddy-chatbot.git
cd labbuddy-chatbot


### 2. Create a Virtual Environment (optional but recommended)


```bash
python -m venv venv
source venv/bin/activate    # On Windows use `venv\Scripts\activate`


### 3. Install Dependencies


```bash
pip install -r requirements.txt


###4. Run the App Locally


```bash
uvicorn main:app --reload


### 5. Expose Your App with Ngrok (for Twilio webhook)


```bash
ngrok http 8000


###6. Set Webhook in Twilio
 
 Set your webhook to:
```arduino
https://<your-ngrok-url>/whatsapp


##📱 WhatsApp User Flow

Hi! 👋 Welcome to LabBuddy – your trusted partner in diagnostics.
1. 🧪 Book a Lab Test
2. 🩺 Talk to a Diagnostic Expert

→ Enter Pincode → Select Test → Get Top 3 Labs
→ Choose Lab → Enter Patient Details
→ Choose Date & Time → Make Payment → Booking Confirmed 🎉


##📝 Environment Variables

Create a .env file in the root directory to manage credentials:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+your_twilio_whatsapp_number

Note: Your app may not directly use these values unless you’re integrating outbound messages. These can be useful for future improvements.


##✅ Example Output

On WhatsApp:

🏥 Top national labs for CBC:

1. SRL Diagnostics - Sector 18, Noida
2. Thyrocare - Connaught Place, Delhi
3. Lal PathLabs - Civil Lines, Gurgaon

Reply with the lab number you would like to book.


## 💡 Why This Solution?

LabBuddy offers a practical, cost-efficient, and scalable way to digitize the diagnostic lab booking experience—right from a platform 
users already trust: WhatsApp.

✅ No app installation required – Just a simple WhatsApp message to get started.
⚡ FastAPI ensures high-performance and asynchronous handling of multiple users.
📍 Personalized lab suggestions based on location and test needs.
💬 Human-like conversation flow makes booking as easy as chatting.
💳 Payment-ready and patient-aware – Collects critical details securely and leads users to payment and confirmation.
💼 Perfect for small labs, startups, and healthcare platforms looking to digitize with minimal cost.

Whether you are a solo developer, lab operator, or startup, LabBuddy empowers you to launch a smart, reliable, and intuitive chatbot 
experience without depending on expensive enterprise platforms.
