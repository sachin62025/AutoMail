# src/core/email_sender.py

import yagmail
import time
from typing import List, Callable

class EmailSender:
    def __init__(self, sender_email: str, sender_password: str):
        if not sender_email or not sender_password:
            raise ValueError("Sender email and password must be provided.")
        
        try:
            self.yag = yagmail.SMTP(sender_email, sender_password)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SMTP server. Check your credentials. Error: {e}")

    def send_batch_email(self, recipients: List[str], subject: str, body: str, attachment_path: str = None):
        try:
            self.yag.send(
                to=recipients,
                subject=subject,
                contents=body,
                attachments=attachment_path
            )
        except Exception as e:
            raise RuntimeError(f"An error occurred while sending the batch email: {e}")

    def send_individual_emails(
        self, 
        recipients: List[str], 
        subject: str, 
        body: str, 
        attachment_path: str = None,
        progress_callback: Callable = None
    ):
        total_recipients = len(recipients)
        for i, recipient in enumerate(recipients):
            try:
                if progress_callback:
                    progress_callback(i, total_recipients, recipient)

                self.yag.send(
                    to=recipient,
                    subject=subject,
                    contents=body,
                    attachments=attachment_path
                )
                
                if i < total_recipients - 1:
                    time.sleep(1)

            except Exception as e:
                raise RuntimeError(f"Failed to send email to {recipient}. Error: {e}")

