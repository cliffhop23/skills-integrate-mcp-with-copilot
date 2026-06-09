document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("jobs-grid");
  const heading = document.getElementById("jobs-heading");
  const filterStatus = document.getElementById("filter-status");
  const filterScore = document.getElementById("filter-score");
  const filterScoreVal = document.getElementById("filter-score-val");
  const btnRecs = document.getElementById("btn-recommendations");
  const btnRefresh = document.getElementById("btn-refresh");
  const toast = document.getElementById("toast");

  let toastTimer = null;

  function showToast(msg, isError = false) {
    toast.textContent = msg;
    toast.style.background = isError ? "#c62828" : "#1a237e";
    toast.classList.remove("hidden");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.add("hidden"), 3000);
  }

  // --- Stats ---
  async function loadStats() {
    try {
      const res = await fetch("/jobs/stats");
      const s = await res.json();
      document.querySelector("#stat-total .stat-num").textContent = s.total;
      document.querySelector("#stat-new .stat-num").textContent = s.by_status.new ?? 0;
      document.querySelector("#stat-saved .stat-num").textContent = s.by_status.saved ?? 0;
      document.querySelector("#stat-applied .stat-num").textContent = s.by_status.applied ?? 0;
      document.querySelector("#stat-rejected .stat-num").textContent = s.by_status.rejected ?? 0;
    } catch (_) {}
  }

  // --- Build URL with filters ---
  function buildUrl() {
    const status = filterStatus.value;
    const score = filterScore.value;
    let url = "/jobs?";
    if (status) url += `status=${encodeURIComponent(status)}&`;
    if (score > 0) url += `min_score=${score}`;
    return url;
  }

  // --- Render jobs ---
  function renderJobs(jobs, titleText = "All Tracked Jobs") {
    heading.textContent = `${titleText} (${jobs.length})`;
    grid.innerHTML = "";

    if (!jobs.length) {
      grid.innerHTML = '<p class="loading-msg">No jobs match the current filters.</p>';
      return;
    }

    jobs.forEach((job) => {
      const card = document.createElement("div");
      card.className = "job-card";
      card.dataset.id = job.job_id;

      const scoreClass =
        job.match_score >= 60 ? "score-high" :
        job.match_score >= 30 ? "score-med" : "score-low";

      const statusClass = `status-${job.status}`;

      const appliedLine = job.applied_at
        ? `<p class="job-posted">Applied: ${new Date(job.applied_at).toLocaleDateString()}</p>`
        : "";

      const notesLine = job.notes
        ? `<p class="job-notes">Note: ${job.notes}</p>`
        : "";

      // Action buttons depend on current status
      let actions = "";
      if (job.status !== "applied" && job.status !== "rejected") {
        actions += `<button class="btn-apply" data-id="${job.job_id}" data-action="applied">
                      Mark Applied
                    </button>`;
      }
      if (job.status === "new") {
        actions += `<button class="btn-save" data-id="${job.job_id}" data-action="saved">
                      Save
                    </button>`;
      }
      if (job.status !== "rejected") {
        actions += `<button class="btn-pass" data-id="${job.job_id}" data-action="rejected">
                      Pass
                    </button>`;
      }
      if (job.status !== "new") {
        actions += `<button class="btn-undo" data-id="${job.job_id}" data-action="new">
                      Reset
                    </button>`;
      }

      card.innerHTML = `
        <div class="job-card-header">
          <a class="job-title" href="${job.apply_url}" target="_blank" rel="noopener">
            ${job.title}
          </a>
          <span class="score-badge ${scoreClass}">${job.match_score}%</span>
        </div>
        <p class="job-company">${job.company}</p>
        <p class="job-location">${job.location}</p>
        <p class="job-comp">${job.compensation !== "N/A" ? job.compensation : "Compensation not listed"}</p>
        <p class="job-type">${job.job_type !== "N/A" ? job.job_type : ""} &bull; ${job.search_term || ""}</p>
        <p class="job-posted">Posted: ${job.posted_on}</p>
        ${appliedLine}
        ${notesLine}
        <span class="status-pill ${statusClass}">${job.status}</span>
        <div class="job-actions">${actions}</div>
      `;

      grid.appendChild(card);
    });

    // Wire up action buttons
    grid.querySelectorAll("[data-action]").forEach((btn) => {
      btn.addEventListener("click", handleStatusChange);
    });
  }

  // --- Load all jobs ---
  async function loadJobs() {
    grid.innerHTML = '<p class="loading-msg">Loading jobs…</p>';
    try {
      const res = await fetch(buildUrl());
      const jobs = await res.json();
      renderJobs(jobs);
      loadStats();
    } catch (e) {
      grid.innerHTML = '<p class="loading-msg">Failed to load jobs. Is the server running?</p>';
      console.error(e);
    }
  }

  // --- Load recommendations ---
  async function loadRecommendations() {
    grid.innerHTML = '<p class="loading-msg">Loading recommendations…</p>';
    try {
      const res = await fetch("/jobs/recommendations");
      const jobs = await res.json();
      renderJobs(jobs, "Top Recommendations");
      loadStats();
    } catch (e) {
      grid.innerHTML = '<p class="loading-msg">Failed to load recommendations.</p>';
    }
  }

  // --- Status change ---
  async function handleStatusChange(e) {
    const btn = e.currentTarget;
    const jobId = btn.dataset.id;
    const action = btn.dataset.action;

    const labels = { applied: "Applied!", saved: "Saved", rejected: "Passed", new: "Reset" };
    try {
      const res = await fetch(`/jobs/${encodeURIComponent(jobId)}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: action }),
      });
      if (!res.ok) throw new Error(await res.text());
      showToast(`${labels[action]} — refreshing…`);
      loadJobs();
    } catch (err) {
      showToast("Update failed: " + err.message, true);
    }
  }

  // --- Filter / control wiring ---
  filterStatus.addEventListener("change", loadJobs);
  filterScore.addEventListener("input", () => {
    filterScoreVal.textContent = filterScore.value + "%";
    loadJobs();
  });
  btnRecs.addEventListener("click", loadRecommendations);
  btnRefresh.addEventListener("click", loadJobs);

  // --- Boot ---
  loadJobs();
  loadStats();
});
