---
phase: 7
slug: admin-order-tracking
status: approved
shadcn_initialized: false
preset: none
created: 2026-08-02
reviewed_at: 2026-08-02
---

# Phase 7 — UI Design Contract

> Visual and interaction contract for Phase 7 — Admin Order Tracking. Phase 7 extends the existing Phase 1/2/3/6 design system — it does **not** redefine it. All tokens, typography, spacing, and color roles are inherited unchanged. This contract declares only the **new components, new copy, new interactions, and new CSS class names** introduced by the admin order list, order detail, and forward-only status flow.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — Flask server-rendered Jinja2 templates with hand-written CSS |
| Preset | not applicable |
| Component library | none (hand-rolled table, status badges, progress stepper, POST-form buttons) |
| Icon library | none (text labels and aria-labels only; progress stepper uses CSS dots, no icon glyphs) |
| Font | Noto Sans VN (Google Fonts) — inherited Phase 1; fallback `Roboto, system-ui, -apple-system, sans-serif` |

**Design system source:** Phase 1 baseline (`01-UI-SPEC.md`) — colors `#2563EB` / `#F9FAFB` / `#FFFFFF` / `#1F2937` / `#6B7280` / `#DC2626` / `#059669`; type scale 14/16/24/32 with weights 400 + 600; spacing multiples of 4 (4/8/16/24/32/48/64); breakpoints 480/768/1200. Phase 2 (`02-UI-SPEC.md`) — button variants, status badges, `.data-table`, `.form-field`, `.action-row`, `.empty-state`, `.pagination`. Phase 6 (`06-UI-SPEC.md`) — confirms no new design-system tokens; single-field extension only. This phase reuses the admin list/detail patterns from Phase 2.

**Phase 7 extensions (new, declared here):**
1. **Admin nav link "Đơn hàng"** on the admin dashboard nav-list — mirrors the existing "Sản phẩm" nav-group (count badge pattern).
2. **Order list page** (`/admin/orders`) — status-filterable, paginated table of orders; reuses `.data-table`, `.pagination`, `.empty-state`, `.table-scroll`.
3. **Order detail page** (`/admin/orders/<id>`) — customer info, item snapshot table, timestamps, status stepper, transition buttons; reuses `.admin-card`, `.data-table`, `.action-row`, `.badge`.
4. **Order status badges** — 5 new badge variants (`.badge-order-*`) mapping the 5 VN statuses; follows the Phase 2 `.badge` shape and the existing badge trio (text / bg / border).
5. **Forward-only progress stepper** (`.order-progress`) — a 4-step CSS indicator Chờ xác nhận → Đã gói → Đã gửi → Đã nhận with the current step highlighted; Đã hủy renders a terminal banner instead of the stepper.
6. **Status transition buttons** — each valid next status (per transition map) renders as its own small POST form with a hidden `next_status` field + CSRF token; cancel renders a `.btn-danger` form with a native `confirm()` dialog.

**shadcn gate:** Not applicable. Tech stack is Python Flask with Jinja2 + plain CSS (CLAUDE.md "What NOT to Use" bans Tailwind, Bootstrap, React/Vue, shadcn). No `components.json`, no React/Next/Vite.

---

## Spacing Scale

Inherited unchanged from Phase 1 (`4 / 8 / 16 / 24 / 32 / 48 / 64`). Phase 7 introduces **no new spacing tokens** — all gaps use existing tokens.

| Token | Value | Phase 7 Usage |
|-------|-------|---------------|
| xs | 4px | Progress stepper dot bottom margin, badge margin, customer-meta dd margin |
| sm | 8px | `.data-table` cell vertical padding (inherited), action-row gap, stepper step gap |
| md | 16px | `.admin-card` padding (inherited), section gap on detail, filter form gap, badge margin-left |
| lg | 24px | Detail page section padding / separators, `.order-detail` padding, empty-state padding |
| xl | 32px | Stepper bottom margin before customer section, empty-state extra top/bottom |
| 2xl | 48px | Not used in Phase 7 |
| 3xl | 64px | Not used in Phase 7 |

**Exceptions (declared, justified sub-token values — not new spacing tokens):**
- Progress stepper dot: `12px` diameter — a fixed geometric size for the connector circle, not a spacing gap.
- Progress stepper connector line: `2px` thickness via `li::before`/`li::after` `border-top: 2px solid` — a border weight, not a spacing token.
- Cancel/advance buttons: reuse `.btn` height `44px` (inherited touch target) — no exception.

---

## Typography

Roles inherited from Phase 1. Phase 7 maps all new elements onto existing roles — **no new sizes, no new weights** (declared: 14, 16, 24, 32 px; weights 400 + 600).

