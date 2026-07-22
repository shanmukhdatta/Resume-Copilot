/**
 * main.js
 * -------
 * Wires the DOM to ResumeCopilotAPI. Split into small named functions
 * grouped by concern (reveals / health / upload / demo flow / render)
 * rather than one big listener soup, so each piece stays easy to touch
 * in isolation — same "single responsibility" spirit as the backend.
 */

/* ========================================================================
   1. Scroll reveals
   ======================================================================== */

function initScrollReveals() {
  const targets = document.querySelectorAll(".reveal, .reveal-line");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
  );
  targets.forEach((el) => observer.observe(el));
}

/* ========================================================================
   2. Backend health indicator
   ======================================================================== */

async function checkBackendHealth() {
  const el = document.getElementById("backend-status");
  const label = el.querySelector(".nav__status-label");
  try {
    const health = await ResumeCopilotAPI.health();
    el.dataset.state = "online";
    label.textContent = `${health.app_name} online`;
  } catch (err) {
    el.dataset.state = "offline";
    label.textContent = "Backend unreachable";
  }
}

function initHealthCheck() {
  checkBackendHealth();
  setInterval(checkBackendHealth, window.APP_CONFIG.HEALTH_CHECK_INTERVAL_MS);
}

/* ========================================================================
   3. Demo state
   ======================================================================== */

const demoState = {
  resumeFile: null,
  jdFile: null,
  resumeFileId: null,
  jdFileId: null,
  sessionId: null,
};

const AGENT_LABELS = [
  "Planner", "Summary", "Skills", "Experience",
  "Projects", "Education", "Certifications", "Achievements",
];

function setStep(stepId) {
  document.querySelectorAll(".demo-step").forEach((el) => {
    el.dataset.active = el.id === stepId ? "true" : "false";
  });
}

function showFormError(message) {
  const el = document.getElementById("form-error");
  el.textContent = message || "";
}

/* ---- Dropzones ---- */

function initDropzone(zoneId, inputId, filenameId, onFile) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  const filenameEl = document.getElementById(filenameId);

  function handleFile(file) {
    if (!file) return;
    filenameEl.textContent = file.name;
    zone.dataset.filled = "true";
    onFile(file);
  }

  input.addEventListener("change", () => handleFile(input.files[0]));

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.style.borderColor = "var(--accent)";
  });
  zone.addEventListener("dragleave", () => {
    zone.style.borderColor = "";
  });
  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.style.borderColor = "";
    const file = e.dataTransfer.files[0];
    if (file) {
      input.files = e.dataTransfer.files;
      handleFile(file);
    }
  });
}

function refreshGenerateButton() {
  const btn = document.getElementById("btn-generate");
  const ready = demoState.resumeFile && demoState.jdFile;
  btn.disabled = !ready;
  btn.textContent = ready ? "Generate my tailored resume" : "Upload both files to continue";
}

/* ---- Agent progress (staged animation while the blocking call runs) ---- */

function buildAgentGrid() {
  const grid = document.getElementById("agent-grid");
  grid.innerHTML = AGENT_LABELS.map(
    (name) => `
      <div class="agent-chip" data-state="pending" data-agent="${name}">
        <span class="agent-chip__dot"></span>
        <span>${name}</span>
      </div>`
  ).join("");
}

function animateAgentProgress() {
  const chips = Array.from(document.querySelectorAll(".agent-chip"));
  const statusEl = document.getElementById("agent-status");
  const messages = [
    "Planning your tailoring strategy…",
    "Eight agents writing in parallel…",
    "Validating output against your original resume…",
    "Rendering your resume…",
  ];
  let msgIndex = 0;
  statusEl.textContent = messages[0];

  chips[0].dataset.state = "active";

  let i = 0;
  const interval = setInterval(() => {
    if (chips[i]) chips[i].dataset.state = "done";
    i += 1;
    if (chips[i]) chips[i].dataset.state = "active";
    msgIndex = Math.min(msgIndex + 1, messages.length - 1);
    statusEl.textContent = messages[msgIndex];
    if (i >= chips.length) clearInterval(interval);
  }, 550);

  // Returned so the caller can force-complete once the real response lands.
  return () => {
    clearInterval(interval);
    chips.forEach((c) => (c.dataset.state = "done"));
    statusEl.textContent = "Done.";
  };
}

/* ---- Results rendering ---- */

