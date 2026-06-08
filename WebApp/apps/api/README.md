# Go API — Run and Test

REST endpoints that call PostgreSQL insert stored procedures.

**Base URL:** `http://localhost:8080`

---

## Prerequisites

1. **Go 1.22+** installed
2. **PostgreSQL** running on `localhost:5432`
3. Database **`email_classifier`** created with tables and insert functions applied

### One-time database setup

From `WebApp/apps/db/`, run scripts in order (psql or pgAdmin):

```text
001_create_db.sql
002_drop_tables.sql      (connect to email_classifier first)
003_create_tables.sql
004_insert_user.sql
006_insert_email.sql
007_insert_classification.sql
008_insert_rule.sql
```

Default credentials (see `WebApp/apps/db/Instructions`):

```text
postgres / admin @ localhost:5432 / email_classifier
```

---

## Start the API

```powershell
cd WebApp/apps/api
go run ./cmd/server
```

Optional: copy env vars from `.env.example`:

```powershell
$env:DATABASE_URL = "postgres://postgres:admin@localhost:5432/email_classifier?sslmode=disable"
$env:PORT = "8080"
go run ./cmd/server
```

You should see:

```text
api listening on http://localhost:8080
```

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | API is running |
| GET | `/health/db` | API can reach PostgreSQL |
| POST | `/api/v1/users` | Insert user |
| POST | `/api/v1/emails` | Insert email |
| POST | `/api/v1/classifications` | Insert classification |
| POST | `/api/v1/rules` | Insert rule |

**Success (201):**

```json
{"id": 1, "message": "User created successfully"}
```

**Error (4xx):**

```json
{"error": "Email already exists"}
```

---

## Test with PowerShell (terminal)

Keep the API running in one terminal. In another:

```powershell
cd WebApp/apps/api
.\scripts\test-endpoints.ps1
```

The script creates a user, seeds a test email account, then inserts an email, classification, and rule.

---

## Test with curl

**Health:**

```bash
curl http://localhost:8080/health
curl http://localhost:8080/health/db
```

**Create user:**

```bash
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"name\":\"Test User\"}"
```

**Create email** (needs a valid `user_id` and `account_id` — see seed step below):

```bash
curl -X POST http://localhost:8080/api/v1/emails \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":1,\"account_id\":1,\"provider_email_id\":\"gmail_123\",\"subject\":\"Hello\",\"sender\":\"a@b.com\",\"recipients\":[\"test@example.com\"],\"snippet\":\"Hi\",\"received_at\":\"2026-06-08T10:00:00Z\",\"cached_body\":\"Full body\"}"
```

**Create classification:**

```bash
curl -X POST http://localhost:8080/api/v1/classifications \
  -H "Content-Type: application/json" \
  -d "{\"email_id\":1,\"label\":\"spam\",\"confidence\":0.98,\"model_version\":\"v1.0\",\"source\":\"model\"}"
```

**Create rule:**

```bash
curl -X POST http://localhost:8080/api/v1/rules \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":1,\"name\":\"Spam Keywords\",\"condition_type\":\"subject_contains\",\"condition_value\":\"lottery\",\"action\":\"mark_spam\",\"enabled\":true}"
```

---

## Test with Postman

1. Import or create a collection with base URL `http://localhost:8080`.
2. Set header `Content-Type: application/json` on all POST requests.
3. Run in order:

| # | Method | URL | Body |
|---|--------|-----|------|
| 1 | GET | `/health/db` | — |
| 2 | POST | `/api/v1/users` | `{"email":"postman@example.com","name":"Postman User"}` |
| 3 | — | *(seed account in psql — see below)* | — |
| 4 | POST | `/api/v1/emails` | use `user_id` / `account_id` from steps 2–3 |
| 5 | POST | `/api/v1/classifications` | use `email_id` from step 4 |
| 6 | POST | `/api/v1/rules` | use `user_id` from step 2 |

A ready-made collection is in `scripts/postman-collection.json` — import it via **File → Import** in Postman.

---

## Seed email account (required for emails)

`fn_email_account_insert` is not ready yet. For testing emails, insert an account directly in psql after creating a user:

```sql
INSERT INTO email_accounts (user_id, provider, provider_email)
VALUES (1, 'gmail', 'test@example.com')
RETURNING id;
```

Use the returned `id` as `account_id` when calling `POST /api/v1/emails`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `database: ping database: connection refused` | Start PostgreSQL; check host/port |
| `database: ping database: ... does not exist` | Run `001_create_db.sql` |
| `function fn_user_insert does not exist` | Run insert function SQL scripts |
| `Invalid user or account` on email insert | Create user + email_account first |
| Port already in use | Set `$env:PORT = "8081"` or stop the other process |

---

## Later work

- Middleware (logging, CORS, recover): see `WebApp/docs/tickets/middleware-stack.md`
- `POST /api/v1/email-accounts` when `fn_email_account_insert` is complete
- Read endpoints when SELECT stored procedures exist
