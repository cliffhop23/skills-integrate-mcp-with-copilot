"""Integration tests for /jobs API endpoints."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import job_finder
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def setup_function():
    """Reset job store before each test."""
    job_finder.jobs.clear()
    job_finder.seed_jobs()


# --- GET /jobs ---

def test_list_jobs_returns_list():
    resp = client.get("/jobs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == len(job_finder.jobs)


def test_list_jobs_sorted_by_score_descending():
    resp = client.get("/jobs")
    scores = [j["match_score"] for j in resp.json()]
    assert scores == sorted(scores, reverse=True)


def test_list_jobs_filter_by_status():
    job_finder.set_status("JOBSEARCH_3", "applied")
    resp = client.get("/jobs?status=applied")
    assert resp.status_code == 200
    data = resp.json()
    assert all(j["status"] == "applied" for j in data)
    assert len(data) == 1


def test_list_jobs_filter_by_min_score():
    resp = client.get("/jobs?min_score=50")
    assert resp.status_code == 200
    data = resp.json()
    assert all(j["match_score"] >= 50 for j in data)


def test_list_jobs_unknown_status_returns_empty():
    resp = client.get("/jobs?status=nonexistent")
    assert resp.status_code == 200
    assert resp.json() == []


# --- GET /jobs/stats ---

def test_stats_structure():
    resp = client.get("/jobs/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "by_status" in data
    assert "avg_match_score" in data


def test_stats_total_matches_store():
    resp = client.get("/jobs/stats")
    assert resp.json()["total"] == len(job_finder.jobs)


# --- GET /jobs/recommendations ---

def test_recommendations_only_new_and_saved():
    job_finder.set_status("JOBSEARCH_3", "applied")
    job_finder.set_status("JOBSEARCH_4", "rejected")
    resp = client.get("/jobs/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    for j in data:
        assert j["status"] in ("new", "saved")


def test_recommendations_max_10():
    resp = client.get("/jobs/recommendations")
    assert len(resp.json()) <= 10


def test_recommendations_sorted_by_score():
    resp = client.get("/jobs/recommendations")
    scores = [j["match_score"] for j in resp.json()]
    assert scores == sorted(scores, reverse=True)


# --- GET /jobs/{job_id} ---

def test_get_job_returns_correct_job():
    resp = client.get("/jobs/JOBSEARCH_3")
    assert resp.status_code == 200
    assert resp.json()["job_id"] == "JOBSEARCH_3"


def test_get_job_not_found():
    resp = client.get("/jobs/DOES_NOT_EXIST")
    assert resp.status_code == 404


# --- POST /jobs ---

def test_add_job_creates_and_returns():
    payload = {
        "job_id": "TEST_NEW",
        "title": "AI Security Engineer",
        "company": "CyberCo",
        "location": "Remote",
        "job_type": "Full-time",
        "compensation": "$120,000 a year",
        "posted_on": "June 9, 2026",
        "apply_url": "https://example.com/apply",
        "search_term": "Security Engineer",
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["job_id"] == "TEST_NEW"
    assert data["status"] == "new"
    assert data["match_score"] > 0


def test_add_job_appears_in_list():
    payload = {
        "job_id": "TEST_LIST",
        "title": "Data Engineer",
        "company": "DataCo",
        "location": "Minneapolis, MN",
        "job_type": "Full-time",
        "compensation": "$90,000 a year",
        "posted_on": "June 9, 2026",
        "apply_url": "https://example.com/apply2",
    }
    client.post("/jobs", json=payload)
    resp = client.get("/jobs")
    ids = [j["job_id"] for j in resp.json()]
    assert "TEST_LIST" in ids


# --- PUT /jobs/{job_id}/status ---

def test_update_status_valid():
    for status in ("saved", "applied", "rejected", "new"):
        resp = client.put("/jobs/JOBSEARCH_3/status", json={"status": status})
        assert resp.status_code == 200
        assert resp.json()["status"] == status


def test_update_status_applied_sets_timestamp():
    resp = client.put("/jobs/JOBSEARCH_3/status", json={"status": "applied"})
    assert resp.status_code == 200
    assert resp.json()["applied_at"] is not None


def test_update_status_invalid_value():
    resp = client.put("/jobs/JOBSEARCH_3/status", json={"status": "maybe"})
    assert resp.status_code == 400


def test_update_status_not_found():
    resp = client.put("/jobs/GHOST/status", json={"status": "saved"})
    assert resp.status_code == 404


def test_update_status_with_notes():
    resp = client.put(
        "/jobs/JOBSEARCH_3/status",
        json={"status": "saved", "notes": "Great company"},
    )
    assert resp.status_code == 200
    assert resp.json()["notes"] == "Great company"