function scoreColor(score) {
  if (score >= 75) return "var(--good)";
  if (score >= 50) return "var(--warn)";
  return "var(--danger)";
}

function renderScorecard(evaluation, validation) {
  const ring = document.getElementById("score-ring-fill");
  const circumference = 2 * Math.PI * 52; // matches r=52 in the SVG
  const score = Math.max(0, Math.min(100, evaluation.ats_score || 0));
  const offset = circumference - (score / 100) * circumference;

  ring.style.stroke = scoreColor(score);
  // rAF so the transition actually animates from its initial state.
  requestAnimationFrame(() => {
    ring.style.strokeDashoffset = offset;
  });
  document.getElementById("score-value").textContent = Math.round(score);

  document.getElementById("metric-keywords").textContent = `${evaluation.keyword_coverage ?? 0}%`;
  document.getElementById("metric-match").textContent = `${evaluation.resume_match_score ?? 0}%`;

  const validationEl = document.getElementById("metric-validation");
  validationEl.textContent = validation.overall_passed ? "Passed" : "Needs review";
  validationEl.style.color = validation.overall_passed ? "var(--good)" : "var(--warn)";

  const strengthsEl = document.getElementById("strengths-list");
  strengthsEl.innerHTML = (evaluation.strengths || [])
    .slice(0, 4)
    .map((s) => `<span class="tag">${escapeHtml(s)}</span>`)
    .join("");

  const missingEl = document.getElementById("missing-skills-list");
  const missing = evaluation.skill_gap?.missing_skills || [];
  missingEl.innerHTML = missing
    .slice(0, 6)
    .map((s) => `<span class="tag">Missing: ${escapeHtml(s)}</span>`)
    .join("");

  renderInsightList("recommendations-list", evaluation.recommendations, "Nothing to flag — this resume is well aligned with the role.");
  renderInsightList("weaknesses-list", evaluation.weaknesses, "No significant weaknesses detected.");
  renderLearningResources(evaluation.learning_resources);
}

