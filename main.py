from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import jobs  # your job-fetching module
import smtplib
from email.mime.text import MIMEText
import json
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")

JOB_TITLES = [
    "software engineer intern",
    "backend engineer intern",
    "full stack engineer intern",
    "machine learning intern",
    "data engineer intern"
]

SKILLS = [
    "python","java","c++","typescript","react",
    "machine learning","tensorflow","fastapi",
    "sql","backend","api","data","ai"
]

EXCLUDE = [
    "phd","graduate level","senior","staff","principal",
    "lead","manager","director"
]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "job_titles": JOB_TITLES,
            "skills": SKILLS,
            "exclude": EXCLUDE,
            "jobs": [],
            "email_status": "",
            "selected_skills": SKILLS,
            "selected_exclude": EXCLUDE,
            "recipient_email": "",
            "selected_job_titles": JOB_TITLES
        }
    )

@app.post("/generate_email", response_class=HTMLResponse)
async def generate_email(
    request: Request,
    job_titles: str = Form(...),
    skills: str = Form(...),
    exclude: str = Form(...),
    recipient_email: str = Form(...)
):
    # Split comma-separated strings into lists
    job_titles_list = [x.strip() for x in job_titles.split(",") if x.strip()]
    skills_list = [x.strip() for x in skills.split(",") if x.strip()]
    exclude_list = [x.strip() for x in exclude.split(",") if x.strip()]

    jobs.ROLES = job_titles_list
    jobs.SKILLS = skills_list
    jobs.EXCLUDE_KEYWORDS = exclude_list

    job_list = jobs.fetch_jobs()

    content = ""
    for j in job_list:
        content += f"{j['title']} ({j['source']})\nScore: {j['score']}\n{j['link']}\n\n"

    try:
        msg = MIMEText(content)
        msg["Subject"] = "🚀 Daily AI-Curated Internships"
        msg["From"] = jobs.EMAIL
        msg["To"] = recipient_email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(jobs.EMAIL, jobs.APP_PASSWORD)
            server.send_message(msg)
        email_status = f"✅ Email sent successfully to {recipient_email}!"
    except Exception as e:
        email_status = f"❌ Email failed: {e}"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "job_titles": JOB_TITLES,
            "skills": SKILLS,
            "exclude": EXCLUDE,
            "jobs": job_list,
            "email_status": email_status,
            "selected_skills": skills_list,
            "selected_exclude": exclude_list,
            "recipient_email": recipient_email,
            "selected_job_titles": job_titles_list
        }
    )

@app.get("/all_jobs_data")
def all_jobs_data():
    try:
        with open("senn_jobs.json", "r", encoding="utf-8") as f:
            jobs_data = json.load(f)
    except FileNotFoundError:
        jobs_data = []
    return jobs_data