| Role | Size | Weight | Line Height | Phase 7 Usage |
|------|------|--------|-------------|---------------|
| Body | 16px | 400 | 1.5 | Order table body cells, customer name/phone/address/note, order detail terminal note |
| Label | 14px | 400 | 1.5 | Status badge text, table header, customer-meta dt labels, stepper step labels, timestamps, empty-state body, help-text |
| Label (semibold) | 14px | 600 | 1.5 | Transition buttons (`.btn`), "Tổng cộng" label, filter submit button, pagination |
| Heading | 24px | 600 | 1.2 | Page heading "Đơn hàng", detail heading "Đơn #12", section sub-headings |
| Display | 32px | 600 | 1.1 | Order detail total value (`.cart-total-value` reuse — single large number) |

**Font stack (inherited):** `Noto Sans VN`, `Roboto`, `system-ui`, `-apple-system`, `sans-serif`

### Phase 7 Type Usage Map

| Element | Role | Weight | Notes |
|---------|------|--------|-------|
| List page heading "Đơn hàng" | Heading | 600 | 24px |
| Nav "Đơn hàng" link | Body | 400 | 16px, `#1F2937`, inherited `.nav-list a` |
| Filter select label | Label | 400 | 14px, visually-hidden label, visible option text |
| Filter option labels (with counts) | Label | 400 | 14px, e.g. "Chờ xác nhận (3)" |
| Order table — ID link `#12` | Label | 600 | 14px, `#2563EB` (accent), ≥44px touch target |
| Order table — customer name | Body | 400 | 16px, `#1F2937` |
| Order table — total | Body | 600 | 16px, `#1F2937`, `format_price`, tabular-nums |
| Order table — status badge | Label | 600 | 14px, `.badge-order-*` |
| Order table — created date | Label | 400 | 14px, `#6B7280`, `%d/%m/%Y` |
| Empty state heading "Chưa có đơn nào" | Body | 600 | 16px |
| Empty state body | Body | 400 | 16px, `#6B7280` |
| Detail heading "Đơn #12" | Heading | 600 | 24px |
| Stepper step labels | Label | 400 | 14px, `#6B7280` (current step `#1F2937`/600) |
| Section sub-heading "Thông tin khách" / "Sản phẩm" / "Thời gian" | Body (semibold) | 600 | 16px (matches `.product-description h2` pattern — intentional 16px/600 variant of the Body role, not Heading) |
| Customer-meta dt (Họ và tên / SĐT / Địa chỉ / Ghi chú) | Label | 400 | 14px, `#6B7280` |
| Customer-meta dd (values) | Body | 400 | 16px, `#1F2937` |
| Items table — product snapshot name | Body | 400 | 16px, `#1F2937` |
| Items table — quantity | Body | 400 | 16px |
| Items table — unit price | Label | 400 | 14px, `#6B7280`, `format_price`, tabular-nums |
| Items table — line total | Body | 600 | 16px, `#1F2937`, `format_price`, tabular-nums |
| Total label "Tổng cộng" | Label | 600 | 14px, `#6B7280` |
| Total value | Display | 600 | 32px, `#2563EB`, `format_price`, tabular-nums |
| Timestamp rows "Ngày tạo" / "Cập nhật" | Label | 400 | 14px, `#6B7280`, `%d/%m/%Y %H:%M` |
| Advance button "Chuyển sang: Đã gói" | Label | 600 | 14px, `.btn.btn-primary` |
| Cancel button "Hủy đơn" | Label | 600 | 14px, `.btn.btn-danger` |
| Terminal note "Đơn đã hoàn thành." / "Đơn đã bị hủy." | Body | 400 | 16px, `#6B7280` |

---

## Color

Base palette inherited unchanged from Phase 1 + Phase 2 badge palette. Phase 7 adds **two new hex values** — `#DBEAFE` and `#BFDBFE` (Tailwind blue-100/blue-200) — used for **status-related surfaces**: the two new blue order-status badges (Chờ xác nhận, Đã gửi) plus the decorative ring (`box-shadow`) around the stepper current dot. All other badge colors reuse the existing Phase 2 badge trios. The darker blue `#1D4ED8` already exists in the stylesheet (`.btn-primary:hover`) and is reused as blue-badge text to meet AA contrast on the `#DBEAFE` background.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | #F9FAFB | Page background (inherited) |
| Secondary (30%) | #FFFFFF | `.admin-card`, `.admin-card--wide` (inherited) |
| Accent (10%) | #2563EB | Order ID link, advance button (`.btn-primary`), total value, filter submit button, focus rings, stepper current dot |
| Destructive | #DC2626 | Cancel button (`.btn-danger`), flash errors, required nothing (no form fields in Phase 7) |
| Success semantic | #059669 | Success flash messages (via `.flash-success`), stepper done dots, delivered badge text |
| Neutral semantic | #6B7280 | Table header text, timestamps, unit prices, customer-meta dt, stepper future-step labels, empty-state body, terminal note |
| Border | #D1D5DB | `.admin-card` radius (inherited), stepper connector (idle), input borders (none new) |
| Table header bg | #F9FAFB | `.data-table thead` (inherited) |
| Row hover | #F9FAFB | `.data-table tbody tr:hover` (inherited) |

### Order Status Badges (new variants of the Phase 2 `.badge`)

