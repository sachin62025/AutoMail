# Bulk Email Sender with Streamlit

A user-friendly web application built with Python and Streamlit to send bulk emails efficiently and professionally. This tool is ideal for sending newsletters, announcements, or personalized messages to a list of recipients without needing complex software.

---

## Key Features

- **Rich Text Editor (WYSIWYG):** Compose beautiful emails with bold, italics, lists, and headings without writing any HTML.
- **Flexible Sending Modes:**
  - **Individual Mode:** Sends a separate email to each recipient, ensuring privacy (no one sees the other recipients). Includes a 1-second delay between sends.
  - **Batch Mode:** Sends a single email to all recipients (using BCC) for maximum speed.
- **Multiple Recipient Sources:**
  - Type or paste emails manually.
  - Upload a CSV file with an `Email` column.
- **File Attachments:** Easily attach files to your emails.
- **Secure Credential Management:** Uses a `.env` file to keep your sender email and password safe and out of the code.
- **Real-time Progress:** A progress bar and status updates show the sending process in real-time in Individual Mode.
- **Professional Project Structure:** The code is organized into modules for UI, core logic, and utilities, making it easy to maintain and extend.

---

## Project Structure

```
automatic-email-sender/
├── .gitignore
├── .env
├── requirements.txt
├── README.md
└── src/
    ├── app.py     
    ├── core/
    │   └── email_sender.py 
    └── utils/
        └── recipient_parser.py 
```

---

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

- Python 3.8 or higher
- Git

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/automatic-email-sender.git
cd automatic-email-sender
```

### 3. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

- **On Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 4. Install Dependencies

Install all the required libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Configure Your Credentials

The application uses a `.env` file to handle sensitive credentials securely.

1. Create a new file named `.env` in the root directory of the project.
2. Copy the content from the example below and paste it into your `.env` file.

   ```env
   SENDER_EMAIL="your_email@gmail.com"
   SENDER_PASSWORD="your-16-character-app-password"
   ```
3. Replace the placeholder values with your sender's Gmail address and the **16-character App Password**.

   > **Important:** You **cannot** use your regular Gmail password if you have 2-Factor Authentication (2FA) enabled. See the section below on how to generate an App Password.
   >

---

## How to Run the Application

```bash
streamlit run src/app.py
```

Your web browser will automatically open a new tab with the application running.

---

## How to Generate a Gmail App Password

To send emails programmatically from a Gmail account with 2FA enabled, you must use an App Password.

1. Go to your Google Account settings: [https://myaccount.google.com/](https://myaccount.google.com/)
2. Navigate to the **Security** tab on the left.
3. Ensure that **2-Step Verification** is turned **ON**. You cannot create App Passwords without it.
4. On the same page, click on **App passwords**.
5. You might be asked to sign in again for security.
6. Under "Select app," choose **Mail**.
7. Under "Select device," choose **Other (Custom name)** and give it a descriptive name like "Streamlit Bulk Sender".
8. Click **Generate**.
9. A 16-character password will be displayed in a yellow box. **Copy this password.** This is what you will paste into your `.env` file for the `SENDER_PASSWORD` variable.
