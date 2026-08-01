# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-08-01
**Phases:** 4 | **Plans:** 12 | **Tasks:** 38 | **Sessions:** ~5

### What Was Built
- Flask app hoàn chỉnh: 3 blueprints (public/admin/auth), Flask-Login, Flask-WTF + CSRF, SQLite WAL + busy_timeout, image_utils, format_price.
- Admin CRUD đầy đủ với multi-image galleries (UUID files, thumbnails, delete-orphan cascade).
- Public catalog responsive + detail gallery + search không dấu (NFD+casefold) + Messenger contact.
- Deploy configs đầy đủ: waitress (Windows), gunicorn/systemd (Linux), nginx HTTPS + admin rate-limit.
- Milestone audit PASSED — 28/28 reqs, 6/6 E2E flows.

### What Worked
- Verify-first: mỗi plan có harness verify với temp-DB cô lập → 4/4 phase passed, review findings đều fixed.
- Velocity ổn định ~15min/plan (3.0 giờ cho 12 plans) — granularity coarse đúng cỡ cho dự án này.
- Quyết định giữ registry sạch: Phase 4 zero package mới, CSS 16KB < 20KB budget.

### What Was Inefficient
- Agent nền (UI researcher/auditor/integration-checker) chết nhiều lần vì 429 rate limit OPENCODE free tier → orchestrator phải tự làm inline UI-SPEC/UI-REVIEW/integration-check.
- CLI `milestone.complete` trích accomplishments sai (bắt bug notes thay vì SUMMARY one-liners) → phải sửa tay MILESTONES.md.
- Phase 2 verification còn `human_needed` (3 visual UAT items) — defer qua close.

### Patterns Established
- Agent nền cần chỉ thị retry-on-429; việc nhỏ (UI-SPEC, UI-REVIEW, integration check) làm inline khi agent chết quá nhiều.
- Verify harness DB isolation: Flask-SQLAlchemy tạo engine eager — phải dispose+rebuild `db._app_engines[app][None]` để cô lập temp DB.
- Commit từng file cụ thể, không `git add .`; sau Write file dài phải xác minh (đếm dòng / grep marker cuối).
- Không bao giờ Read file `.output` của agent nền (transcript JSONL tràn context).

### Key Lessons
1. Retry-on-429 + inline fallback cho agent nền — đừng chờ agent chết 3 lần mới tự làm.
2. Harness verify phải cô lập DB từ đầu; eager engine của Flask-SQLAlchemy là cái bẫy.
3. Deferral item cần ghi rõ nguồn (file + status) để close sau không phải truy vết lại.

### Cost Observations
- Model: OPENCODE free tier (429 rate-limit thường xuyên) — retry là cần thiết.
- Sessions: ~5 (mỗi phase 1-2 session + pause/resume).
- Notable: 12 plans / 3.0 giờ execute — hiệu quả cao nhờ verify-first + granularity coarse.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | ~5 | 4 | Verify-first + inline fallback cho agent nền khi 429 |

### Cumulative Quality

| Milestone | Plans | Verified | Review Findings Fixed |
|-----------|-------|----------|------------------------|
| v1.0 | 12 | 12/12 (100%) | 100% (0 HIGH còn mở) |

### Top Lessons (Verified Across Milestones)

1. Verify-first với temp-DB cô lập là thứ giữ milestone sạch — mỗi plan phải có harness.
2. Agent nền không tin cậy trên tier free — làm việc nhỏ inline, agent cho việc lớn.