function renderInsightList(listId, items, emptyMessage) {
  const el = document.getElementById(listId);
  if (!items || items.length === 0) {
    el.innerHTML = `<li class="insight-list__empty">${escapeHtml(emptyMessage)}</li>`;
    return;
  }
  el.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderLearningResources(learningResources) {
  const el = document.getElementById("resource-list");
  if (!learningResources || learningResources.length === 0) {
    el.innerHTML = `<p class="insight-list__empty">No skill gaps to close — nothing to suggest here.</p>`;
    return;
  }
  el.innerHTML = learningResources
    .map((entry) => {
      const links = (entry.resources || [])
        .map(
          (r) => `<a class="resource-link" href="${escapeHtml(r.url)}" target="_blank" rel="noopener noreferrer">
            ${escapeHtml(r.title)} <span class="resource-link__provider">${escapeHtml(r.provider)}</span>
          </a>`
        )
        .join("");
      return `
        <div class="resource-group">
          <div class="resource-group__skill">${escapeHtml(entry.skill)}</div>
          <div class="resource-group__links">${links}</div>
        </div>`;
    })
    .join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function renderResumePreview(resume) {
  const el = document.getElementById("resume-preview");
  const c = resume.contact || {};

  if (!c.full_name && !resume.summary && (resume.experience || []).length === 0) {
    el.innerHTML = `<p class="rp-empty">No content was generated for this section yet. This can happen if the backend's LLM provider isn't configured — see the README.</p>`;
    return;
  }

  const contactLine = [c.email, c.phone, c.location].filter(Boolean).join("  ·  ");

  const skillsHtml = (resume.skills || [])
    .map((cat) => `<p><strong>${escapeHtml(cat.category)}:</strong> ${escapeHtml((cat.skills || []).join(", "))}</p>`)
    .join("");

  const experienceHtml = (resume.experience || [])
    .map(
      (exp) => `
      <div class="rp-entry">
        <div class="rp-entry-title">
          <span>${escapeHtml(exp.title)}, ${escapeHtml(exp.company)}</span>
          <span class="rp-entry-dates">${escapeHtml(exp.start_date)} – ${escapeHtml(exp.end_date)}</span>
        </div>
        <ul>${(exp.bullets || []).map((b) => `<li>${escapeHtml(b)}</li>`).join("")}</ul>
      </div>`
    )
    .join("");

  const projectsHtml = (resume.projects || [])
    .map(
      (p) => `
      <div class="rp-entry">
        <div class="rp-entry-title"><span>${escapeHtml(p.name)}</span></div>
        <ul>${(p.bullets || []).map((b) => `<li>${escapeHtml(b)}</li>`).join("")}</ul>
      </div>`
    )
    .join("");

  const educationHtml = (resume.education || [])
    .map(
      (e) => `
      <div class="rp-entry">
        <div class="rp-entry-title">
          <span>${escapeHtml(e.degree)}, ${escapeHtml(e.institution)}</span>
          <span class="rp-entry-dates">${escapeHtml(e.start_date)} – ${escapeHtml(e.end_date)}</span>
        </div>
      </div>`
    )
    .join("");

  el.innerHTML = `
    <h3>${escapeHtml(c.full_name || "Your name")}</h3>
    <p class="rp-contact">${escapeHtml(contactLine)}</p>
    ${resume.summary ? `<div class="rp-section"><h4>Summary</h4><p class="rp-summary">${escapeHtml(resume.summary)}</p></div>` : ""}
    ${skillsHtml ? `<div class="rp-section"><h4>Skills</h4>${skillsHtml}</div>` : ""}
    ${experienceHtml ? `<div class="rp-section"><h4>Experience</h4>${experienceHtml}</div>` : ""}
    ${projectsHtml ? `<div class="rp-section"><h4>Projects</h4>${projectsHtml}</div>` : ""}
    ${educationHtml ? `<div class="rp-section"><h4>Education</h4>${educationHtml}</div>` : ""}
  `;
}

/* ---- Reset ---- */

function resetDemo() {
  demoState.resumeFile = null;
  demoState.jdFile = null;
  demoState.resumeFileId = null;
  demoState.jdFileId = null;
  demoState.sessionId = null;

  ["input-resume", "input-jd"].forEach((id) => (document.getElementById(id).value = ""));
  ["filename-resume", "filename-jd"].forEach((id) => (document.getElementById(id).textContent = ""));
  ["dropzone-resume", "dropzone-jd"].forEach((id) => (document.getElementById(id).dataset.filled = "false"));
  document.getElementById("input-notes").value = "";
  showFormError("");
  refreshGenerateButton();
  setStep("step-upload");
}

/* ---- Main generate flow ---- */

async function handleGenerateClick() {
  showFormError("");
  setStep("step-generating");
  buildAgentGrid();
  const completeAnimation = animateAgentProgress();

  try {
    const [resumeUpload, jdUpload] = await Promise.all([
      ResumeCopilotAPI.uploadFile("resume", demoState.resumeFile),
      ResumeCopilotAPI.uploadFile("jd", demoState.jdFile),
    ]);
    demoState.resumeFileId = resumeUpload.file_id;
    demoState.jdFileId = jdUpload.file_id;

    const template = document.getElementById("input-template").value;
    const notes = document.getElementById("input-notes").value;

    const result = await ResumeCopilotAPI.generateResume({
      resumeFileId: demoState.resumeFileId,
      jdFileId: demoState.jdFileId,
      userNotes: notes,
      template,
    });

    demoState.sessionId = result.session_id;
    completeAnimation();

    setTimeout(() => {
      renderScorecard(result.evaluation, result.validation);
      renderResumePreview(result.resume);
      setStep("step-results");
    }, 400);
  } catch (err) {
    completeAnimation();
    setStep("step-upload");
    showFormError(err.message || "Something went wrong. Check that your backend is running.");
  }
}

function handleExportClick(exportFormat) {
  if (!demoState.sessionId) return;
  const url = ResumeCopilotAPI.downloadUrl(demoState.sessionId, exportFormat);
  window.open(url, "_blank");
}

/* ========================================================================
   4. Init
   ======================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initScrollReveals();
  initHealthCheck();

  initDropzone("dropzone-resume", "input-resume", "filename-resume", (file) => {
    demoState.resumeFile = file;
    refreshGenerateButton();
  });
  initDropzone("dropzone-jd", "input-jd", "filename-jd", (file) => {
    demoState.jdFile = file;
    refreshGenerateButton();
  });

  document.getElementById("btn-generate").addEventListener("click", handleGenerateClick);
  document.getElementById("btn-start-over").addEventListener("click", resetDemo);

  document.querySelectorAll("[data-export]").forEach((btn) => {
    btn.addEventListener("click", () => handleExportClick(btn.dataset.export));
  });
});
