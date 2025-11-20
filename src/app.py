# src/app.py

import streamlit as st
import os
from dotenv import load_dotenv
from core.email_sender import EmailSender
from utils.recipient_parser import parse_from_text, parse_from_csv
from streamlit_quill import st_quill
load_dotenv()

st.set_page_config(page_title="Bulk Email Sender", layout="centered")
st.title(" Bulk Email Sender")

st.sidebar.header("Sender Credentials")
default_email = os.getenv("SENDER_EMAIL", "")
default_password = os.getenv("SENDER_PASSWORD", "")

sender_email = st.sidebar.text_input("Sender Email", value=default_email)
sender_password = st.sidebar.text_input("App Password", type="password", value=default_password)

# --- UI for Recipients ---
st.header("Add Recipients")
recipient_option = st.radio(
    "How to provide recipient emails?",
    ("Type manually", "Upload a CSV file"),
    horizontal=True
)

recipients = []
if recipient_option == "Type manually":
    recipient_text = st.text_area("Enter emails (comma-separated)")
    recipients = parse_from_text(recipient_text)
else:
    uploaded_file = st.file_uploader("Choose a CSV file (must have an 'Email' column)")
    if uploaded_file:
        try:
            recipients = parse_from_csv(uploaded_file)
            st.success(f"Loaded {len(recipients)} emails from {uploaded_file.name}")
        except ValueError as e:
            st.error(e)

if recipients:
    st.write(f"**Total Recipients:** {len(recipients)}")
    with st.expander("Show Recipients"):
        st.write(recipients)

# --- UI for Email Content ---
st.header("Compose Your Email")
email_subject = st.text_input("Subject")
# email_body = st.text_area("Email Body (HTML is supported)", height=300)
st.write("Email Body")
email_body = st_quill(
    placeholder="Compose your email here...",
    html=True,  
    toolbar=[
        ['bold', 'italic', 'underline', 'strike'],
        [{'header': '1'}, {'header': '2'}],
        [{'list': 'ordered'}, {'list': 'bullet'}],
        ['link', 'image'],
        ['clean']
    ],
    key="quill_editor"
)
attachment = st.file_uploader("Attach a file (Optional)")

# --- UI for Sending Email ---
st.header("Send It!")
sending_mode = st.radio(
    "Select Sending Mode",
    ("Individual Mode", "Batch Mode (sends one email to all, fast)"),
    index=0, 
    help="Individual Mode is more professional. Batch mode sends a single email with all recipients hidden (BCC)."
)

if st.button("SEND EMAILS", use_container_width=True):
    if not sender_email or not sender_password:
        st.error("Sender credentials are required.")
    elif not recipients:
        st.warning("No recipients have been added.")
    elif not email_subject:
        st.warning("Email subject is empty.")
    else:
        try:
            # Initialize the sender (outside the conditional logic)
            email_sender = EmailSender(sender_email, sender_password)
            attachment_path = None
            if attachment:
                attachment_path = os.path.join(os.getcwd(), attachment.name)
                with open(attachment_path, "wb") as f:
                    f.write(attachment.getbuffer())

            # --- Conditional logic based on sending mode ---
            if sending_mode.startswith("Individual"):
                # --- INDIVIDUAL MODE LOGIC ---
                st.info("Sending emails in Individual Mode...")
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(index, total, current_recipient):
                    progress = (index + 1) / total
                    progress_bar.progress(progress)
                    status_text.info(f"Sending email {index + 1}/{total} to: {current_recipient}")

                email_sender.send_individual_emails(
                    recipients, email_subject, email_body, attachment_path, progress_callback=update_progress
                )
                status_text.empty()
                progress_bar.empty()
                st.success("✅ All emails have been sent successfully!")

            else:
                # --- BATCH MODE LOGIC ---
                with st.spinner(f"Sending one email to all {len(recipients)} recipients in Batch Mode..."):
                    email_sender.send_batch_email(
                        recipients, email_subject, email_body, attachment_path
                    )
                st.success("✅ Batch email sent successfully!")

            # Clean up attachment if it exists
            if attachment_path:
                os.remove(attachment_path)

        except (ValueError, ConnectionError, RuntimeError) as e:
            st.error(f"An error occurred: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


