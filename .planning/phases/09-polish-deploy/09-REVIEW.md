---
phase: 09-polish-deploy
reviewed: 2026-08-03T12:30:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - README.md
  - app/static/css/style.css
  - app/templates/public/_checkout_form.html
  - app/templates/public/cart.html
  - docs/deploy/Linux.md
  - docs/deploy/README.md
  - docs/deploy/Windows.md
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 9: Code Review Report

**Reviewed:** 2026-08-03T12:30:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Phase 9 is a polish + deploy-docs close-out phase. The changes touch README, CSS, two public templates, and deploy documentation. The CSS and template changes are correct and consistent — new CSS classes match their template usage, and inline styles were properly migrated to stylesheet rules.

The deploy documentation introduces a v1.0-to-v1.1 migration section and backup instructions. Cross-referencing the deploy docs against `app/db.py` (`init_db_command`) confirms the migration behavior is accurately described: the `ALTER TABLE products ADD COLUMN cost_price` guard, the legacy `orders` table detection via `product_name` column, the empty-table rebuild vs. data-preserving error, and the admin upsert are all correctly documented.

However, the Windows.md backup section contains a buggy line that executes a `.db` file as a command, and both platform backup instructions diverge on directory-creation prerequisites. These are real defects that could cause silent backup failures.

## Critical Issues

None found. No security vulnerabilities, data-loss paths, or behavioral regressions in the application code changes.

## Warnings

### WR-01: Windows backup section contains a dead line that executes a database file as a command

**File:** `docs/deploy/Windows.md:107`

**Issue:**
The batch snippet in the backup section begins with:

```bat
"C:\path\to\storewweb\data\app.db" > nul 2>&1
```

On Windows, a bare quoted file path is interpreted as a command to execute. Since `app.db` is not an executable, Windows produces an error (`'app.db' is not recognized as an internal or external command...`). The `> nul 2>&1` redirection silently swallows that error. This line serves no purpose — it is neither a `REM` comment, an `echo`, nor a validity check. It is likely an accidental leftover.

**Fix:**
Remove the line entirely. If a verification step is desired, replace it with a proper existence check:

```bat
if not exist "C:\path\to\storewweb\data\app.db" echo Database file not found & exit /b 1
sqlite3.exe "C:\path\to\storewweb\data\app.db" ".backup C:\backups\app-%date:~-4,4%%date:~-10,2%%date:~-7,2%.db"
```

### WR-02: Windows.md backup destination directory `C:\backups` is never created

**File:** `docs/deploy/Windows.md:104-123` (and contrast with `docs/deploy/Linux.md:134`)

**Issue:**
The sqlite3 `.backup` command writes to `C:\backups\app-YYYYMMDD.db`. The sqlite3 CLI does **not** create parent directories — if `C:\backups` does not exist, the backup command fails silently (especially problematic under Task Scheduler, where stdout/stderr are not visible). Linux.md correctly includes `mkdir -p /srv/backups` before its cron backup command (line 134), but Windows.md has no equivalent step.

**Fix:**
Add a directory-creation step before the backup command, or instruct the user to create it. For example:

```bat
if not exist C:\backups mkdir C:\backups
sqlite3.exe "C:\path\to\storewweb\data\app.db" ".backup C:\backups\app-%date:~-4,4%%date:~-10,2%%date:~-7,2%.db"
```

### WR-03: `data/` directory creation not instructed in Windows install steps

**File:** `docs/deploy/Windows.md:13-20` (contrast with `docs/deploy/Linux.md:30`)

**Issue:**
Linux.md Step 1 explicitly creates the data directory: `sudo mkdir -p /srv/storewweb/data /srv/storewweb/app/static/uploads`. Windows.md's install section (Step 1) does not mention creating `data\`. While the repo ships with `data/.gitkeep` (so the directory survives cloning), the Windows instructions use the template path `C:\path\to\storewweb\data\app.db` and never tell a Windows user to ensure `data\` exists. If a user copies files manually or runs in a context where `.gitkeep` was stripped, `flask init-db` fails with `unable to open database file`.

**Fix:**
Add a note in Windows.md Step 1 or Step 3 to ensure the `data\` directory exists before running `flask init-db`:

```bat
if not exist data mkdir data
```

## Info

### IN-01: `%date%` substring formatting in Windows backup is locale-dependent

**File:** `docs/deploy/Windows.md:108`

**Issue:**
The backup filename uses `%date:~-4,4%%date:~-10,2%%date:~-7,2%` to produce `YYYYMMDD`. This works only on en-US locale Windows, where `%date%` returns a format like `Sun 08/03/2026`. On a Vietnamese or other non-en-US locale, the date string layout differs and the substrings may yield incorrect digits or garbage characters in the filename. The Linux equivalent (`$(date +%F)`) is locale-independent by design.

**Fix (optional):**
Add a brief note that en-US locale is assumed, or use a locale-robust approach via PowerShell:

```bat
sqlite3.exe "%~dp0data\app.db" ".backup C:\backups\app-%%DATE:~0,4%%%%DATE:~5,2%%%%DATE:~8,2%.db"
```

Or use `wmic` / PowerShell date formatting. At minimum, add a comment: `# en-US locale assumed; adjust %date% slicing for other locales.`

### IN-02: Redundant `FLASK_APP` env var alongside `--app wsgi` in migration docs

**File:** `docs/deploy/README.md:46` and `docs/deploy/Windows.md:43`

**Issue:**
The migration command blocks set `FLASK_APP=wsgi` and then invoke `flask --app wsgi init-db`. The `--app wsgi` flag already overrides `FLASK_APP`, making the `set FLASK_APP=wsgi` line redundant. This is harmless but adds noise and could confuse a reader into thinking both are required.

**Fix (optional):**
Remove the `set FLASK_APP=wsgi` line from the Windows migration block, or remove the `--app wsgi` flag and rely solely on the env var. Pick one approach and use it consistently across Windows.md, Linux.md, and the deploy README.md.

## Structural Findings (fallow)

No `<structural_findings>` block was provided by the workflow.

---

_Reviewed: 2026-08-03T12:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
