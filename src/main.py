import os
import uuid
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import json
import pypdf

from src.core.email_sender import EmailSender
from src.core.ai_generator import GeminiEmailGenerator
from src.utils.recipient_parser import parse_from_text, parse_from_csv

load_dotenv()

app = FastAPI(title="Auto-Mail API")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# In-memory store for task progress
# Format: {task_id: {"status": "running"|"completed"|"failed", "sent": 0, "total": 0, "message": ""}}
task_progress: Dict[str, Dict] = {}

# Models
class AIRequest(BaseModel):
    prompt: str

# Initialize AI Generator
try:
    ai_generator = GeminiEmailGenerator()
except Exception as e:
    print(f"Warning: AI Generator could not be initialized: {e}")
    ai_generator = None

@app.get("/")
async def read_root():
    return FileResponse("src/static/index.html")

@app.post("/api/generate-email")
async def generate_email(
    prompt: str = Form(...),
    resume: Optional[UploadFile] = File(None)
):
    if not ai_generator:
        raise HTTPException(status_code=500, detail="AI Generator is not initialized. Check API Key.")
    
    context_text = ""
    if resume:
        try:
            if resume.filename.endswith(".pdf"):
                reader = pypdf.PdfReader(resume.file)
                for page in reader.pages:
                    context_text += page.extract_text() + "\n"
            elif resume.filename.endswith(".txt"):
                content = await resume.read()
                context_text = content.decode("utf-8")
            else:
                # Try to read as text for other formats or just ignore
                pass
        except Exception as e:
            print(f"Error reading resume: {e}")
            # Continue without context if reading fails
            pass

    try:
        email_content = ai_generator.generate_email(prompt, context_text)
        return email_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-csv")
async def parse_csv_endpoint(file: UploadFile = File(...)):
    try:
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        with open(temp_filename, "r") as f:
             import pandas as pd
             df = pd.read_csv(temp_filename)
             if 'Email' not in df.columns:
                 cols = [c.lower() for c in df.columns]
                 if 'email' in cols:
                     email_col = df.columns[cols.index('email')]
                     emails = df[email_col].dropna().unique().tolist()
                 else:
                     raise ValueError("CSV must have an 'Email' column")
             else:
                 emails = df['Email'].dropna().unique().tolist()
        
        os.remove(temp_filename)
        return {"recipients": emails, "count": len(emails)}
        
    except Exception as e:
        if os.path.exists(f"temp_{file.filename}"):
             os.remove(f"temp_{file.filename}")
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

@app.post("/api/send-email")
async def send_email_endpoint(
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    recipients: str = Form(...), # JSON string of list
    subject: str = Form(...),
    body: str = Form(...),
    sending_mode: str = Form(...),
    attachment: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None
):
    try:
        recipient_list = json.loads(recipients)
        
        email_sender = EmailSender(sender_email, sender_password)
        
        attachment_path = None
        if attachment:
            attachment_path = os.path.join(os.getcwd(), attachment.filename)
            with open(attachment_path, "wb") as f:
                content = await attachment.read()
                f.write(content)
        
        task_id = str(uuid.uuid4())
        task_progress[task_id] = {
            "status": "running",
            "sent": 0,
            "total": len(recipient_list),
            "message": "Starting..."
        }

        if sending_mode == "batch":
            # Batch is fast, but we can still wrap it to be consistent
            background_tasks.add_task(process_batch_email, task_id, email_sender, recipient_list, subject, body, attachment_path)
        else:
            background_tasks.add_task(process_individual_emails, task_id, email_sender, recipient_list, subject, body, attachment_path)
            
        return {"task_id": task_id, "message": "Email sending started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_progress[task_id]

def process_batch_email(task_id, sender, recipients, subject, body, attachment_path):
    try:
        sender.send_batch_email(recipients, subject, body, attachment_path)
        task_progress[task_id]["status"] = "completed"
        task_progress[task_id]["sent"] = len(recipients)
        task_progress[task_id]["message"] = "Batch email sent successfully!"
    except Exception as e:
        task_progress[task_id]["status"] = "failed"
        task_progress[task_id]["message"] = str(e)
    finally:
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)

def process_individual_emails(task_id, sender, recipients, subject, body, attachment_path):
    try:
        total = len(recipients)
        for i, recipient in enumerate(recipients):
            # Update progress
            task_progress[task_id]["sent"] = i
            task_progress[task_id]["message"] = f"Sending to {recipient}..."
            
            # We need to modify send_individual_emails to NOT loop internally if we want granular control here,
            # OR we pass a callback. The existing class has a callback! Perfect.
            # But wait, the existing class loops. 
            # Let's use the existing class's callback to update our store.
            pass # Logic moved below
        
        def progress_callback(index, total, current_recipient):
            task_progress[task_id]["sent"] = index + 1
            task_progress[task_id]["message"] = f"Sent to {current_recipient}"

        sender.send_individual_emails(recipients, subject, body, attachment_path, progress_callback=progress_callback)
        
        task_progress[task_id]["status"] = "completed"
        task_progress[task_id]["message"] = "All emails sent successfully!"
        
    except Exception as e:
        task_progress[task_id]["status"] = "failed"
        task_progress[task_id]["message"] = str(e)
    finally:
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
