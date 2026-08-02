---
phase: 07-admin-order-tracking
plan: 03
subsystem: admin-orders
type: execute
tags: [admin, orders, status-transition, forward-only, ord-08, ord-09, stepper]

# Dependency graph
requires:
  - phase: 07-admin-order-tracking
    provides: ORDER_STATUSES, _order_total, order_badge_class, order_detail route + detail.html background, strftime filter, .badge-order-* badges
provides:
  - TRANSITION_MAP constant (server-side forward-only status transition map)
  - admin.update_order_status POST route (POST /admin/orders/<id>/status)
  - Status section in detail.html (stepper + transition buttons + terminal notes)
  - CSS .order-progress stepper + .order-terminal
affects: [Phase 7 remaining (stats page), Phase 8 stats]

# Tech tracking
tech-stack:
  added: []  # no new dependencies
  patterns:
    - Server-side single-source-of-truth transition map validated against client-supplied next_status
    - CSRF-hidden-form pattern (hidden csrf_token + hidden next_status per transition button)
    - CSS-only progress stepper with ::before connectors (no icon glyphs)
    - One POST form per valid transition (not dropdown) — map has <=1 forward step

key-files:
  created:
    - app/templates/admin/orders/detail.html (extended)
  modified:
    - app/admin.py (TRANSITION_MAP + update_order_status)
    - app/templates/admin/orders/detail.html (status section)
    - app/static/css/style.css (.order-progress + .order-terminal)

key-decisions:
  - "CSRF-hidden-form pattern (not OrderStatusForm): each transition button is a separate POST form with hidden csrf_token + hidden next_status; CSRFProtect app-wide validates; OrderStatusForm would be boilerplate for 1 hidden field — app/forms.py untouched"
  - "Stepper renders 4 steps for non-terminal; Đã nhận shows all-done stepper + terminal note; Đã hủy shows NO stepper, only terminal note (cancelled is outside the forward chain)"
  - "Stepper position computed via flow.index(order.status) + loop.index0; current gets is-current + aria-current=step, prior steps is-done, future idle"
  - "Button labels explicit verb+target: 'Chuyển sang: {next_status}' (not 'Cập nhật')"
  - "Cancel (Hủy đơn) only rendered for Chờ xác nhận + Đã gói per forward-only rule; Đã gửi/Đã nhận cannot cancel"

patterns-established:
  - "TRANSITION_MAP.get(order.status, set()) fail-safe: unknown status -> empty set -> all transitions rejected"
  - "Invalid transition: flash error + redirect, no DB commit, no 500"

requirements-completed: [ORD-08, ORD-09]

# Metrics
duration: 8 min
completed: 2026-08-02
---

# Phase 7 Plan 3 Summary

**Forward-only order status transitions (ORD-08/ORD-09): server-side TRANSITION_MAP + POST route + detail page stepper with per-status transition buttons, zero new dependencies**

## Performance

- **Duration:** 8 min
- **Started:** 2026-08-02T12:40:20Z
- **Completed:** 2026-08-02T12:48:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `TRANSITION_MAP` constant in `app/admin.py` — single source of truth for forward-only status flow (Chờ xác nhận → Đã gói → Đã gửi → Đã nhận; + Đã hủy from first two; Đã nhận/Đã hủy terminal)
- `POST /admin/orders/<int:order_id>/status` route via `update_order_status()` — validates `next_status` against `TRANSITION_MAP[order.status]` server-side; invalid/backward/cancel-from-shipped/terminal all rejected with flash error + redirect, no DB change, no 500
- "Cập nhật trạng thái" section appended to detail.html — `.order-progress` 4-step stepper (is-done/is-current/aria-current) + per-status transition buttons (Chuyển sang: {next}) with hidden csrf_token + hidden next_status; terminal notes for Đã nhận ("Đơn đã hoàn thành.") and Đã hủy ("Đơn đã bị hủy.")
- CSS stepper appended to style.css — `.order-progress` flex row + `li + li::before` connector, `.dot` (12px, done #059669 / current #2563EB + #DBEAFE ring), `.order-terminal` muted

## Task Commits

Each task was committed atomically:

1. **Task 1: TRANSITION_MAP + update_order_status POST route** - `dcd5896` (feat)
2. **Task 2: Status section in detail.html** - `0e76b1e` (feat)
3. **Task 3: CSS order-status stepper** - `3de0f18` (feat)

## Files Created/Modified

- `app/admin.py` - Added `TRANSITION_MAP` constant after `ORDER_STATUSES`; added `update_order_status()` POST route after `order_detail()`
- `app/templates/admin/orders/detail.html` - Appended `.order-section` "Cập nhật trạng thái" at end of `.admin-card.order-detail` (after Thời gian section)
- `app/static/css/style.css` - Appended `.order-progress` + state variants + `.order-terminal` after `.data-table .unit-price`

## Decisions Made

- CSRF-hidden-form pattern over OrderStatusForm: each valid transition renders as its own POST form with `<input type="hidden" name="csrf_token">` + `<input type="hidden" name="next_status">`; CSRFProtect (app-wide, `csrf.init_app(app)` at `__init__.py:54`) validates token before route hits — no manual CSRF check in route. OrderStatusForm would add a FlaskForm for 1 hidden field with no validation benefit.
- Stepper position via Jinja `flow.index(order.status)` + `loop.index0` comparison: steps before current = `.is-done`, current = `.is-current` + `aria-current="step"`, future = idle.
- Đã nhận terminal: all 4 steps `.is-done` + note "Đơn đã hoàn thành." (keeps stepper visible to show full journey completed).
- Đã hủy terminal: NO stepper rendered — only `<p class="order-terminal">Đơn đã bị hủy.</p>` (cancelled is outside forward chain; showing empty stepper misrepresents it).
- Cancel button ("Hủy đơn") only rendered for Chờ xác nhận + Đã gói per forward-only rule; Đã gửi cannot be cancelled (no downward transitions from shipped).

## Deviations from Plan

None - plan executed exactly as written.

### Auto-fixed Issues

1. **[Rule 1 - Bug] Removed duplicate `onsite=` attribute in cancel form**
   - **Found during:** Task 2 (detail.html status section)
   - **Issue:** While writing the Đã gói cancel form, a stray duplicate attribute `onsite=` was left alongside `onsubmit=` — invalid HTML that browsers ignore but is malformed
   - **Fix:** Removed the erroneous `onsite=` attribute; single `onsubmit="return confirm('...')` remains
   - **Files modified:** app/templates/admin/orders/detail.html
   - **Verification:** Task 2 verify script (TASK_OK) confirms cancel form renders correctly
   - **Committed in:** 0e76b1e (part of Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Trivial malformed-attribute fix; no scope creep.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Threat Surface

No new threat surface beyond the plan's `<threat_model>` (`app/admin.py` POST route at admin browser → status endpoint). CSRF via Flask-WTF app-wide (T-07-02), server-side next_status whitelist (T-07-01), order_id lookup with missing-order flash (T-07-03), admin-only via `_protect_admin` before_request (T-07-04), stepper render derived from `order.status` but server is source of truth (T-07-05) — all mitigations implemented per plan.

## Stub Check

No stubs. All status values source from `order.status` (DB String column), all buttons wire to real `admin.update_order_status` endpoint, all stepper states derive from `TRANSITION_MAP`.

## Known Stubs

None.

## Next Phase Readiness

- Plan 07-03 complete: full forward-only status flow from list → detail → transition → redirect.
- Remaining in Phase 7 (if any): Phase 8 stats page will reuse `TRANSITION_MAP` and `_order_total` for revenue/cost aggregation.

---

*Phase: 07-admin-order-tracking*
*Completed: 2026-08-02*