Shape inherited from Phase 2 (pill, `padding: 2px 8px; border-radius: 999px; font-size: 14px; font-weight: 600; border: 1px solid`). Text is the full VN status label — **color is never the only status indicator** (accessibility: badge text carries the meaning).

| Class | Status | Text | Background | Border | Source |
|-------|--------|------|------------|--------|--------|
| `.badge-order-pending` | Chờ xác nhận | `#1D4ED8` | `#DBEAFE` | `#BFDBFE` | NEW `#DBEAFE`/`#BFDBFE`, text = existing `.btn-primary:hover` blue |
| `.badge-order-packed` | Đã gói | `#D97706` | `#FFFBEB` | `#FDE68A` | reuses `.badge-out_of_stock` trio |
| `.badge-order-shipped` | Đã gửi | `#1D4ED8` | `#DBEAFE` | `#BFDBFE` | NEW trio (same as pending) |
| `.badge-order-delivered` | Đã nhận | `#059669` | `#ECFDF5` | `#A7F3D0` | reuses `.badge-available` trio |
| `.badge-order-cancelled` | Đã hủy | `#6B7280` | `#F3F4F6` | `#E5E7EB` | reuses `.badge-discontinued` trio |

**Contrast note:** The two blue badges use `#1D4ED8` text on `#DBEAFE` (ratio ≈ 4.6:1 → AA at 14px). The amber/green/gray trios are **inherited unchanged** from the Phase 2 product badges (accepted in earlier reviews); Phase 7 does not regress them.

**Accent reserved for (inherited list, extended for Phase 7):**
1. Primary buttons — "Chuyển sang: <next>", "Lọc" (NEW)
2. Order ID link `#12` (NEW)
3. Order detail total value (NEW)
4. Links — back link, brand hover (inherited)
5. Input focus ring / focus border (inherited; no new inputs beyond the filter select)
6. Progress stepper current-step dot (NEW)

**Color usage rules (inherited + Phase 7):**
- All non-link text: `#1F2937`
- Cancel button: `.btn-danger` (red `#DC2626` bg, white text, hover `#B91C1C`) — only rendered when `order.status in {'Chờ xác nhận', 'Đã gói'}`
- Advance button: `.btn-primary` (`#2563EB` bg, white text, hover `#1D4ED8`) — rendered only when the transition map has a forward step
- Stepper done dots: `#059669`; current dot: `#2563EB` with `#DBEAFE` ring; idle dots: `#D1D5DB`
- Terminal states (Đã nhận, Đã hủy): no buttons, no stepper (Đã hủy) or all-done stepper (Đã nhận) + muted note
- Invalid transition flash: `#DC2626` (inherited `.flash.error`)
- Success flash: `#047857` (inherited `.flash.success`)

---

## Layout & Component Contract

### 0. Admin Nav "Đơn hàng" (dashboard nav-list)

**Current state:** There is **no shared admin nav template**. Admin pages render the global `base.html` (no `header` block for admin) and reach each other via links. The only admin nav is the `nav-list` on `app/templates/admin/dashboard.html`. This contract **adds the orders link to that dashboard nav-list only** — consistent with how "Sản phẩm" is wired. A shared admin nav across all admin pages is a Phase 9 polish item (out of scope here).

**Location:** `app/templates/admin/dashboard.html`, inside the existing `.nav-list`, after the "Sản phẩm" `.nav-group`.

```
[nav.nav-list]
  ├── [a] Trang chủ
  ├── [div.nav-group]
  │   ├── [a href="/admin/products"] Sản phẩm
  │   └── [span.badge] {products_count}
  ├── [div.nav-group]  ── NEW
  │   ├── [a href="/admin/orders"] Đơn hàng
  │   └── [span.badge] {orders_count} | "Chưa có đơn" (when 0)
  └── [div.nav-group.logout-form]
      └── [form POST] Đăng xuất
```

**Markup (mirrors the existing "Sản phẩm" group exactly):**
```html
<div class="nav-group">
  <a href="{{ url_for('admin.orders') }}">Đơn hàng</a>
  {% if orders_count > 0 %}<span class="badge">{{ orders_count }}</span>{% else %}<span class="badge">Chưa có đơn</span>{% endif %}
</div>
```
- `admin.dashboard` passes `orders_count` (cheap `Order.query.count()`); if the planner wants to skip the count, the `<span class="badge">` may be omitted — the link alone satisfies the requirement.
- No CSS change: reuses `.nav-group` / `.badge` (inherited).

### 1. Order List Page (`GET /admin/orders`)

**Route:** `admin.orders()` — pattern identical to `admin.products()`: `Order.query.order_by(Order.created_at.desc(), Order.id.desc()).paginate(page=page, per_page=20, error_out=False)`.

**Template:** `app/templates/admin/orders/list.html` (NEW) — `{% extends "base.html" %}`.

