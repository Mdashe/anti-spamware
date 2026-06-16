# Quick start (new machine)

Short guide after cloning the repo: Postgres, connection string, run the API.

---

## 1. Install

| Tool | Notes |
|------|--------|
| **Go 1.22+** | [go.dev/dl](https://go.dev/dl/) |
| **PostgreSQL** | pgAdmin is fine; note your **port** (often `5432` or `5433`) |

---

## 2. Database (one time)

Connect in **pgAdmin Query Tool** (or `psql`) to database **`postgres`** on your server.

Run scripts from `WebApp/apps/db/` **in this order**:

```text
002_drop_tables.sql
003_create_tables.sql
004_insert_user.sql
005_insert_email_account.sql
006_insert_email.sql
007_insert_classification.sql
008_insert_rule.sql
```

Optional: `010_export_table_script.sql` — helper to copy table data to another DB.

`001_create_db.sql` only needed if you want a separate `email_classifier` database instead of `postgres`.

---

## 3. Connection string

Build yours from pgAdmin → server **Properties → Connection**:

```text
postgres://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=disable
```

**This repo’s default** (see `WebApp/apps/api/.env.example`):

```text
postgres://postgres:admin@localhost:5433/postgres?sslmode=disable
```

On another machine, change **port**, **password**, or **host** — everything else stays the same.

**Check it works** (replace port if needed):

```powershell
$env:PGPASSWORD = "admin"
psql -h localhost -p 5433 -U postgres -d postgres -c "SELECT current_database(), inet_server_port();"
```

---

## 4. Run the API

```powershell
cd WebApp/apps/api
```

If your connection matches the default, just:

```powershell
go run ./cmd/server
```

If your port/password/database differ, set env vars first:

```powershell
$env:DATABASE_URL = "postgres://postgres:YOUR_PASSWORD@localhost:YOUR_PORT/postgres?sslmode=disable"
$env:PORT = "8080"
go run ./cmd/server
```

Success: `api listening on http://localhost:8080`

Quick check (second terminal):

```powershell
Invoke-WebRequest http://localhost:8080/health -UseBasicParsing
```

---

## 5. Moving data from another machine

1. On the **source** DB: run `010_export_table_script.sql`, then  
   `SELECT fn_export_table_script('users');` (repeat per table).
2. Paste each result into Query Tool on the **new** DB and execute.

Or use pgAdmin backup/restore for the whole database.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `password authentication failed` on **5432** / `email_classifier` | Wrong default — set `$env:DATABASE_URL` to your real host, port, and database |
| `connection refused` | Postgres not running, or wrong port |
| `function fn_* does not exist` | Re-run the `WebApp/apps/db/` scripts on the DB you’re connected to |

More API detail: `WebApp/apps/api/README.md`
