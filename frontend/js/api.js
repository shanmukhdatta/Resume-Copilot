/**
 * api.js
 * ------
 * A deliberately thin wrapper around the backend's REST API. Every
 * function here maps 1:1 to a route in app/api/routes/*.py so the
 * request/response shapes never drift silently — if the backend schema
 * changes, this is the only file that needs to change.
 *
 * No framework, no bundler: plain fetch, because this is a static site.
 */
const ResumeCopilotAPI = (() => {
  const BASE = window.APP_CONFIG.API_BASE_URL;

  async function request(path, options = {}) {
    const res = await fetch(`${BASE}${path}`, options);
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail || detail;
      } catch (_) {
        /* response wasn't JSON (e.g. a file download error) */
      }
      throw new Error(detail);
    }
    return res;
  }

  return {
    /** GET /health -> {status, app_name, version} */
    async health() {
      const res = await request("/health");
      return res.json();
    },

    /**
     * POST /upload/resume or /upload/jd (multipart)
     * -> {file_id, filename, saved_path, size_mb}
     */
    async uploadFile(kind, file) {
      const path = kind === "resume" ? "/upload/resume" : "/upload/jd";
      const form = new FormData();
      form.append("file", file);
      const res = await request(path, { method: "POST", body: form });
      return res.json();
    },

    /**
     * POST /resume/generate
     * body: {resume_file_id, jd_file_id, user_notes, template}
     * -> {session_id, resume, validation, evaluation}
     *
     * This is the single call that runs the ENTIRE LangGraph pipeline
     * server-side (upload -> parse -> plan -> 8 parallel agents ->
     * assembly -> validation/retry -> render -> evaluate) and blocks
     * until it's done. See FUTURE note in index.html about streaming
     * per-agent progress instead.
     */
    async generateResume({ resumeFileId, jdFileId, userNotes, template }) {
      const res = await request("/resume/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_file_id: resumeFileId,
          jd_file_id: jdFileId,
          user_notes: userNotes || "",
          template: template || "ats",
        }),
      });
      return res.json();
    },

    /** POST /evaluation {session_id} -> EvaluationReport */
    async getEvaluation(sessionId) {
      const res = await request("/evaluation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      return res.json();
    },

    /** GET /templates -> {templates: string[]} */
    async listTemplates() {
      const res = await request("/templates");
      return res.json();
    },

    /**
     * GET /templates/download/{session_id}/{export_format}
     * Triggers a real browser download of the rendered file.
     */
    downloadUrl(sessionId, exportFormat) {
      return `${BASE}/templates/download/${sessionId}/${exportFormat}`;
    },
  };
})();
