# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import jobs  # our job-fetching module

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- Home Page ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    job_list = jobs.fetch_jobs()
    return templates.TemplateResponse("index.html", {"request": request, "jobs": job_list})

# --- Optional: API endpoint for JSON ---
@app.get("/api/jobs")
def api_jobs():
    return {"jobs": jobs.fetch_jobs()}