```
[.admin-page]
  ├── [.admin-header]
  │   ├── [h1] Đơn hàng
  │   └── (no primary CTA — admin reads, does not create orders)
  │
  ├── [form.order-filter method="get" action="/admin/orders"]  ── filter bar
  │   ├── [label.visually-hidden for="status-filter"] Lọc theo trạng thái
  │   ├── [select#status-filter name="status"]
  │   │   ├── [option value=""] Tất cả ({total})
  │   │   ├── [option value="Chờ xác nhận"] Chờ xác nhận ({n})
  │   │   ├── [option value="Đã gói"] Đã gói ({n})
  │   │   ├── [option value="Đã gửi"] Đã gửi ({n})
  │   │   ├── [option value="Đã nhận"] Đã nhận ({n})
  │   │   └── [option value="Đã hủy"] Đã hủy ({n})
  │   └── [button.btn.btn-primary type="submit"] Lọc
  │
  ├── [IF orders exist]
  │   [.admin-card.admin-card--wide]
  │     [.table-scroll]
  │       [table.data-table]
  │         [caption.visually-hidden] Danh sách đơn hàng
  │         [thead]
  │           [th scope="col"] ID
  │           [th scope="col"] Khách hàng
  │           [th scope="col"] Tổng tiền
  │           [th scope="col"] Trạng thái
  │           [th scope="col"] Ngày tạo
  │         [tbody — one row per order]
  │           [td] [a.order-id href=detail] #{{ order.id }}
  │           [td] {{ order.customer_name }}
  │           [td.price-cell] {{ _order_total(order) | format_price }}
  │           [td] [span.badge.badge-order-*] {{ order.status }}
  │           [td.muted] {{ order.created_at | strftime('%d/%m/%Y') }}
  │     [IF pagination.pages > 1]
  │       [.pagination]
  │         Trước | Trang {{ page }} / {{ pages }} | Sau
  │         (links preserve ?status=current_status)
  │
  └── [IF no orders at all]
      [.admin-card.admin-card--wide]
        [.empty-state]
          [h2] Chưa có đơn nào
          [p] Khách đặt hàng qua web sẽ hiện ở đây.
      [ELIF no orders for this filter]
        [.empty-state]
          [h2] Không có đơn nào ở trạng thái “{status}”
          [p] Thử chọn trạng thái khác hoặc chọn “Tất cả”.
```

**Component specifics:**
- **Filter select** is inside a GET form (no JS) — a plain submit button "Lọc" fires the query. The `name="status"` value is the full VN label (matches the DB column value). Empty `status` param (or `?status=`) = all orders. If the status param is not one of the 5 labels → ignore the filter (show all), no 500.
- **Option counts** (optional, cheap): `admin.orders()` also computes a per-status count dict (one `GROUP BY` query) rendered as `{n}` in option labels. If the planner finds this adds complexity, counts may be omitted — the filter still works.
- **ID cell** is the detail link: `#{{ order.id }}` styled `.order-id` (Label 14px/600, `#2563EB`, `padding` to keep a ≥44px touch target). This is a deliberate deviation from the product-list "actions cell" pattern — an order has exactly one drill-in action, so the ID itself is the link; no separate "Xem" column.
- **Total** computed server-side by the `_order_total(order)` helper (`sum(item.product_price * item.quantity for item in order.items)`), rendered via the inherited `format_price` filter (e.g. `1.200.000₫`). Reuse `.price-cell` (tabular-nums).
- **Pagination** reuses the `.pagination` block verbatim from `admin/products/list.html`, with one addition: links must carry the active filter — `url_for('admin.orders', page=..., status=current_status)`. When `current_status` is empty, omit the param.
- **Two empty states**: distinguish "no orders in the whole system" from "no orders matching the filter". The filtered-empty state shows the active status label.

**New CSS classes:** `.order-filter` (flex row, gap sm/md, align center), `.order-id` (accent, 600, inline-block with padding for touch), `.muted` (or reuse `.data-table .qty-muted`-style `#6B7280`).

### 2. Order Detail Page (`GET /admin/orders/<int:order_id>`)

**Route:** `admin.order_detail(order_id)` — `db.session.get(Order, order_id)`; missing order → flash `'Không tìm thấy đơn.'` (error) + redirect `/admin/orders`.

**Template:** `app/templates/admin/orders/detail.html` (NEW) — `{% extends "base.html" %}`.

