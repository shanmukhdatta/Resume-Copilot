/**
 * config.js
 * ---------
 * The ONE place to point this frontend at a backend instance. Mirrors
 * the backend's own `app/config.py` philosophy: centralize
 * configuration instead of scattering base URLs through the codebase.
 *
 * FUTURE: read this from a <meta> tag or a build-time env var instead
 * of a hardcoded constant, so the same static bundle can be deployed
 * against multiple environments (staging/prod) without editing source.
 */
window.APP_CONFIG = {
  // Must match app.config.Settings.API_PREFIX on the backend (default "/api/v1").
  API_BASE_URL: "http://localhost:8000/api/v1",

  // How often to re-check backend health while the page is open (ms).
  HEALTH_CHECK_INTERVAL_MS: 15000,
};
