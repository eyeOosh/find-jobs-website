# jobs.py
from dotenv import load_dotenv
import os, feedparser, requests, json
from bs4 import BeautifulSoup

load_dotenv()

EMAIL = os.environ.get("EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")

LOCATIONS = ["San Jose, CA", "Austin, TX", "Remote"]
ROLES = [
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

EXCLUDE_KEYWORDS = [
    "phd", "ph.d", "doctorate","postdoctoral","postdoc",
    "graduate level","graduate-level","master's","masters","ms degree","m.s.","pursuing a master's",
    "pursuing graduate","senior","staff","principal","lead","manager","director",
    "5+ years","7+ years","10+ years","experienced hire"
]

SEEN_FILE = "seen_jobs.json"

# Load seen jobs
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_jobs = set(json.load(f))
else:
    seen_jobs = set()

def is_relevant(text):
    text = text.lower()
    for word in EXCLUDE_KEYWORDS:
        if word in text:
            return False
    if "intern" not in text and "new grad" not in text:
        return False
    return True

def score_job(text):
    text = text.lower()
    score = 0
    for skill in SKILLS:
        if skill in text:
            score += 2
    if "intern" in text:
        score += 5
    if "new grad" in text:
        score += 3
    if "undergraduate" in text:
        score += 3
    if "bachelor" in text:
        score += 2
    return score

def fetch_jobs():
    jobs = []
    # --- Indeed ---
    for role in ROLES:
        for loc in LOCATIONS:
            url = f"https://www.indeed.com/rss?q={role.replace(' ','+')}&l={loc.replace(' ','+')}"
            feed = feedparser.parse(url)
            for entry in feed.entries:
                link = entry.link
                if link in seen_jobs:
                    continue
                text = entry.title + " " + entry.summary
                if not is_relevant(text):
                    continue
                score = score_job(text)
                if score >= 6:
                    jobs.append({"title": entry.title, "link": link, "score": score, "source": "Indeed"})
                    seen_jobs.add(link)
    # --- LinkedIn ---
    for role in ROLES:
        for loc in LOCATIONS:
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={role.replace(' ','%20')}&location={loc.replace(' ','%20')}"
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                for job in soup.select(".base-card"):
                    title_tag = job.select_one(".base-search-card__title")
                    link_tag = job.select_one("a")
                    if not title_tag or not link_tag:
                        continue
                    title = title_tag.text.strip()
                    link = link_tag["href"]
                    if link in seen_jobs:
                        continue
                    if not is_relevant(title):
                        continue
                    score = score_job(title)
                    if score >= 6:
                        jobs.append({"title": title, "link": link, "score": score, "source": "LinkedIn"})
                        seen_jobs.add(link)
            except:
                pass
    # Save seen jobs
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_jobs), f)
    # Sort by score
    jobs = sorted(jobs, key=lambda x: x["score"], reverse=True)[:30]
    return jobs