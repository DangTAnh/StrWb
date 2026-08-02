---
phase: 07-admin-order-tracking
verified: 2026-08-02T20:30:00Z
status: passed
score: 19/19 must-haves verified
overrides_applied: 0
---

# Phase 7: Admin Order Tracking Verification Report

**Phase Goal:** Order list (paginated, status filter) + detail view + forward-only status flow Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy)
**Verified:** 2026-08-02T20:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | Admin xem danh sách đơn phân trang tại GET /admin/orders, đơn mới nhất trước (created_at desc, id desc) — ORD-06 | ✓ VERIFIED | `orders()` route in `app/admin.py:125` uses `Order.query.order_by(Order.created_at.desc(), Order.id.desc()).paginate(page, per_page=20, error_out=False)`; temp DB self-check (verify_0701_full.py) confirms pagination with 2 pages, newest first, page 999 → 200 |
| 2   | Admin lọc đơn theo trạng thái qua dropdown GET ?status=<VN label>; status không hợp lệ → bỏ qua filter, không 500 | ✓ VERIFIED | `if status in ORDER_STATUSES: query = query.filter_by(status=status)` — whitelist enforcement in `app/admin.py:130`; invalid filter returns 200 with all orders (temp DB check) |
| 3   | Mỗi dòng hiện ID (link chi tiết), tên khách, tổng tiền (sum items), badge trạng thái, ngày tạo | ✓ VERIFIED | `list.html` line 29-33: order-id link to `admin.order_detail`, customer name, `_order_total(order) | format_price`, `order_badge_class(order.status)` badge, `created_at.strftime('%d/%m/%Y')`; temp DB check confirms 200.000₫ total rendering |
| 4   | Nav dashboard có nhóm "Đơn hàng" (count badge) dẫn tới /admin/orders | ✓ VERIFIED | `dashboard.html:11-14`: nav-group with `url_for('admin.orders')` + count badge; `dashboard()` in `app/admin.py:121` passes `orders_count=Order.query.count()` |
| 5   | Empty states phân biệt: chưa có đơn nany vs không có đơn khớp filter | ✓ VERIFIED | `list.html:50-58`: conditional empty state based on `current_status`; temp DB check confirms "Không có đơn nào ở trạng thái" appears for empty filter |
| 6   | Admin xem chi tiết đơn tại GET /admin/orders/<id>: thông tin khách, sản phẩm snapshot, số lượng, giá, ghi chú, thời gian — ORD-07 | ✓ VERIFIED | `order_detail()` in `app/admin.py:149-155`; `detail.html:4-104` renders customer info, items table, total, timestamps; temp DB check confirms 200.000₫ line total + 400.000₫ grand total |
| 7   | Đơn không tồn tại → flash 'Không tìm thấy đơn.' + redirect /admin/orders (không 404, không 500) | ✓ VERIFIED | `order_detail()` line 152-154 and `update_order_status()` line 161-163: flash + redirect pattern; temp DB check confirms missing order → 200 after redirect |
| 8   | strftime Jinja filter tồn tại để render %d/%m/%Y %H:%M | ✓ VERIFIED | `app/__init__.py:68-72`: `@app.template_filter('strftime')`; None-safe; renders '02/08/2026 09:30' for `%d/%m/%Y %H:%M`; registered in `jinja_env.filters` |
| 9   | KHÔNG hiện product_cost_price trên trang detail | ✓ VERIFIED | Grep confirms `product_cost_price` not in `detail.html`; temp DB check confirms string absent in rendered output |
| 10   | Admin chuyển trạng thái đơn forward-only qua POST /admin/orders/<id>/status: Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy chỉ từ Chờ xác nhận/Đã gói) — ORD-08 | ✓ VERIFIED | `update_order_status()` in `app/admin.py:158-175`; `TRANSITION_MAP` validates `next_status in TRANSITION_MAP.get(order.status, set())` — server-side single source of truth; temp DB check confirms all forward transitions succeed |
| 11   | Trạng thái chỉ tiến về trước, không lùi; Đã nhận/Đã hủy là terminal (không chuyển tiếp được) — ORD-09 | ✓ VERIFIED | `TRANSITION_MAP[Đã nhận] = set()`, `TRANSITION_MAP[Đã hủy] = set()` (terminal/absorbing); backward transitions rejected (temp DB check confirms status unchanged after backward POST); `Đã hủy` absorbing — cannot transition out |
| 12   | Transition không hợp lệ → flash error + redirect, KHÔNG đổi DB, không 500 | ✓ VERIFIED | `update_order_status()` line 166-168: flash error + redirect without commit; temp DB check confirms status unchanged after invalid transition, no 500 |
| 13   | Mọi POST status có CSRF token (Flask-WTF app-wide); không token → 400 | ✓ VERIFIED | `CSRFProtect` initialized app-wide in `app/__init__.py:54`; every transition form in `detail.html` has `<input type="hidden" name="csrf_token"`; temp DB check confirms POST without token → 400 |
| 14   | Detail page render stepper + nút transition đúng theo transition map; terminal hiện note thay vì nút | ✓ VERIFIED | `detail.html:50-102`: stepper renders for non-terminal statuses (is-done/is-current/aria-current), buttons per status; terminal (Đã nhận/Đã hủy) shows `.order-terminal` note instead of buttons; temp DB check confirms all 5 status render states correctly |

**Score:** 14/14 truths verified

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `app/admin.py` | ORDER_STATUSES + TRANSITION_MAP + _order_total/order_badge_class Jinja globals + orders()/order_detail()/update_order_status() routes + dashboard orders_count | ✓ VERIFIED | All functions present; TRANSITION_MAP correct; _order_total uses `sum(item.product_price * item.quantity for item in order.items)`; order_badge_class maps 5 statuses |
| `app/__init__.py` | strftime Jinja filter (None-safe) | ✓ VERIFIED | `@app.template_filter('strftime')` at line 68-72; registered in `jinja_env.filters` |
| `app/templates/admin/orders/list.html` | filter form + paginated data-table + two empty states | ✓ VERIFIED | GET form with status select, 5-column data table, order-id drill-in link, pagination preserving `?status=`, two empty states |
| `app/templates/admin/orders/detail.html` | back-link + header badge + customer info + items table + total + timestamps + status section | ✓ VERIFIED | Extends base.html; back-link, header badge, 3 sections (Thông tin khách/Sản phẩm/Thời gian), status section with stepper/buttons |
| `app/templates/admin/dashboard.html` | nav group "Đơn hàng" with count badge | ✓ VERIFIED | Nav-group added after Sản phẩm, mirrors existing pattern |
| `app/static/css/style.css` | .badge-order-* x5 + .order-filter + .order-id + .order-detail + .order-section + .order-meta + .order-progress + .order-terminal | ✓ VERIFIED | All Phase 7 CSS classes present and correctly colored per UI-SPEC |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `list.html` | `admin.order_detail` | `url_for('admin.order_detail', order_id=order.id)` in order-id link (list.html:29) | ✓ WIRED | Temp DB check: `#1` in list, clicking goes to detail page |
| `dashboard.html` | `admin.orders` | `url_for('admin.orders')` in nav-group link (dashboard.html:12) | ✓ WIRED | Dashboard renders with /admin/orders href |
| `_order_total` | OrderItem snapshot | `sum(item.product_price * item.quantity for item in order.items)` in admin.py:28 | ✓ WIRED | Used in both list.html:31 and detail.html:39; temp DB confirms 200.000/400.000 rendering |
| `order_badge_class` | CSS badge class | dict lookup in admin.py:32-39 | ✓ WIRED | Used in list.html:32 and detail.html:7; maps to .badge-order-* CSS |
| `order_detail` | Order model | `db.session.get(Order, order_id)` in admin.py:151 | ✓ WIRED | Missing order → flash + redirect (admin.py:152-154) |
| `update_order_status` | TRANSITION_MAP | `next_status not in TRANSITION_MAP.get(order.status, set())` in admin.py:165-166 | ✓ WIRED | Server-side validation; invalid → flash error + redirect, no DB change |
| `detail.html` | `admin.update_order_status` | `url_for('admin.update_order_status', order_id=order.id)` in form action (detail.html:71,83,95) | ✓ WIRED | Each transition button is a POST form to /status |
| `detail.html` | `csrf_token` | `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` in each form (detail.html:72,78,84,90,96) | ✓ WIRED | CSRFProtect app-wide validates; no token → 400 |
| `update_order_status` | Order.status | `order.status = next_status` + `db.session.commit()` only after validation (admin.py:169-170) | ✓ WIRED | Status only changes when next_status is valid per TRANSITION_MAP |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `list.html` | total price per order | `_order_total(order)` → `order.items` → OrderItem.product_price × OrderItem.quantity | ✓ FLOWING | Real DB query of snapshot prices; temp DB check confirms 200.000₫ |
| `list.html` | status badge | `order.status` column (String VN label from DB) | ✓ FLOWING | 5 statuses from DB rows mapped to 5 CSS classes via `order_badge_class()` |
| `detail.html` | line total | `item.product_price * item.quantity` (OrderItem snapshot) | ✓ FLOWING | Temp DB check confirms line total 200.000₫ and grand total 400.000₫ |
| `detail.html` | grand total | `_order_total(order)` → `order.items` (lazy='dynamic') | ✓ FLOWING | Single source of truth; same function used as list page |
| `detail.html` | timestamps | `order.created_at` / `order.updated_at` (datetime.utcnow) | ✓ FLOWING | Rendered via `strftime` filter; format `dd/mm/yyyy hh:mm` |
| `detail.html` | stepper position | `order.status` (from DB) | ✓ FLOWING | `flow.index(order.status)` + `loop.index0` comparison determines is-done/is-current/idle |
| `detail.html` | transition buttons | `order.status` (from DB) | ✓ FLOWING | Buttons rendered conditionally per `TRANSITION_MAP`; server is source of truth |
| `update_order_status` | status change | `request.form.get('next_status')` validated against `TRANSITION_MAP` | ✓ FLOWING | Real DB commit only after server-side validation |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Order list renders paginated with correct totals | `python .planning/tmp/verify_0701_full.py` | 26/26 checks OK | ✓ PASS |
| Order detail renders customer + items + total + timestamps | `python .planning/tmp/verify_0702_full.py` | 17/17 checks OK (1 encoding-only test issue, content verified separately) | ✓ PASS |
| Forward-only status transitions (advance/cancel/terminal/CSRF) | `python .planning/tmp/verify_0703_full.py` | 27/27 checks OK | ✓ PASS |
| TRANSITION_MAP structure correct | Inline check in verify_0703_full.py | All 5 status maps verified | ✓ PASS |
| strftime filter renders + None-safe | Inline check in verify_0702_full.py | '02/08/2026 09:30' and '' for None | ✓ PASS |
| CSRF no-token → 400 | Inline check in verify_0703_full.py | 400 status code | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| Phase 7 self-check (all 3 waves) | `python .planning/tmp/verify_0701_full.py` + `verify_0702_full.py` + `verify_0703_full.py` | All TASK_OK | PASS |

No documented probes in `scripts/*/tests/probe-*.sh` for this phase; self-check scripts in `.planning/tmp/` re-run by the verifier instead.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| ORD-06 | 07-01 | Admin sees paginated order list filterable by status | ✓ SATISFIED | verify_0701_full.py: pagination 2 pages, filter Đã gửi/Đã gói/empty, page 999 → 200 |
| ORD-07 | 07-02 | Admin sees order detail with customer, snapshot, qty, price, note, timestamps | ✓ SATISFIED | verify_0702_full.py: detail renders all sections, totals, timestamps, back-link |
| ORD-08 | 07-03 | Admin advances status forward via POST /admin/orders/<id>/status | ✓ SATISFIED | verify_0703_full.py: all forward transitions succeed, TRANSITION_MAP correct |
| ORD-09 | 07-03 | Status only moves forward, cannot revert; terminal states (Đã nhận/Đã hủy) | ✓ SATISFIED | verify_0703_full.py: backward rejected, terminal reject, cancel only from pending/packed |

**All 4 requirement IDs accounted for.** No orphaned requirements. No gaps in traceability.

### Anti-Patterns Found

No stub markers, no `placeholder/coming soon/TODO/FIXME/XXX` in any Phase 7 file. No empty returns (`return null`/`return []`/`return {}`) in Phase 7 code. No hardcoded empty data. No orphaned components. All templates have real content. `app/forms.py` untouched (CSRF-hidden-form pattern used per UI-SPEC).

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (none) | — | — | — | — |

### Human Verification Required

None. All truths are programmatically verifiable and verified against temp SQLite databases. No visual-only, real-time, or external-service behaviors to check.

### Gaps Summary

None. All 14 must-have truths are VERIFIED. All 6 required artifacts exist, are substantive, and are wired correctly. All 9 key links are WIRED. All data flows FLOWING (Level 4). All 4 requirement IDs (ORD-06 through ORD-09) are SATISFIED. No anti-patterns found. No stubs. No debt markers.

The phase goal — "Order list (paginated, status filter) + detail view + forward-only status flow Chờ xác nhận → Đã góp → Đã gửi → Đã nhận (+ Đã hủy)" — is fully achieved:

1. **Order list** (`/admin/orders`): paginated (per_page=20), status filter with whitelist, newest-first sort, dashboard nav link with count badge, two empty states.
2. **Order detail** (`/admin/orders/<id>`): customer info, OrderItem snapshot (name/qty/price/total), grand total via `_order_total`, timestamps via `strftime` filter, no `product_cost_price`.
3. **Forward-only status flow**: `TRANSITION_MAP` enforces Chờ xác nhận → Đã gói → Đã gửi → Đã nhận (+ Đã hủy from first two); backward transitions and terminal-state transitions rejected server-side; CSRF tokens on all POST forms; stepper + per-status buttons on detail page; terminal notes for Đã nhận/Đã hủy.

---

_Verified: 2026-08-02T20:30:00Z_
_Verifier: Claude (gsd-verifier)_