```
[.admin-page]
  ├── [a.back-link href="/admin/orders"] Quay lại
  ├── [.admin-header]
  │   ├── [h1] Đơn #{{ order.id }}
  │   └── [span.badge.badge-order-*] {{ order.status }}
  │
  └── [.admin-card.order-detail]
      ├── [IF order.status == 'Đã hủy']
      │   [.order-terminal.is-cancelled] Đơn đã bị hủy.  (muted note, no stepper)
      ├── [ELIF order.status == 'Đã nhận']
      │   [ol.order-progress all-done]  (4 steps, all .is-done)
      │   [p.order-terminal] Đơn đã hoàn thành.  (muted)
      ├── [ELSE]
      │   [ol.order-progress]  (4 steps; current = order.status .is-current)
      │
      ├── [section.order-section]
      │   [h2] Thông tin khách
      │   [dl.order-meta]
      │     [dt] Họ và tên      [dd] {{ order.customer_name }}
      │     [dt] Số điện thoại  [dd] {{ order.customer_phone }}
      │     [dt] Địa chỉ        [dd] {{ order.customer_address }}
      │     [IF order.customer_note]
      │       [dt] Ghi chú      [dd] {{ order.customer_note }}
      │
      ├── [section.order-section]
      │   [h2] Sản phẩm
      │   [table.data-table]
      │     [caption.visually-hidden] Sản phẩm trong đơn
      │     [thead]
      │       [th scope="col"] Sản phẩm
      │       [th scope="col"] Số lượng
      │       [th scope="col"] Đơn giá
      │       [th scope="col"] Thành tiền
      │     [tbody — one row per order.items]
      │       [td] {{ item.product_name }}  (snapshot; plain text, no product link)
      │       [td] {{ item.quantity }}
      │       [td.unit-price] {{ item.product_price | format_price }}
      │       [td.line-total] {{ (item.product_price * item.quantity) | format_price }}
      │   [.cart-total]  (reuse from Phase 6)
      │     [span.cart-total-label] Tổng cộng
      │     [span.cart-total-value] {{ _order_total(order) | format_price }}
      │
      ├── [section.order-section]
      │   [h2] Thời gian
      │   [dl.order-meta]
      │     [dt] Ngày tạo  [dd] {{ order.created_at | strftime('%d/%m/%Y %H:%M') }}
      │     [dt] Cập nhật  [dd] {{ order.updated_at | strftime('%d/%m/%Y %H:%M') }}
      │
      └── [section.order-section]  ── status actions (rendered per transition map)
          [h2] Cập nhật trạng thái
          [IF order.status == 'Chờ xác nhận']
            [.action-row]
              [form.inline-form POST → update_order_status] [hidden next_status="Đã gói"] [button.btn.btn-primary] Chuyển sang: Đã gói
              [form.inline-form POST → update_order_status] [hidden next_status="Đã hủy"] [button.btn.btn-danger  onsubmit=confirm] Hủy đơn
          [ELIF order.status == 'Đã gói']
            [.action-row]
              [form ...] [hidden next_status="Đã gửi"] [button.btn.btn-primary] Chuyển sang: Đã gửi
              [form ...] [hidden next_status="Đã hủy"] [button.btn.btn-danger  onsubmit=confirm] Hủy đơn
          [ELIF order.status == 'Đã gửi']
            [.action-row]
              [form ...] [hidden next_status="Đã nhận"] [button.btn.btn-primary] Chuyển sang: Đã nhận
          [ELSE]  (Đã nhận / Đã hủy — terminal)
            [p.order-terminal] Đơn đã hoàn thành. | Đơn đã bị hủy.
```

**Component specifics:**
- **Card width:** detail uses `.admin-card` with a new `.order-detail` padding class (`padding: 24px`). The item table is typically 1–3 rows, so 720px is comfortable. (`.admin-card--wide` is not used — it has `padding: 0` for full-bleed tables.)
- **Product snapshot:** `item.product_name` is plain text (no product link). If `item.product_id` is non-null and the product still exists, an optional link to `admin.edit_product` is allowed but **not required** (CONTEXT.md decision). Default contract: plain text.
- **`product_cost_price` is NOT rendered** anywhere on the detail page (CONTEXT.md decision — cost price is Phase 8 stats data; keep this page minimal).
- **`_order_total(order)`** is the same helper used on the list page — single source of truth for the grand total.
- **`format_price` filter** is inherited; the line-total expression `(item.product_price * item.quantity) | format_price` renders VND.
- **`strftime` filter**: a tiny Jinja filter `strftime('%d/%m/%Y %H:%M')` must exist — check whether it is already registered; if not, the planner adds a 3-line custom filter in `app/__init__.py` or the admin blueprint (a 12-month milestone, not a new dependency).
- **Section headings** use `h2` at 16px/600 (matches `.product-description h2` and `.gallery-section h3` pattern) with `.order-section { border-top: 1px solid #E5E7EB; padding-top: 24px; margin-top: 24px; }` for separation.

### 3. Status Flow UI — Progress Stepper + Transition Buttons

**Decision (resolving CONTEXT.md "UI-SPEC sẽ quyết"):** Show a 4-step **progress stepper** on the detail page for all non-terminal statuses, and **one primary button per valid transition** (not a dropdown). Rationale: the transition map has at most one forward step per status, so a dropdown is overkill; the stepper makes the forward-only rule visually explicit (forward-only, cannot go back), which is the core UX of ORD-09.

