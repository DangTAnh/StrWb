---
phase: 09-polish-deploy
plan: 03
subsystem: Deploy docs v1.1 migration + backup
tags: [deploy, docs, migration, backup, wal, v1.1]
dependency_graph:
  requires: [09-01]
  provides: [deploy-migration-v1.1, wal-safe-backup, readme-v1.1-description]
  affects: [docs/deploy/README.md, docs/deploy/Windows.md, docs/deploy/Linux.md, README.md]
tech_stack:
  added: []
  patterns: [docs, deploy-guides]
decisions:
  - "Migration v1.1 docs describe the idempotent init-db upgrade accurately per app/db.py: cost_price ALTER (idempotent), legacy orders rebuild only when empty, abort with explicit message when legacy rows exist (never data loss)"
  - "Backup guidance covers SQLite WAL: .db + -wal + -shm file copy OR sqlite3 .backup (WAL-safe) on both Windows and Linux"
  - "README v1.1 description line placed directly under restored # StoreWeb H1, no other README content altered"
metrics:
  duration: 6 min
  completed_date: "2026-08-03T08:30:00Z"
  tasks: 3
  files: 4
---

# Phase 9 Plan 3: Deploy Docs v1.1 Migration + Backup Summary

Updated the deploy documentation for the v1.1 release: migration + backup instructions, and the repo-root README v1.1 description.

## Tasks Completed

| # | Task | Status | Commit | Files |
|---|------|--------|--------|-------|
| 1 | Migration v1.1 + backup sections in docs/deploy/README.md | DONE | `cb9807d` | docs/deploy/README.md |
| 2 | Windows backup section + init-db upgrade note + README v1.1 line | DONE | `c826ff5` | docs/deploy/Windows.md, README.md |
| 3 | Extend Linux backup + init-db upgrade note | DONE | `c959493` | docs/deploy/Linux.md |

## Changes Applied

### Task 1: docs/deploy/README.md (`cb9807d`)

- **Migration v1.1** section: backup `data/app.db` first, then idempotent `flask --app wsgi init-db` — no separate migration script (PLAT-05). Documents init-db's data-safety guards accurately per `app/db.py`:
  - `cost_price` column added only if absent (PRAGMA guard, idempotent)
  - Legacy `orders` table rebuilt only when empty; explicit `Manual migration required` abort when legacy rows exist (never drops data)
  - Upserts admin account from `.env`; `ADMIN_PASSWORD` must be valid
- **Sao lưu (Backup)** section: WAL-safe backup — `sqlite3 .backup` or copy `app.db` + `app.db-wal` + `app.db-shm` together; uploads sync guidance; scheduling cross-refs to Windows.md and Linux.md
- Checklist step 3 (init-db) notes it performs v1.1 migration on existing DB
- Verify production item 7: re-audit populated cart after operator runs init-db on the real DB

### Task 2: docs/deploy/Windows.md + README.md (`c826ff5`)

- Windows.md: added `## Sao lưu (Backup)` section — Task Scheduler scheduling, `sqlite3.exe ".backup"` (WAL-safe), file copy method (`app.db` + `app.db-wal` + `app.db-shm`), `robocopy` uploads sync, 14-day retention guidance
- Windows.md section 3: added note that init-db performs idempotent v1.1 migration on existing v1.0 install (cost_price, legacy orders rebuild) — back up before running
- README.md (repo root): v1.1 description line `Đặt hàng qua giỏ hàng, theo dòng đơn và thống kê (v1.1).` placed directly under the restored `# StoreWeb` H1

### Task 3: docs/deploy/Linux.md (`c959493`)

- §6 Backup: noted `sqlite3 .backup` is WAL-safe (covers `-wal`/`-shm`); promoted uploads `rsync` into the routine daily cron line alongside DB backup; kept 14-day retention and `%%` escaping note verbatim
- §2: added init-db v1.1 upgrade note (idempotent cost_price, legacy orders rebuild, back up DB first — PLAT-05)

## Verification

All acceptance criteria and automated checks pass:

- `grep -c "## Migration v1.1\|## Sao lưu" docs/deploy/README.md` → 3 (both sections present)
- Migration v1.1 section mentions `flask --app wsgi init-db`, idempotent, `cost_price`, legacy-orders rebuild
- `grep -n "## Sao lữ" docs/deploy/Windows.md` matches; contains Task Scheduler, .backup/-wal, uploads
- Windows.md section 3 mentions v1.1 migration via init-db
- `grep -n "\-wal\|cost_price" docs/deploy/Linux.md` matches; §2 has v1.1 migration note
- `grep -c "%%F" docs/deploy/Linux.md` → 2 (crontab escaping preserved)
- `sed -n '1p' README.md` == `# StoreWeb`; README contains `v1.1` and `giỏ hàng`

## Threat Surface Scan

| Flag | File | Description |
|------|------|-------------|
| none | — | No new network endpoints, auth paths, file access patterns, or schema changes. Docs-only changes describing existing init-db behavior accurately. |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED
