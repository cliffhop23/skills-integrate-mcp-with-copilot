"""Unit tests for job_finder module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import job_finder


def setup_function():
    """Reset job store before each test."""
    job_finder.jobs.clear()
    job_finder.seed_jobs()


def test_seed_jobs_populates_store():
    assert len(job_finder.jobs) > 0


def test_all_seeded_jobs_have_required_fields():
    required = {"job_id", "title", "company", "location", "job_type",
                "compensation", "posted_on", "apply_url", "status",
                "match_score", "applied_at", "notes"}
    for job in job_finder.jobs.values():
        assert required.issubset(job.keys()), f"Missing fields in {job['job_id']}"


def test_seeded_jobs_default_status_is_new():
    for job in job_finder.jobs.values():
        assert job["status"] == "new"


def test_match_score_bounded():
    for job in job_finder.jobs.values():
        assert 0 <= job["match_score"] <= 100


def test_score_keyword_hit():
    score = job_finder._score("Data Engineer AI", "Some Corp", "$80k")
    assert score > 0


def test_score_preferred_title_boost():
    score_match = job_finder._score("Data Analyst", "Acme", "N/A")
    score_no_match = job_finder._score("Cashier", "Grocery Co", "N/A")
    assert score_match > score_no_match


def test_score_capped_at_100():
    score = job_finder._score(
        "AI ML cybersecurity security fraud analyst data engineer python sql aws azure cloud",
        "IT HEROES security corp",
        "N/A",
    )
    assert score == 100


def test_add_job_creates_entry():
    job = job_finder.add_job(
        job_id="TEST_001",
        title="Security Engineer",
        company="Test Corp",
        location="Remote",
        job_type="Full-time",
        compensation="$100k",
        posted_on="June 1, 2026",
        apply_url="https://example.com/apply",
        search_term="Security",
    )
    assert job["job_id"] == "TEST_001"
    assert "TEST_001" in job_finder.jobs
    assert job["status"] == "new"
    assert job["match_score"] > 0


def test_add_job_preserves_existing_status():
    job_finder.set_status("JOBSEARCH_3", "saved")
    job_finder.add_job(
        job_id="JOBSEARCH_3",
        title="Data Analyst - AI Trainer",
        company="DataAnnotation",
        location="Richfield, MN",
        job_type="Contract",
        compensation="$50-$100/hr",
        posted_on="April 23, 2026",
        apply_url="https://to.indeed.com/aar7dcn8m6dz",
    )
    assert job_finder.jobs["JOBSEARCH_3"]["status"] == "saved"


def test_set_status_valid_transitions():
    for status in ("saved", "applied", "rejected", "new"):
        result = job_finder.set_status("JOBSEARCH_3", status)
        assert result is not None
        assert result["status"] == status


def test_set_status_applied_records_timestamp():
    job_finder.set_status("JOBSEARCH_3", "applied")
    assert job_finder.jobs["JOBSEARCH_3"]["applied_at"] is not None
    assert job_finder.jobs["JOBSEARCH_3"]["applied_at"].endswith("Z")


def test_set_status_notes_stored():
    job_finder.set_status("JOBSEARCH_3", "saved", notes="Good match")
    assert job_finder.jobs["JOBSEARCH_3"]["notes"] == "Good match"


def test_set_status_returns_none_for_missing_job():
    result = job_finder.set_status("DOES_NOT_EXIST", "saved")
    assert result is None


def test_get_stats_totals():
    stats = job_finder.get_stats()
    assert stats["total"] == len(job_finder.jobs)
    assert sum(stats["by_status"].values()) == stats["total"]


def test_get_stats_avg_score_in_range():
    stats = job_finder.get_stats()
    assert 0 <= stats["avg_match_score"] <= 100


def test_get_stats_applied_count_updates():
    job_finder.set_status("JOBSEARCH_3", "applied")
    job_finder.set_status("JOBSEARCH_4", "applied")
    stats = job_finder.get_stats()
    assert stats["by_status"].get("applied", 0) == 2


def test_get_stats_empty_store():
    job_finder.jobs.clear()
    stats = job_finder.get_stats()
    assert stats["total"] == 0
    assert stats["avg_match_score"] == 0