**Stepper markup (semantic `<ol>`):**
```html
<ol class="order-progress">
  <li class="is-done"><span class="dot"></span>Chờ xác nhận</li>
  <li class="is-done"><span class="dot"></span>Đã gói</li>
  <li class="is-current" aria-current="step"><span class="dot"></span>Đã gửi</li>
  <li><span class="dot"></span>Đã nhận</li>
</ol>
```
- Steps strictly before the current step get `.is-done` (dot `#059669`), the current step gets `.is-current` (dot `#2563EB` with `box-shadow: 0 0 0 3px #DBEAFE` ring, label `#1F2937`/600), future steps stay idle (dot `#D1D5DB`, label `#6B7280`).
- Connector line between dots via `li:not(:first-child)::before` (absolute `border-top: 2px solid`; done segments `#059669`, idle `#D1D5DB`).
- **Đã nhận (terminal, completed):** all 4 `<li>` get `.is-done`; the muted note "Đơn đã hoàn thành." replaces the buttons section (no buttons — nothing to do).
- **Đã hủy (terminal, absorbing):** no stepper at all — render only the muted note "Đơn đã bị hủy." plus the badge. Cancelled is outside the forward chain; showing a 4-step progress with no highlight would misrepresent it.

**Transition buttons:** each valid `next_status` from the transition map renders as its own POST form:
```html
<form method="post" action="{{ url_for('admin.update_order_status', order_id=order.id) }}" class="inline-form">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <input type="hidden" name="next_status" value="Đã gói">
  <button type="submit" class="btn btn-primary">Chuyển sang: Đã gói</button>
</form>
```
- Button label is always the explicit verb+target: **"Chuyển sang: {next_status}"** (not "Cập nhật" / "Tiếp theo").
- Cancel uses `.btn-danger` with a native confirm dialog:
```html
<form method="post" action="{{ url_for('admin.update_order_status', order_id=order.id) }}" class="inline-form"
      onsubmit="return confirm('Hủy đơn #{{ order.id }}? Hành động này không thể hoàn tác.');">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <input type="hidden" name="next_status" value="Đã hủy">
  <button type="submit" class="btn btn-danger">Hủy đơn</button>
</form>
```
- **Server is the source of truth** — the transition map is enforced server-side; the buttons only present valid options. `next_status` not in the map → flash error + redirect, no DB change.

**Explicit transition-map → button mapping (the only four button configurations):**

| Current status | Buttons rendered | Terminal note |
|----------------|------------------|---------------|
| Chờ xác nhận | "Chuyển sang: Đã gói" (primary) + "Hủy đơn" (danger) | — |
| Đã gói | "Chuyển sang: Đã gửi" (primary) + "Hủy đơn" (danger) | — |
| Đã gửi | "Chuyển sang: Đã nhận" (primary) | — |
| Đã nhận | none | "Đơn đã hoàn thành." |
| Đã hủy | none | "Đơn đã bị hủy." |

**New CSS classes:** `.order-progress`, `.order-progress li`, `.order-progress .dot`, `.order-progress li.is-done .dot`, `.order-progress li.is-current`, `.order-progress li::before`, `.order-terminal` (muted `#6B7280`), `.order-meta`, `.order-section`, `.order-filter`, `.order-id`, `.order-detail`.

---

## Interaction Contracts

### Route Map (all admin, `@login_required` via `_protect_admin`)

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/orders` | GET | Order list, `?status=<label>` filter + `?page=N` pagination |
| `/admin/orders/<int:order_id>` | GET | Order detail (customer, items, timestamps, status, transitions) |
| `/admin/orders/<int:order_id>/status` | POST | Advance / cancel order status; validates `next_status` against transition map |

### Filter Flow

1. GET `/admin/orders` — read `status` from query args. If empty → all orders. If not one of the 5 labels → ignore filter (show all), no 500.
2. Query: `Order.query.order_by(Order.created_at.desc(), Order.id.desc())`, optional `.filter_by(status=status)`, `.paginate(page=page, per_page=20, error_out=False)`.
3. Render table + pagination (pagination links preserve the active `status`).
4. Select shows the currently active filter selected; option labels carry per-status counts (optional).

### Status Transition Flow

1. GET `/admin/orders/<id>` — load order; missing → flash `'Không tìm thấy đơn.'` (error) + redirect `/admin/orders`.
2. POST `/admin/orders/<id>/status` with hidden `next_status` + CSRF token (Flask-WTF `CSRFProtect` app-wide — `app/__init__.py:54`).
3. Server: load order (missing → flash error + redirect). Validate `next_status ∈ transition_map[order.status]`:
   - Valid → set `order.status = next_status`, commit, flash success, redirect to detail.
   - Invalid → flash error, redirect to detail, **no DB change, no 500**.
4. Transition map (single source, server-side — duplicated verbatim from 07-CONTEXT.md):
   ```
   'Chờ xác nhận': {'Đã gói', 'Đã hủy'}
   'Đã gói':       {'Đã gửi', 'Đã hủy'}
   'Đã gửi':       {'Đã nhận'}
   'Đã nhận':      set()   # terminal
   'Đã hủy':       set()   # terminal, absorbing
   ```

### Cancel Flow

- "Hủy đơn" is **only rendered** when `status in {'Chờ xác nhận', 'Đã gói'}` (the two cancelable states per CONTEXT.md).
- Client-side: native `confirm()` dialog warns "Hủy đơn #N? Hành động này không thể hoàn tác." — JS-free fallback: if confirm is unavailable, the POST still fires and the server is the source of truth; the dialog is a UX guard only.
- Server-side: cancel is just the `next_status='Đã hủy'` transition — same validation path; no special route.

### Flash Messages (new)

| Type | Message | Trigger |
|------|---------|---------|
| success | "Đã chuyển đơn #{{id}} sang trạng thái “{{next_status}}”." | Valid forward transition |
| success | "Đã hủy đơn #{{id}}." | Valid cancel transition |
| error | "Không tìm thấy đơn." | Order id missing on detail/status route |
| error | "Không thể chuyển trạng thái đơn #{{id}}." | `next_status` not in transition map (incl. attempting to revert or cancel a shipped/delivered order) |

### Accessibility (inherited + Phase 7)

- `lang="vi"`, skip link, flash zone (inherited `base.html`)
- Tables use `<table>` + `<thead>` + `<th scope="col">` + `<caption class="visually-hidden">` (inherited product-list pattern)
- **Status is never conveyed by color alone** — every `.badge-order-*` carries the full VN label text
- Progress stepper is a semantic `<ol>`; the current step has `aria-current="step"`; dots are `<span>` with no text (decorative) — the label text conveys meaning
- All transition/cancel controls are POST forms with CSRF tokens; button labels are explicit full phrases ("Chuyển sang: Đã gói", "Hủy đơn")
- Filter select has a `visually-hidden` label (`.visually-hidden`, inherited)
- Touch targets ≥44px: buttons inherit `.btn` height 44px; `.order-id` link gets inline-block padding to reach 44px; pagination links already ≥44px (Phase 3 rule)
- Badge text color contrast: blue badges `#1D4ED8` on `#DBEAFE` ≈ 4.6:1 (AA); amber/green/gray trios inherited from accepted Phase 2 badges

