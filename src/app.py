"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path
import job_finder
import shodan_scanner

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# ---------------------------------------------------------------------------
# Shodan — Fortinet SSL VPN vulnerability scanner endpoints
# ---------------------------------------------------------------------------

class ShodanScanRequest(BaseModel):
    api_key: str
    max_results: Optional[int] = 100


@app.post("/security/fortinet/scan")
async def fortinet_scan(payload: ShodanScanRequest):
    """
    Query Shodan for internet-exposed Fortinet SSL VPN hosts and classify
    them against known critical CVEs (defensive use only).
    """
    if payload.max_results and payload.max_results > 500:
        raise HTTPException(status_code=400, detail="max_results cannot exceed 500")
    result = await shodan_scanner.run_scan(
        api_key=payload.api_key,
        max_results=payload.max_results or 100,
    )
    return result


@app.get("/security/fortinet/scans")
def list_fortinet_scans():
    """Return a summary list of all completed Shodan scans."""
    return shodan_scanner.list_scans()


@app.get("/security/fortinet/scans/{scan_id}")
def get_fortinet_scan(scan_id: str):
    """Return full results for a specific Shodan scan."""
    scan = shodan_scanner.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@app.get("/security/fortinet/cves")
def fortinet_cves():
    """Return the reference list of tracked Fortinet SSL VPN CVEs."""
    return shodan_scanner.get_cve_info()


# ---------------------------------------------------------------------------
# Job auto-apply endpoints
# ---------------------------------------------------------------------------

class JobSearchRequest(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    job_type: str
    compensation: str
    posted_on: str
    apply_url: str
    search_term: Optional[str] = ""


class StatusUpdateRequest(BaseModel):
    status: str  # new | saved | applied | rejected
    notes: Optional[str] = ""


@app.get("/jobs")
def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    min_score: int = Query(0, description="Minimum match score"),
):
    """Return all tracked jobs, optionally filtered."""
    result = list(job_finder.jobs.values())
    if status:
        result = [j for j in result if j["status"] == status]
    result = [j for j in result if j["match_score"] >= min_score]
    result.sort(key=lambda j: j["match_score"], reverse=True)
    return result


@app.get("/jobs/stats")
def job_stats():
    """Return application statistics."""
    return job_finder.get_stats()


@app.get("/jobs/recommendations")
def job_recommendations():
    """Return top-10 unacted-on jobs sorted by match score."""
    result = [
        j for j in job_finder.jobs.values()
        if j["status"] in ("new", "saved")
    ]
    result.sort(key=lambda j: j["match_score"], reverse=True)
    return result[:10]


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """Return a single job by ID."""
    job = job_finder.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/jobs")
def add_job(payload: JobSearchRequest):
    """Add or update a job in the tracker (called after an Indeed search)."""
    job = job_finder.add_job(
        job_id=payload.job_id,
        title=payload.title,
        company=payload.company,
        location=payload.location,
        job_type=payload.job_type,
        compensation=payload.compensation,
        posted_on=payload.posted_on,
        apply_url=payload.apply_url,
        search_term=payload.search_term,
    )
    return job


@app.put("/jobs/{job_id}/status")
def update_job_status(job_id: str, payload: StatusUpdateRequest):
    """Update the status of a tracked job."""
    valid = {"new", "saved", "applied", "rejected"}
    if payload.status not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {sorted(valid)}"
        )
    job = job_finder.set_status(job_id, payload.status, payload.notes or "")
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
