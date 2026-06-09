"""
Indeed Auto Job Apply — job tracking module.

Seeded with live Indeed results matching Thomas Hopkinson's resume profile
(AI Engineer / Cybersecurity / Data Engineer, Minneapolis-Saint Paul).
Scores each job against resume keywords and tracks application status.
"""

from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Resume-derived signal for match scoring
# ---------------------------------------------------------------------------
RESUME_KEYWORDS = {
    "ai", "ml", "machine learning", "artificial intelligence",
    "cybersecurity", "security", "fraud", "analyst",
    "data engineer", "data", "engineer", "python", "sql",
    "aws", "azure", "cloud", "llm", "automation",
    "it", "network", "consultant", "project manager",
    "react", "full stack", "devops", "kubernetes", "docker",
}

PREFERRED_TITLES = [
    "AI Engineer", "ML Engineer", "Data Engineer", "Data Analyst",
    "IT Security Specialist", "Cybersecurity Analyst", "Fraud Analyst",
    "IT Project Manager", "IT Consultant", "Security Engineer",
]

MIN_HOURLY = 22  # $/hr

# ---------------------------------------------------------------------------
# In-memory job store  {job_id: job_dict}
# ---------------------------------------------------------------------------
jobs: dict[str, dict] = {}


def _score(title: str, company: str, compensation: str) -> int:
    """Return 0-100 match score against resume profile."""
    score = 0
    text = (title + " " + company).lower()
    for kw in RESUME_KEYWORDS:
        if kw in text:
            score += 5
    for pt in PREFERRED_TITLES:
        if pt.lower() in text:
            score += 15
    return min(score, 100)