---

## Responsive Behavior

| Breakpoint | Max-width | Phase 7 Behavior |
|------------|-----------|------------------|
| Mobile | 480px | Order list table scrolls horizontally (`.table-scroll` inherited); filter select full-width, "Lọc" button below; stepper labels tighten (`.order-progress` becomes `overflow-x: auto` so the 4-step row scrolls rather than wraps); transition buttons stack full-width; `#FFFFFF` cards keep `margin-top: 16px` (inherited) |
| Tablet | 768px | Order list table full-width (no scroll needed); detail `.order-detail` card at `max-width: 100%`; `.order-filter` single row (select + button); `.action-row` keeps two buttons side-by-side if they fit, else wraps |
| Desktop | 1200px | `.admin-card` detail at 720px; list `.admin-card--wide` at 1200px; stepper fully visible in one row; `.action-row` two buttons inline |

**CSS approach:** Plain CSS — reuse `.data-table`, `.table-scroll`, `.pagination`, `.badge`, `.btn`, `.btn-primary`, `.btn-danger`, `.action-row`, `.inline-form`, `.empty-state`, `.admin-card`, `.admin-card--wide`, `.admin-header`, `.cart-total`, `.cart-total-label`, `.cart-total-value`, `.price-cell`, `.back-link`. New classes: `.badge-order-*` (×5), `.order-progress` (+ state variants), `.order-filter`, `.order-id`, `.order-meta`, `.order-section`, `.order-terminal`, `.order-detail`. Keep total CSS under inherited ~20KB target (the additions are ~80 lines).

**Templates touched / created:**
- `app/templates/admin/dashboard.html` — add "Đơn hàng" nav-group (with optional count)
- `app/templates/admin/orders/list.html` — NEW — filter + paginated table + empty states
- `app/templates/admin/orders/detail.html` — NEW — stepper + customer + items + timestamps + transition buttons
- `app/static/css/style.css` — add badge variants + stepper + order page classes

---

## Copywriting Contract

All copy in Vietnamese (`lang="vi"`, PLAT-01). All new copy for Phase 7:

