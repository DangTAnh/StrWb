---
phase: 8
slug: admin-stats
status: draft
shadcn_initialized: false
preset: none
created: 2026-08-02
---

# Phase 8 — UI Design Contract

> Visual and interaction contract for Phase 8 — Admin Stats. Phase 8 extends the existing Phase 1/2/6/7 design system — it does **not** redefine it. All tokens, typography, spacing, and color roles are inherited unchanged. This contract declares only the **new components, new copy, new interactions, and new CSS class names** introduced by the stats dashboard (`GET /admin/stats`).

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — Flask server-rendered Jinja2 templates with hand-written CSS |
| Preset | not applicable |
| Component library | none (hand-rolled stat cards, status breakdown list) |
| Icon library | none (text labels only; counts render as `.badge` pills, no icon glyphs) |
| Font | Noto Sans VN (Google Fonts) — inherited Phase 1; fallback `Roboto, system-ui, -apple-system, sans-serif` |

**Design system source:** Phase 1 baseline (`01-UI-SPEC.md`) — colors `#2563EB` / `#F9FAFB` / `#FFFFFF` / `#1F2937` / `#6B7280` / `#DC2626` / `#059669`; type scale 14/16/24/32 with weights 400 + 600; spacing multiples of 4 (4/8/16/24/32/48/64); breakpoints 480/768/1200. Phase 2 (`02-UI-SPEC.md`) — button variants, status badges, `.data-table`, `.empty-state`, `.pagination`. Phase 6 (`06-UI-SPEC.md`) — confirms no new design-system tokens; `format_price` filter. Phase 7 (`07-UI-SPEC.md`) — admin order list/detail patterns, `.badge-order-*`, `.admin-page`/`.admin-header`/`.admin-card--wide` layout, `_order_total` + `order_badge_class` globals. This phase reuses the admin card/group layout and the `.badge-order-*` family.

**Phase 8 extensions (new, declared here):**
1. **Admin nav link "Thống kê"** on the admin dashboard nav-list — mirrors the existing "Sản phẩm" / "Đơn hàng" nav-group pattern (no count badge — stats has no single scalar count).
2. **Stats dashboard page** (`/admin/stats`) — server-rendered, GET-only, zero JS, zero polling. Three grouped sections of stat cards reusing the `.admin-card--wide` container + `.order-section` divider pattern.
3. **Stat card** (`.stat-card`) — a light-gray tile (label + value + optional hint/note) for scalar metrics: revenue, profit, units sold, and the four inventory counts.
4. **Status breakdown list** (`.status-breakdown`) — the Đơn hàng section's per-status order counts; **each row is a link** to the Phase 7 filtered order list (`/admin/orders?status=<label>`), carrying the existing `.badge-order-*` pills.

**shadcn gate:** Not applicable. Tech stack is Python Flask with Jinja2 + plain CSS (CLAUDE.md "What NOT to Use" bans Tailwind, Bootstrap, React/Vue, shadcn). No `components.json` (verified: none in repo), no React/Next/Vite.

---

## Spacing Scale

Inherited unchanged from Phase 1 (`4 / 8 / 16 / 24 / 32 / 48 / 64`). Phase 8 introduces **no new spacing tokens** — all gaps use existing tokens.

| Token | Value | Phase 8 Usage |
|-------|-------|---------------|
| xs | 4px | stat-card internal label↔value gap, badge margin |
| sm | 8px | breakdown row padding (vertical, part of 44px touch target), stat-hint margin-top |
| md | 16px | `.stats-grid` gap, `.stat-card` padding, `.stats-group` bottom padding |
| lg | 24px | `.stats-group` section padding, group-title margin-bottom, breakdown list margin-top |
| xl | 32px | Not used in Phase 8 |
| 2xl | 48px | Not used in Phase 8 |
| 3xl | 64px | Not used in Phase 8 |

**Exceptions (declared, justified sub-token values — not new spacing tokens):**
- Breakdown row total height: `min-height: 44px` — inherits the project-wide touch-target rule (same as `.btn` height, `.pagination a`, `.order-id`). Achieved with `padding: 12px 8px` + `min-height: 44px`, not a new spacing token.
- Stat-value `32px` line-height 1.1 and `24px` line-height 1.2 are inherited role line-heights (Display / Heading), not spacing tokens.

