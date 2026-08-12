---
phase: 09-polish-deploy
plan: 01
subsystem: UI polish + revert restoration
tags: [css, templates, polish, revert, v1.1]
dependency_graph:
  requires: [09-UI-SPEC, 06-public-order-form]
  provides: [polished-cart-checkout-markup, restored-readme-h1, restored-form-help-text]
  affects: [public/cart, public/_checkout_form, admin/products/form.html, README.md]
tech_stack:
  added: []
  patterns: [jinja2-templates, hand-written-css, flask-wtf]
key_files:
  created: []
  modified:
    - app/static/css/style.css
    - app/templates/public/cart.html
    - app/templates/public/_checkout_form.html
decisions:
  - "F-04 (order-detail line-total accent) is verify-only: the shared .data-table .line-total rule is the intended contract across cart and order-detail; no code change."
  - "R-01 and R-02 were already at committed baseline on worktree creation — no edits needed, only verification."
metrics:
  duration: 4 min
  completed_date: "2026-08-03T04:24:00Z"
  tasks: 3
  files: 3
---

# Phase 9 Plan 1: UI Polish Contract Application Summary

Applied the locked Phase 9 UI polish contract (09-UI-SPEC.md F-01..F-06, R-01, R-02) to the v1.1 cart/checkout surfaces and restored two stray uncommitted reverts. No new features, no redesign, no new CSS tokens, no new dependencies.

## Tasks Completed

| # | Task | Status | Commit | Files |
|---|------|--------|--------|-------|
| 1 | CSS polish F-01, F-02, F-03, F-06 | DONE | `69a7697` | app/static/css/style.css |
| 2 | Template polish F-02, F-05, F-06 | DONE | `65b196d` | cart.html, _checkout_form.html |
| 3 | Restore reverts R-01, R-02 | DONE (verify-only) | `69a7697` | README.md, form.html (already at baseline) |

## Changes Applied

### Task 1: CSS polish (`69a7697`)

In the Phase 6 section of `app/static/css/style.css`:

- **F-01** — `.cart-actions { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; }` — added `flex-wrap: wrap;` (no media query, inherited gap/spacing unchanged).
- **F-02** — added `.cart-thumb { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; vertical-align: middle; }` (new rule, NOT reusing `.thumb` at line 211 which is 48px).
- **F-03** — `.cart-badge` `line-height: 1.5;` → `line-height: 1;` (only property changed; no other `.cart-badge` edits).
- **F-06** — added `.checkout-form .btn { width: 100%; max-width: 320px; }`.
- **F-04 (verify-only)** — confirmed `.data-table .line-total { font-weight: 600; color: var(--accent); font-variant-numeric: tabular-nums; }` is byte-identical and shared by both cart (line 38) and order-detail (detail.html line 32). No change made.

No new hex values introduced (diff shows only the four rule changes).

### Task 2: Template polish (`65b196d`)

- **F-02** — `cart.html:24`: replaced inline `style="object-fit: cover; border-radius: 4px; vertical-align: middle;"` with `class="cart-thumb"`. Preserved `src`, `alt="{{ item.product.name }}"`, and `width="80" height="80"` attributes.
- **F-05** — `cart.html:51`: `<span class="cart-total-label">Tổng cộng:</span>` → `<span class="cart-total-label">Tổng cộng</span>` (dropped trailing colon, matching detail.html:38).
- **F-06** — `_checkout_form.html:22`: removed `style="width: 100%; max-width: 320px;"` from the submit button; `.checkout-form .btn` CSS rule supplies the width.
- Empty-state branch (lines 62-68) left byte-identical.

Both files now contain zero inline `style=` attributes.

### Task 3: Revert restoration (verify-only)

- **R-01** — `README.md:1` is `# StoreWeb` (already at committed baseline).

Both `git diff README.md` and `git diff app/templates/admin/products/form.html` are empty — reverts already clean on worktree creation. No edits needed.

## Verification

All acceptance criteria from the plan pass:

- `flex-wrap: wrap` present in `.cart-actions` rule.
- `.cart-thumb` appears exactly once in style.css; `width: 80px; height: 80px;` confirmed.
- `.cart-badge` block contains `line-height: 1;`, not `1.5`.
- `.checkout-form .btn` appears exactly once; rule body is `width: 100%; max-width: 320px;`.
- `.data-table .line-total` rule at line 453 is byte-identical (accent 600 + tabular-nums).
- No new hex values in the style.css diff.
- `class="cart-thumb"` present on cart.html:24; no `style=` on that line.
- `Tổng cộng</span>` (no colon) on cart.html:51.
- `_checkout_form.html:22` button has no `style=` attribute.
- Zero `style=` matches across both template files.
- `README.md:1` is exactly `# StoreWeb`.
- `git diff --quiet README.md app/templates/admin/products/form.html` → clean.
- `grep -n "Trạng thái tự động"` matches one line with `&gt;` and curly quotes.
- App boots: `SECRET_KEY=test python -c "from wsgi import app; ..."` → app imports OK; with temp DB, `GET /` → 200, `GET /login` → 200.
- `git diff --stat HEAD` shows only the intended files changed (style.css, cart.html, _checkout_form.html).

## Deviations from Plan

None — plan executed exactly as written. R-01 and R-02 required no edits because the worktree was created from a baseline commit (`5fc82f5`) that already had both files in their committed state.

## Threat Surface Scan

| Flag | File | Description |
|------|------|-------------|
| none | — | No new network endpoints, auth paths, file access patterns, or schema changes. CSS-only + static template markup changes using inherited tokens. |

## Known Stubs

None. All changes wire real CSS rules and real template markup; no placeholders, empty values, or TODOs introduced.

## Self-Check

- `app/static/css/style.css` — FOUND
- `app/templates/public/cart.html` — FOUND
- `app/templates/public/_checkout_form.html` — FOUND
- Commit `69a7697` — FOUND
- Commit `65b196d` — FOUND
## Self-Check: PASSED
