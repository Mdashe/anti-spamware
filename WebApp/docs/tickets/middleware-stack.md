# Ticket: Minimal Middleware Stack

**Status:** Backlog  
**Branch target:** TBD (after `API_DB_Store`)  
**Priority:** Medium  

---

## Summary

Add a minimal HTTP middleware stack to the Go API (`WebApp/apps/api`). The REST endpoints and DB layer exist without middleware today; this ticket covers cross-cutting concerns only.

---

## Scope

Implement three middleware layers, applied globally to all routes:

| Middleware | Purpose |
|------------|---------|
| **Logging** | Log method, path, status code, and request duration for every request |
| **CORS** | Allow browser requests from the SvelteKit dev server (and later production origin) |
| **Recover** | Catch panics in handlers and return `500 Internal Server Error` instead of crashing the process |

---

## Out of scope

- Authentication / session middleware
- Rate limiting
- Request ID propagation (optional follow-up)
- Reverse proxy / static file serving for SvelteKit

---

## Acceptance criteria

1. Every request logs one line: `METHOD path → status (duration)`.
2. `OPTIONS` preflight requests return `204` with appropriate CORS headers.
3. `Access-Control-Allow-Origin` is configurable via env (default: `http://localhost:5173` for Vite dev).
4. A panic in any handler returns JSON `{"error":"internal server error"}` with status `500`; the server keeps running.
5. Existing endpoints (`/health`, `/health/db`, `/api/v1/*`) behave unchanged aside from CORS headers and logging.
6. `WebApp/scripts/test-api.ps1` (or equivalent) still passes.

---

## Suggested implementation

**Location:** `WebApp/apps/api/internal/middleware/`

```text
middleware/
  logging.go    → func Logging(next http.Handler) http.Handler
  cors.go       → func CORS(allowedOrigin string) func(http.Handler) http.Handler
  recover.go    → func Recover(next http.Handler) http.Handler
  chain.go      → func Chain(middlewares ...func(http.Handler) http.Handler) http.Handler
```

**Wire in `cmd/server/main.go`:**

```go
handler := middleware.Chain(
    mux,
    middleware.Recover,
    middleware.Logging,
    middleware.CORS(cfg.AllowedOrigin),
)
server := &http.Server{Handler: handler, ...}
```

**Config additions (`internal/config/config.go`):**

```text
ALLOWED_ORIGIN=http://localhost:5173   # optional, default above
```

---

## Testing

- Manual: trigger a panic in a test handler temporarily; confirm 500 JSON response and server stays up.
- Manual: send `OPTIONS` from browser devtools or curl; confirm CORS headers.
- Manual: confirm log lines appear for `GET /health` and `POST /api/v1/users`.
- Automated: optional unit test for CORS header values.

---

## References

- Design doc: `WebApp/docs/design-decisions.md` (browser ↔ Go API boundary)
- Current API entry: `WebApp/apps/api/cmd/server/main.go`
- Run/test guide: `WebApp/apps/api/README.md`