| Element | Copy |
|---------|------|
| Nav link (dashboard) | "Đơn hàng" |
| Nav badge (0 orders) | "Chưa có đơn" |
| List page heading | "Đơn hàng" |
| Filter label (visually-hidden) | "Lọc theo trạng thái" |
| Filter default option | "Tất cả" |
| Filter submit | "Lọc" |
| List table headings | "ID" · "Khách hàng" · "Tổng tiền" · "Trạng thái" · "Ngày tạo" |
| List caption (visually-hidden) | "Danh sách đơn hàng" |
| Empty state (no orders) heading | "Chưa có đơn nào" |
| Empty state (no orders) body | "Khách đặt hàng qua web sẽ hiện ở đây." |
| Empty state (filtered) heading | "Không có đơn nào ở trạng thái “{status}”" |
| Empty state (filtered) body | "Thử chọn trạng thái khác hoặc chọn “Tất cả”." |
| Back link | "Quay lại" |
| Detail heading | "Đơn #{{order.id}}" |
| Section heading — customer | "Thông tin khách" |
| Section heading — items | "Sản phẩm" |
| Section heading — time | "Thời gian" |
| Section heading — actions | "Cập nhật trạng thái" |
| Customer-meta labels | "Họ và tên" · "Số điện thoại" · "Địa chỉ" · "Ghi chú" |
| Items table headings | "Sản phẩm" · "Số lượng" · "Đơn giá" · "Thành tiền" |
| Items caption (visually-hidden) | "Sản phẩm trong đơn" |
| Total label | "Tổng cộng" |
| Timestamp labels | "Ngày tạo" · "Cập nhật" |
| Advance button | "Chuyển sang: {next_status}" (e.g. "Chuyển sang: Đã gói") |
| Cancel button | "Hủy đơn" |
| Cancel confirm dialog | "Hủy đơn #{{id}}? Hành động này không thể hoàn tác." |
| Terminal note (Đã nhận) | "Đơn đã hoàn thành." |
| Terminal note (Đã hủy) | "Đơn đã bị hủy." |
| Success flash — advance | "Đã chuyển đơn #{{id}} sang trạng thái “{{next_status}}”." |
| Success flash — cancel | "Đã hủy đơn #{{id}}." |
| Error flash — missing order | "Không tìm thấy đơn." |
| Error flash — invalid transition | "Không thể chuyển trạng thái đơn #{{id}}." |

**Destructive confirmation:** Cancel ("Hủy đơn") is the only destructive-ish action (terminal, absorbing). It uses the native `confirm()` dialog. No separate confirmation page — a status change is not a data deletion (product delete keeps its dedicated page).

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not applicable — shadcn not used (Flask project, not React/Next/Vite) |
| Third-party | none | not applicable — no component registries declared |

**Note:** The shadcn initialization gate does not apply. Tech stack is Python Flask with Jinja2 templates and hand-written CSS (CLAUDE.md "What NOT to Use" bans Tailwind, Bootstrap, React/Vue, shadcn). No new dependencies are added in this phase — CSRF via Flask-WTF (already initialized app-wide in `app/__init__.py:54`), status validation via the server-side transition map, price via inherited `format_price` filter. The cancel `confirm()` is a native browser dialog, not a third-party library. Two new hex values (`#DBEAFE`, `#BFDBFE`) are literal CSS colors in `style.css`, not package additions.

---

## Open Questions / Decisions Made on Pattern

All CONTEXT.md open items are resolved by pattern — **no blocking questions remain**:

1. **Progress indicator?** → **Yes.** A 4-step `.order-progress` stepper (Chờ xác nhận → Đã gói → Đã gửi → Đã nhận) with the current step highlighted; renders for all non-terminal statuses; Đã nhận renders all-done + "Đơn đã hoàn thành."; Đã hủy renders no stepper, only "Đơn đã bị hủy."
2. **Transition control — button vs dropdown?** → **One primary button per valid next status** (the map has ≤1 forward step per status, so a dropdown adds no value). Cancel is a separate `.btn-danger` button.
3. **Cancel confirmation approach?** → Native `confirm()` dialog on the inline POST form (one line of JS, no new template; server is still the source of truth). Product delete keeps its dedicated confirmation page (data deletion vs status change).
4. **Admin nav placement?** → Dashboard `nav-list` only, mirroring the "Sản phẩm" group. There is no shared admin nav template; a shared admin nav is deferred to Phase 9 polish (would touch every admin template — out of scope here).
5. **Timestamp format** → List uses `%d/%m/%Y` (compact); detail uses `%d/%m/%Y %H:%M` for both created_at and updated_at. Requires a small `strftime` Jinja filter if not already registered.

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS — Vietnamese throughout; explicit CTA labels ("Chuyển sang: Đã gói", "Hủy đơn"); two distinct empty states with actionable copy; all 5 status labels are user-facing VN text; cancel carries a confirm dialog; success/error flash copy defined for every transition outcome.
- [ ] Dimension 2 Visuals: PASS — order list reuses `.data-table` + `.pagination` + `.empty-state` exactly like the product list; detail reuses `.admin-card` + `.action-row` + `.cart-total`; stepper is pure CSS, no new glyphs; badges reuse the Phase 2 `.badge` shape.
- [ ] Dimension 3 Color: PASS — one new accent reservation list; two new badge hex values (`#DBEAFE`/`#BFDBFE`) scoped to blue status badges only; amber/green/gray badge trios inherited unchanged; destructive `#DC2626` scoped to cancel button + error flash; success `#059669`/`#047857` scoped to success flash + stepper done dots.
- [ ] Dimension 4 Typography: PASS — maps onto 4 inherited roles (14/16/24/32); 2 weights (400/600); body 1.5, heading 1.2, display 1.1; no new sizes or weights.
- [ ] Dimension 5 Spacing: PASS — all values multiples of 4 from the inherited scale; 12px stepper-dot diameter + 2px connector border declared as justified exceptions.
- [ ] Dimension 6 Registry Safety: PASS — no third-party registries, no shadcn, no new dependencies; all components hand-rolled; native `confirm()` and `strftime` filter only.

**Approval:** pending