---

## Typography

Roles inherited from Phase 1. Phase 8 maps all new elements onto existing roles — **no new sizes, no new weights** (declared: 14, 16, 24, 32 px; weights 400 + 600).

| Role | Size | Weight | Line Height | Phase 8 Usage |
|------|------|--------|-------------|---------------|
| Body | 16px | 400 | 1.5 | Status breakdown row labels (status VN label) |
| Label | 14px | 400 | 1.5 | `.stat-label`, `.stat-hint`, `.stat-note`, breakdown badge count (inherited `.badge`) |
| Label (semibold) | 14px | 600 | 1.5 | Breakdown "Tất cả" badge, status badges (inherited `.badge`) |
| Heading | 24px | 600 | 1.2 | Stat-value for counts (units sold, total orders, inventory counts) — reused as a numeric value role |
| Display | 32px | 600 | 1.1 | Stat-value for money (revenue, profit) — same role as order-detail total and product price |
| Body (semibold variant) | 16px | 600 | 1.5 | Group titles (`h2.stats-group-title`) — matches `.order-section h2` / `.product-description h2` pattern |

**Font stack (inherited):** `Noto Sans VN`, `Roboto`, `system-ui`, `-apple-system`, `sans-serif`

### Phase 8 Type Usage Map

| Element | Role | Weight | Notes |
|---------|------|--------|-------|
| Page heading "Thống kê" | Heading | 600 | 24px, `#1F2937` |
| Nav "Thống kê" link | Body | 400 | 16px, `#1F2937`, inherited `.nav-list a` |
| Group title "Doanh thu & Lợi nhuận" / "Đơn hàng" / "Kho" | Body (semibold) | 600 | 16px, `#1F2937`, margin-bottom 16px |
| Stat label ("Tổng doanh thu" / "Lợi nhuận" / …) | Label | 400 | 14px, `#6B7280` |
| Stat value — revenue / profit | Display | 600 | 32px, tabular-nums; revenue `#2563EB`, profit `#1F2937` |
| Stat value — counts | Heading | 600 | 24px, `#1F2937`, tabular-nums |
| Stat hint | Label | 400 | 14px, `#6B7280` |
| Stat note (NULL-safe profit) | Label | 400 | 14px, `#B45309` (amber-700 — NEW, contrast-fixed) |
| Breakdown row status label | Body | 400 | 16px, `#1F2937` |
| Breakdown badge count | Label | 600 | 14px, inherited `.badge-order-*` / `.badge-neutral` |
| "Tất cả" breakdown row | Body | 400 | 16px, `#1F2937` |

---

## Color