def seed_jobs() -> None:
    """Populate the store with live Indeed results fetched at build time."""
    raw = [
        # --- Data Analyst / Minneapolis ---
        {
            "job_id": "JOBSEARCH_3",
            "title": "Data Analyst - AI Trainer",
            "company": "DataAnnotation",
            "location": "Richfield, MN",
            "job_type": "Contract",
            "compensation": "$50 - $100 an hour",
            "posted_on": "April 23, 2026",
            "apply_url": "https://to.indeed.com/aar7dcn8m6dz",
            "search_term": "Data Analyst",
        },
        {
            "job_id": "JOBSEARCH_4",
            "title": "Data Analyst",
            "company": "Twin Cities NECA",
            "location": "Saint Louis Park, MN",
            "job_type": "Permanent",
            "compensation": "$60,000 - $75,000 a year",
            "posted_on": "May 22, 2026",
            "apply_url": "https://to.indeed.com/aach69kpzsh2",
            "search_term": "Data Analyst",
        },
        {
            "job_id": "JOBSEARCH_8",
            "title": "Business Analyst",
            "company": "Artius Solutions",
            "location": "Minneapolis, MN",
            "job_type": "Contract",
            "compensation": "$60 - $65 an hour",
            "posted_on": "May 06, 2026",
            "apply_url": "https://to.indeed.com/aazvpmf8c74m",
            "search_term": "Data Analyst",
        },
        {
            "job_id": "JOBSEARCH_9",
            "title": "Business Intelligence & Data Automation Specialist",
            "company": "Corporate Technologies (Minneapolis)",
            "location": "Minneapolis, MN",
            "job_type": "Full-time",
            "compensation": "$75,000 - $85,000 a year",
            "posted_on": "April 13, 2026",
            "apply_url": "https://to.indeed.com/aafmk4wk48c6",
            "search_term": "Data Analyst",
        },
        # --- IT Project Manager / Remote ---
        {
            "job_id": "JOBSEARCH_15",
            "title": "IT Project Coordinator",
            "company": "Tencate Grass",
            "location": "Remote",
            "job_type": "Full-time",
            "compensation": "N/A",
            "posted_on": "May 18, 2026",
            "apply_url": "https://to.indeed.com/aa8yrkvxgxrs",
            "search_term": "IT Project Manager",
        },
        {
            "job_id": "JOBSEARCH_16",
            "title": "Technical Project Lead",
            "company": "CM First Group",
            "location": "Remote",
            "job_type": "Permanent",
            "compensation": "$75,000 - $100,000 a year",
            "posted_on": "May 19, 2026",
            "apply_url": "https://to.indeed.com/aazmy4mh8hsk",
            "search_term": "IT Project Manager",
        },
        {
            "job_id": "JOBSEARCH_18",
            "title": "Project Coordinator (Telecom)",
            "company": "Prolim global system",
            "location": "Remote",
            "job_type": "Contract",
            "compensation": "$35 - $40 an hour",
            "posted_on": "May 11, 2026",
            "apply_url": "https://to.indeed.com/aal7wsk9g4kz",
            "search_term": "IT Project Manager",
        },
        {
            "job_id": "JOBSEARCH_19",
            "title": "Project and Operations Manager",
            "company": "Decimal Systems",
            "location": "Remote",
            "job_type": "Full-time",
            "compensation": "$80,000 - $110,000 a year",
            "posted_on": "May 27, 2026",
            "apply_url": "https://to.indeed.com/aa2qvrntg7bf",
            "search_term": "IT Project Manager",
        },
        # --- Data Engineer / Remote ---
        {
            "job_id": "JOBSEARCH_22",
            "title": "Data Engineer - AI Trainer",
            "company": "DataAnnotation",
            "location": "Remote",
            "job_type": "Contract",
            "compensation": "$50 - $100 an hour",
            "posted_on": "January 16, 2026",
            "apply_url": "https://to.indeed.com/aalc4nx6rfsf",
            "search_term": "Data Engineer",
        },
        {
            "job_id": "JOBSEARCH_26",
            "title": "Data Engineer",
            "company": "IT HEROES",
            "location": "Remote",
            "job_type": "Full-time",
            "compensation": "$45 - $55 an hour",
            "posted_on": "May 29, 2026",
            "apply_url": "https://to.indeed.com/aaddyn9cqkn7",
            "search_term": "Data Engineer",
        },
        {
            "job_id": "JOBSEARCH_27",
            "title": "Data Engineer",
            "company": "Cross International, Inc",
            "location": "Remote",
            "job_type": "Full-time",
            "compensation": "$71,869 - $86,552 a year",
            "posted_on": "May 14, 2026",
            "apply_url": "https://to.indeed.com/aatk8k2lt6kd",
            "search_term": "Data Engineer",
        },
        {
            "job_id": "JOBSEARCH_30",
            "title": "Data Engineer Remote - w2",
            "company": "itheroes inc",
            "location": "Remote",
            "job_type": "Contract",
            "compensation": "$50 - $55 an hour",
            "posted_on": "May 30, 2026",
            "apply_url": "https://to.indeed.com/aa48lwq7gyyj",
            "search_term": "Data Engineer",
        },
    ]

    for item in raw:
        jid = item["job_id"]
        jobs[jid] = {
            **item,
            "status": "new",
            "match_score": _score(item["title"], item["company"], item["compensation"]),
            "applied_at": None,
            "notes": "",
        }


def add_job(job_id: str, title: str, company: str, location: str,
            job_type: str, compensation: str, posted_on: str,
            apply_url: str, search_term: str = "") -> dict:
    """Add or update a job in the store."""
    jobs[job_id] = {
        "job_id": job_id,
        "title": title,
        "company": company,
        "location": location,
        "job_type": job_type,
        "compensation": compensation,
        "posted_on": posted_on,
        "apply_url": apply_url,
        "search_term": search_term,
        "status": jobs.get(job_id, {}).get("status", "new"),
        "match_score": _score(title, company, compensation),
        "applied_at": jobs.get(job_id, {}).get("applied_at"),
        "notes": jobs.get(job_id, {}).get("notes", ""),
    }
    return jobs[job_id]


def set_status(job_id: str, status: str, notes: str = "") -> Optional[dict]:
    if job_id not in jobs:
        return None
    jobs[job_id]["status"] = status
    if notes:
        jobs[job_id]["notes"] = notes
    if status == "applied":
        jobs[job_id]["applied_at"] = datetime.utcnow().isoformat() + "Z"
    return jobs[job_id]


def get_stats() -> dict:
    total = len(jobs)
    by_status: dict[str, int] = {}
    for j in jobs.values():
        s = j["status"]
        by_status[s] = by_status.get(s, 0) + 1
    return {
        "total": total,
        "by_status": by_status,
        "avg_match_score": (
            round(sum(j["match_score"] for j in jobs.values()) / total, 1)
            if total else 0
        ),
    }


# Seed on import
seed_jobs()
