// ── Request Logger ────────────────────────────────────────────
const requestLogger = (req, res, next) => {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${req.method} ${req.originalUrl}`);
  next();
};

// ── Not Found Handler ─────────────────────────────────────────
const notFound = (req, res) => {
  res.status(404).json({ success: false, error: `Route ${req.method} ${req.originalUrl} not found` });
};

// ── Global Error Handler ──────────────────────────────────────
const errorHandler = (err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({ success: false, error: err.message || "Internal Server Error" });
};

// ── Validate Required Fields ──────────────────────────────────
const requireFields = (...fields) => (req, res, next) => {
  const missing = fields.filter((f) => req.body[f] === undefined || req.body[f] === "");
  if (missing.length) {
    return res.status(400).json({ success: false, error: `Missing required fields: ${missing.join(", ")}` });
  }
  next();
};

module.exports = { requestLogger, notFound, errorHandler, requireFields };