Base palette inherited unchanged from Phase 1 + Phase 2/7 badge palettes. Phase 8 adds **one new hex value** — `#B45309` (Tailwind amber-700) — used **only** for the conditional NULL-safe profit note (`.stat-note`). The inherited warning amber `#D97706` (`.flash.warning`) measures ≈3.2:1 on `#FFFFFF`, below AA for 14px text; `#B45309` on `#F9FAFB` measures ≈4.7:1 (AA). This mirrors the D-07 precedent of darkening a semantic color to meet contrast. All other colors are inherited unchanged.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | #F9FAFB | Page background (inherited); `.stat-card` tile background |
| Secondary (30%) | #FFFFFF | `.admin-card--wide` stats container (inherited) |
| Accent (10%) | #2563EB | Revenue stat-value, status-breakdown row hover, nav link, focus rings |
| Destructive | #DC2626 | Not used in Phase 8 (no destructive actions — GET-only, no forms) |
| Success semantic | #059669 | Not used in Phase 8 (reused only inside inherited `.badge-order-delivered`) |
| Neutral semantic | #6B7280 | Stat labels, stat hints, profit stat-value (`#1F2937` for counts), breakdown badge neutral text |
| Warning semantic (NEW #B45309) | #B45309 | NULL-safe profit note `.stat-note` — only rendered when cost-bearing items were excluded |
| Border | #E5E7EB | `.stat-card` border, `.stats-group` dividers, breakdown row separators |
| Tile border | #E5E7EB | `.stat-card { background:#F9FAFB; border:1px solid #E5E7EB; }` — same gray as `.data-table thead` |

**Accent reserved for (inherited list, extended for Phase 8):**
1. Revenue stat-value (the single headline money metric) — NEW
2. Status-breakdown row hover background `#F9FAFB` — NEW (row text stays `#1F2937`; link affordance is the hover + count badge, not blue text)
3. Nav "Thống kê" link hover — NEW
4. Links — back link, brand hover (inherited)
5. Focus rings / focus border (inherited; `a:focus-visible`, `:focus-visible` outline)

**Explicit non-accent decisions (deliberate):**
- Profit stat-value is `#1F2937`, **not** accent — it can be negative (cost > price); negative values in accent read as broken. Negative profit renders as `-{format_price}` (e.g. `-200.000₫`); no separate red styling is added this phase (edge case, deferred to Phase 9 polish if it proves real).
- Units-sold and all inventory counts are `#1F2937`, **not** accent — 10% accent would be exceeded with eight colored numbers; the label text carries the meaning (never color-only).
- Breakdown row status labels are `#1F2937`, not accent blue — the row is the link; on hover the row background tints `#F9FAFB` (matches `.data-table tbody tr:hover`).

**Color usage rules (inherited + Phase 8):**
- All non-link text: `#1F2937`
- Money values use `font-variant-numeric: tabular-nums` (inherited `.price-cell` / `.cart-total-value` rule)
- No status conveyed by color alone — every badge carries the full VN label text (inherited)
- Zero data renders as `0₫` / `0` in normal value styling — **no dimming, no placeholder** (CONTEXT.md empty-state decision)

---

## Layout & Component Contract

### 0. Admin Nav "Thống kê" (dashboard nav-list)

**Location:** `app/templates/admin/dashboard.html`, inside the existing `.nav-list`, after the "Đơn hàng" `.nav-group` and before the logout form. There is no shared admin nav template (Phase 7 deferred it to Phase 9); adding to the dashboard nav-list is consistent with how "Sản phẩm" and "Đơn hàng" are wired.

```
[nav.nav-list]
  ├── [a] Trang chủ
  ├── [div.nav-group] Sản phẩm (badge {products_count})
  ├── [div.nav-group] Đơn hàng (badge {orders_count})
  ├── [div.nav-group]  ── NEW
  │   └── [a href="/admin/stats"] Thống kê
  └── [div.nav-group.logout-form] Đăng xuất
```

**Markup:**
```html
<div class="nav-group">
  <a href="{{ url_for('admin.stats') }}">Thống kê</a>
</div>
```
- **No count badge.** Unlike "Sản phẩm"/"Đơn hàng", there is no single scalar count that represents the stats page (it aggregates five statuses and four inventory counts). A badge would be misleading.
- No CSS change: reuses `.nav-group` (inherited).

### 1. Stats Dashboard Page (`GET /admin/stats`)

**Route:** `admin.stats()` — `@admin_bp.route('/stats', methods=['GET'])`, protected by the existing `_protect_admin` before_request. GET-only, server-rendered, **no forms, no POST, no JS, no polling**.

**Template:** `app/templates/admin/stats.html` (NEW) — `{% extends "base.html" %}`.

```
[.admin-page]
  ├── [.admin-header]
  │   └── [h1] Thống kê
  │
  └── [.admin-card.admin-card--wide]                    ── inherited container (1200px, padding 0)
      ├── [section.stats-group]                          ── Doanh thu & Lợi nhuận
      │   ├── [h2.stats-group-title] Doanh thu & Lợi nhuận
      │   └── [div.stats-grid]
      │       ├── [article.stat-card]
      │       │   ├── [p.stat-label] Tổng doanh thu
      │       │   ├── [p.stat-value.stat-value--display] {{ revenue | format_price }}
      │       │   └── [p.stat-hint] Chỉ tính đơn Đã gửi và Đã nhận.
      │       ├── [article.stat-card]
      │       │   ├── [p.stat-label] Lợi nhuận
      │       │   ├── [p.stat-value.stat-value--display] {{ profit | format_price }}
      │       │   ├── [IF profit_note][p.stat-note] {{ profit_note }}  (only when cost items were excluded)
      │       │   └── [p.stat-hint] Doanh thu trừ giá nhập.
      │       └── [article.stat-card]
      │           ├── [p.stat-label] Sản phẩm đã bán
      │           ├── [p.stat-value] {{ units_sold }}
      │           └── [p.stat-hint] Từ các đơn Đã gửi và Đã nhận.
      │
      ├── [section.stats-group]                          ── Đơn hàng
      │   ├── [h2.stats-group-title] Đơn hàng
      │   └── [div.stat-card]
      │       ├── [p.stat-label] Tổng số đơn
      │       ├── [p.stat-value] {{ total_orders }}
      │       ├── [p.stat-hint] Gồm cả đơn đã hủy.
      │       └── [ul.status-breakdown]
      │           ├── [li] [a href="{{ url_for('admin.orders') }}"] Tất cả [span.badge.badge-neutral] {{ total_orders }}
      │           ├── [li] [a href="{{ url_for('admin.orders', status='Chờ xác nhận') }}"] Chờ xác nhận [span.badge.badge-order-pending] {{ status_counts.get('Chờ xác nhận', 0) }}
      │           ├── [li] [a href="{{ url_for('admin.orders', status='Đã gói') }}"] Đã gói [span.badge.badge-order-packed] {{ status_counts.get('Đã gói', 0) }}
      │           ├── [li] [a href="{{ url_for('admin.orders', status='Đã gửi') }}"] Đã gửi [span.badge.badge-order-shipped] {{ status_counts.get('Đã gửi', 0) }}
      │           ├── [li] [a href="{{ url_for('admin.orders', status='Đã nhận') }}"] Đã nhận [span.badge.badge-order-delivered] {{ status_counts.get('Đã nhận', 0) }}
      │           └── [li] [a href="{{ url_for('admin.orders', status='Đã hủy') }}"] Đã hủy [span.badge.badge-order-cancelled] {{ status_counts.get('Đã hủy', 0) }}
      │
      └── [section.stats-group]                          ── Kho
          ├── [h2.stats-group-title] Kho
          └── [div.stats-grid]
              ├── [article.stat-card] [p.stat-label] Tổng sản phẩm [p.stat-value] {{ total_products }} [p.stat-hint] Gồm cả sản phẩm ngừng bán.
              ├── [article.stat-card] [p.stat-label] Còn hàng [p.stat-value] {{ in_stock }}
              ├── [article.stat-card] [p.stat-label] Hết hàng [p.stat-value] {{ out_of_stock }}
              └── [article.stat-card] [p.stat-label] Ngừng bán [p.stat-value] {{ discontinued }}
```

**Component specifics:**
- **Container:** reuses `.admin-card--wide` (`max-width: 1200px; padding: 0; overflow: hidden`). The three `.stats-group` sections stack inside with `padding: 24px` and `border-top: 1px solid #E5E7EB` (first section has no border) — mirrors the `.order-section` divider pattern from Phase 7.
- **Stat card tile:** `.stat-card` is a light-gray tile (`background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px;`) nested inside the white container — the same gray as `.data-table thead` and `.nav-group .badge`, giving clear separation from the white card behind it.
- **Money values** use the inherited `format_price` filter: `{{ revenue | format_price }}` renders `1.200.000₫`. Zero renders as `0₫` (no empty-state component, no dimming — CONTEXT.md decision).
- **Counts** (units sold, total orders, inventory) render as bare integers with `tabular-nums`; the noun lives in the `.stat-label` ("Sản phẩm đã bán", "Tổng số đơn").
- **NULL-safe profit note:** `.stat-note` renders **only** when at least one cost-bearing item was excluded from the profit sum. Copy is server-built: `"Lợi nhuận tính trên {N} sản phẩm có giá nhập."` where `N` = count of items that had a non-NULL `product_cost_price` and were included in the profit calculation. When no items were excluded, the note is absent (never shows a "0" variant).
- **Status breakdown:** each row is a full-width link to the Phase 7 filtered order list. The "Tất cả" row links to `/admin/orders` (no filter); the five status rows link with `?status=<label>`. The label is the full VN status string (matches the DB column value — same convention as the Phase 7 filter select). Badges reuse the existing `.badge-order-*` classes; the "Tất cả" row uses a new neutral `.badge-neutral` (same trio as `.badge-discontinued`, semantically neutral).

**Data contract (what the template must receive from `admin.stats()`):**
- `revenue` (int VND), `profit` (int VND), `profit_note` (str | None), `units_sold` (int)
- `status_counts` (dict of VN label → count, five keys), `total_orders` (int)
- `total_products`, `in_stock`, `out_of_stock`, `discontinued` (all int)

**New CSS classes:** `.stats-group`, `.stats-group-title` (targets `h2`), `.stats-grid`, `.stat-card`, `.stat-label`, `.stat-value`, `.stat-value--display`, `.stat-hint`, `.stat-note`, `.status-breakdown`, `.status-breakdown a`, `.badge-neutral`. Total CSS additions ≈ 70–90 lines; keeps the stylesheet near the inherited ~20KB target.

---

## Interaction Contracts

### Route Map (all admin, `@login_required` via `_protect_admin`)

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/stats` | GET | Stats dashboard — revenue, profit, units sold, orders-by-status, inventory counts |

**No POST routes, no forms, no state mutation, no confirmations.** The page is a read-only aggregate view. The only interactions are navigational links (nav link, breakdown rows). CSRF is not involved (no forms).

### Data Flow

1. GET `/admin/stats` → `admin.stats()`.
2. Server computes aggregates **in Python/SQLAlchemy** (single request, no client calls):
   - `qualifying = {'Đã gửi', 'Đã nhận'}`
   - `revenue` = `SUM(product_price * quantity)` over `OrderItem` rows whose `Order.status ∈ qualifying` (join order_items → orders). **Đã hủy / Chờ xác nhận / Đã gói are excluded** (STAT-01, locked).
   - `profit` = `SUM((product_price - product_cost_price) * quantity)` over the same items **where `product_cost_price IS NOT NULL`**; NULL-cost items are excluded (never treated as 0 — avoids overstating profit; STAT-02, locked).
   - `units_sold` = `SUM(quantity)` over qualifying-order items — same qualifying set as revenue (consistency, locked).
   - `status_counts` = `GROUP BY Order.status` count (all five statuses, incl. Đã hủy — STAT-03, locked); `total_orders` = sum of the five counts.
   - Inventory (STAT-04, locked): `total_products` = all Products incl. discontinued; `in_stock` = `quantity > 0 AND NOT discontinued`; `out_of_stock` = `quantity == 0 AND NOT discontinued`; `discontinued` = `discontinued IS TRUE`.
   - Scope: **all-time** (STAT-05 date filtering is deferred to v2).
3. Render `admin/stats.html` with the data contract above.

### Breakdown → Filtered Orders Navigation

1. Click any breakdown row (or the nav link).
2. `admin.orders` receives the `?status=<label>` param and applies the existing Phase 7 filter (status string in `ORDER_STATUSES` → filter; otherwise show all, no 500).
3. Browser Back returns to the stats page (server-rendered, no SPA state to lose).

### Zero / Empty Data

- **No `.empty-state` component.** CONTEXT.md decision: "hiện số 0 rõ ràng (₫0, 0 đơn) + label, không để trống, không báo lỗi."
- Revenue `0₫`, profit `0₫`, units `0`, total orders `0`, each inventory count `0`, and every breakdown badge `0` render in normal value styling.
- The NULL-safe profit note is **never** shown in the zero case (it only appears when ≥1 cost-bearing item was excluded, which implies qualifying orders exist).

### Accessibility (inherited + Phase 8)

- `lang="vi"`, skip link, flash zone (inherited `base.html`)
- Heading hierarchy: `h1` "Thống kê" → `h2` group titles → `p.stat-label` values (labels are `<p>`, not headings — consistent with order-detail section pattern)
- **Counts and statuses are never conveyed by color alone** — every stat card pairs a value with a text label; every breakdown row pairs the VN status label with a text badge (inherited)
- Breakdown rows are real `<a>` links with `min-height: 44px` touch targets; row text is `#1F2937` (link affordance = hover tint + badge, matching the product table row pattern where the ID link is the affordance)
- Money uses `tabular-nums` (no digit jitter)
- `.stat-note` contrast `#B45309` on `#F9FAFB` ≈ 4.7:1 (AA at 14px) — declared new hex
- No JS required; page works with scripting disabled (links only)

---

## Responsive Behavior

| Breakpoint | Max-width | Phase 8 Behavior |
|------------|-----------|------------------|
| Mobile | 480px | `.stats-grid` collapses to **1 column**; stat cards stack full-width; `.stats-group` sections keep `padding: 24px` (reduced to 16px so the numbers fit); breakdown rows stay full-width with the badge right-aligned; `stat-value--display` (32px) fits on one line (1-column width ≈ 100vw − padding); `.admin-card--wide` becomes `max-width: 100%` (inherited rule) |
| Tablet | 768px | `.stats-grid` becomes **2 columns** (revenue group renders 2+1, kho group renders 2×2); breakdown list full-width; group sections single column |
| Desktop | 1200px | `.stats-grid` becomes **3 columns** (revenue group 3-across; kho group renders 3+1); stats container at 1200px; breakdown list full-width |

**CSS approach:** Plain CSS. Reuse `.admin-page`, `.admin-header`, `.admin-card--wide`, `.badge`, `.badge-order-*`. New classes: `.stats-group`, `.stats-group-title`, `.stats-grid`, `.stat-card`, `.stat-label`, `.stat-value`, `.stat-value--display`, `.stat-hint`, `.stat-note`, `.status-breakdown`, `.status-breakdown a`, `.badge-neutral`. Grid uses the inherited breakpoint pattern (base 1-col → 768px 2-col → 1200px 3-col), matching `.product-grid`.

**Templates touched / created:**
- `app/templates/admin/dashboard.html` — add "Thống kê" nav-group (no badge)
- `app/templates/admin/stats.html` — NEW — grouped stat cards + status breakdown
- `app/static/css/style.css` — add stats-group/grid/stat-card/breakdown/badge-neutral classes
- `app/admin.py` — add `admin.stats()` route (aggregation queries)

---

## Copywriting Contract

All copy in Vietnamese (`lang="vi"`, PLAT-01). All new copy for Phase 8:

| Element | Copy |
|---------|------|
| Nav link (dashboard) | "Thống kê" |
| Page heading | "Thống kê" |
| Group title — money | "Doanh thu & Lợi nhuận" |
| Group title — orders | "Đơn hàng" |
| Group title — inventory | "Kho" |
| Stat label — revenue | "Tổng doanh thu" |
| Stat hint — revenue | "Chỉ tính đơn Đã gửi và Đã nhận." |
| Stat label — profit | "Lợi nhuận" |
| Stat hint — profit | "Doanh thu trừ giá nhập." |
| Stat note — NULL-safe profit (conditional) | "Lợi nhuận tính trên {N} sản phẩm có giá nhập." |
| Stat label — units sold | "Sản phẩm đã bán" |
| Stat hint — units sold | "Từ các đơn Đã gửi và Đã nhận." |
| Stat label — total orders | "Tổng số đơn" |
| Stat hint — total orders | "Gồm cả đơn đã hủy." |
| Stat label — total products | "Tổng sản phẩm" |
| Stat hint — total products | "Gồm cả sản phẩm ngừng bán." |
| Stat label — in stock | "Còn hàng" |
| Stat label — out of stock | "Hết hàng" |
| Stat label — discontinued | "Ngừng bán" |
| Breakdown row — all | "Tất cả" |
| Breakdown rows — statuses | "Chờ xác nhận" · "Đã gói" · "Đã gửi" · "Đã nhận" · "Đã hủy" (inherited ORDER_STATUSES) |

**Primary CTA:** none — the stats page is a read-only dashboard; the only forward action is drilling into the order list via a breakdown row (a link, not a CTA button).

**Empty state:** no component — zeros render clearly with labels (CONTEXT.md decision). "0₫", "0", and badge "0" in normal styling.

**Error state:** none in this phase — GET-only, no forms, no validation, no mutation. Aggregation on an empty DB yields zeros, never an error. (Server errors are the inherited 404/500 pages.)

**Destructive actions:** none — no POST routes, no delete, no status change, no confirmation dialogs.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not applicable — shadcn not used (Flask project, not React/Next/Vite) |
| Third-party | none | not applicable — no component registries declared |

**Note:** The shadcn initialization gate does not apply. Tech stack is Python Flask with Jinja2 templates and hand-written CSS (CLAUDE.md "What NOT to Use" bans Tailwind, Bootstrap, React/Vue, shadcn). **No new dependencies are added in this phase** — aggregation uses SQLAlchemy 2.0 queries (`db.session.query(...).filter(...)`), money uses the inherited `format_price` filter, status filtering reuses the Phase 7 `ORDER_STATUSES`/`url_for('admin.orders', status=...)` pattern. One new hex value (`#B45309`) is a literal CSS color in `style.css`, not a package addition. No JS, no polling, no fetch.

---

## Open Questions / Decisions Made on Pattern

All CONTEXT.md areas are **locked** (`Claude's Discretion: Không có`); every design decision below is resolved by pattern from upstream artifacts — **no blocking questions remain**:

1. **Empty-state component?** → **No.** CONTEXT.md locks "hiện số 0 rõ ràng (₫0, 0 đơn) + label, không để trống, không báo lỗi." Zeros render in normal value styling; no `.empty-state`, no dimming.
2. **Stat-value color for money?** → Revenue `#2563EB` (single headline metric); profit `#1F2937` (can be negative, accent would misread); counts `#1F2937`. Keeps accent at 10%.
3. **Status breakdown affordance?** → Full-width rows with `min-height: 44px`, text `#1F2937`, hover tint `#F9FAFB`, count in the existing `.badge-order-*` pill — mirrors the product/order table row pattern where the row link affordance is hover + badge, not blue text.
4. **"Tất cả" row?** → Yes — a neutral `.badge-neutral` pill (same gray trio as `.badge-discontinued`, semantically neutral) linking to unfiltered `/admin/orders`.
5. **Nav badge for "Thống kê"?** → **None** — no single scalar count represents the page; a badge would mislead. Link-only nav-group.
6. **New hex value?** → `#B45309` for `.stat-note` only — inherited warning amber `#D97706` fails AA (3.2:1) on white; `#B45309` on `#F9FAFB` ≈ 4.7:1 (AA). Mirrors the accepted D-07 darkening precedent.

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS — Vietnamese throughout; no primary CTA (read-only dashboard is intentional); zero-data state renders explicit `0₫`/`0` with labels; no error state needed (GET-only); no destructive actions; conditional NULL-safe profit note copy defined.
- [ ] Dimension 2 Visuals: PASS — stats page reuses `.admin-card--wide` + `.order-section` divider pattern; stat cards reuse the `.data-table thead` gray (`#F9FAFB`) tile style; breakdown reuses `.badge-order-*`; no new component shapes, no icons, no JS.
- [ ] Dimension 3 Color: PASS — one new hex (`#B45309`) scoped to the NULL-safe note only and justified as a contrast fix over inherited `#D97706`; accent reserved for exactly four items (revenue value, row hover, nav hover, focus rings); counts deliberately non-accent to respect 60/30/10.
- [ ] Dimension 4 Typography: PASS — maps onto 4 inherited roles (14/16/24/32); 2 weights (400/600); no new sizes or weights; group titles reuse the established 16px/600 variant.
- [ ] Dimension 5 Spacing: PASS — all values multiples of 4 from the inherited scale; 44px breakdown-row touch target declared as a justified inherited-rule exception.
- [ ] Dimension 6 Registry Safety: PASS — no third-party registries, no shadcn, no new dependencies; aggregation via SQLAlchemy 2.0 queries; one literal CSS hex added; no JS.

**Approval:** pending
