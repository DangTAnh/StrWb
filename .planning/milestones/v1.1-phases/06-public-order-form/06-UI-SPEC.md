---
phase: 6
slug: public-order-form
status: draft
shadcn_initialized: false
preset: none
created: 2026-08-02
reviewed_at: 2026-08-02
---

# Phase 6 — UI Design Contract

> Visual and interaction contract for Phase 6 — Cart + Checkout (Public Order Form). Phase 6 extends the existing Phase 1/2/3 design system — it does **not** redefine it. All tokens, typography, spacing, and color roles are inherited unchanged. This contract declares only the **new components, new copy, new interactions, and new CSS class names** introduced by the cart/checkout flow.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — Flask server-rendered Jinja2 templates with hand-written CSS |
| Preset | not applicable |
| Component library | none (hand-rolled form fields, cart table, cart-link badge) |
| Icon library | none (text labels and aria-labels only) |
| Font | Noto Sans VN (Google Fonts) — inherited Phase 1; fallback `Roboto, system-ui, -apple-system, sans-serif` |

**Design system source:** Phase 1 baseline (`01-UI-SPEC.md`) — colors `#2563EB` / `#F9FAFB` / `#FFFFFF` / `#1F2937` / `#6B7280` / `#DC2626` / `#059669`; type scale 14/16/24/32 with weights 400 + 600; spacing multiples of 4 (4/8/16/24/32/48/64); breakpoints 480/768/1200. Phase 2 (`02-UI-SPEC.md`) — button variants, badge styles, `.form-field` / `.form-row-2` patterns. Phase 3 (`03-UI-SPEC.md`) — public header/nav (`public/_nav.html`), product card, product detail layout, `.contact-strip`, flash zone in `base.html`. Phase 5 (`05-UI-SPEC.md`) — confirms no new design-system tokens; single-field extension only.

**Phase 6 extensions (new, declared here):**
1. **Add-to-cart block** on product detail — replaces the single Messenger CTA on the detail page only; uses existing `.btn` / `.form-field` classes.
2. **Cart-link badge** in the public nav — a small indicator showing item count; reuses `--accent` for the badge background.
3. **Cart page** — a table-based line-item list (reuses `.data-table` patterns + `format_price`); empty-state reuses `.empty-state`.
4. **Checkout form** — a new form card (reuses `.form-field`, `.form-row-2`, `.btn`); CSRF + honeypot field.

**shadcn gate:** Not applicable. Tech stack is Python Flask with Jinja2 + plain CSS (CLAUDE.md "What NOT to Use" bans Tailwind, Bootstrap, React/Vue, shadcn). No `components.json`, no React/Next/Vite.

---

## Spacing Scale

Inherited unchanged from Phase 1 (`4 / 8 / 16 / 24 / 32 / 48 / 64`). Phase 6 introduces **no new spacing tokens** — all gaps use existing tokens.

| Token | Value | Phase 6 Usage |
|-------|-------|---------------|
| xs | 4px | Cart-link badge text margin-left, field-error margin-top |
| sm | 8px | Cart table cell vertical padding, qty-input width gap |
| md | 16px | Add-to-cart block vertical rhythm, cart table cell horizontal padding, checkout field margin-bottom, cart-link badge vertical position |
| lg | 24px | Cart page section gap, empty-state padding |
| xl | 32px | Cart ↔ checkout vertical gap (single-page layout) |
| 2xl | 48px | Major section break above contact strip (homepage, inherited) |
| 3xl | 64px | Contact strip top margin (homepage, inherited) |

**Exceptions:**
- Cart-link badge: `0.5rem` (8px) right padding + `0.25rem` (4px) horizontal — a compact pill badge that sits inline with the nav brand; this is a justified sub-token exception (badge text must not push nav height).
- Quantity input in cart: explicit `width: 72px` — not a spacing token, it is a content width (number entry, max 3 digits + buttons).
- Honeypot field: `display: none` — visually hidden, off-screen via CSS (not a `visually-hidden` class, a true `display:none` so it is never focusable).

---

## Typography

Roles inherited from Phase 1. Phase 6 maps all new elements onto existing roles — **no new sizes, no new weights** (declared: 14, 16, 24, 32 px; weights 400 + 600).

| Role | Size | Weight | Line Height | Phase 6 Usage |
|------|------|--------|-------------|---------------|
| Body | 16px | 400 | 1.5 | Cart line-item name, checkout form label text, cart empty-state body |
| Label | 14px | 400 | 1.5 | Cart-link badge text, field help-text, cart page sub-heading, checkout field errors |
| Heading | 24px | 600 | 1.2 | Cart page heading "Giỏ hàng", checkout section heading |
| Display | 32px | 600 | 1.1 | Checkout total leading number |

**Font stack (inherited):** `Noto Sans VN`, `Roboto`, `system-ui`, `-apple-system`, `sans-serif`

### Phase 6 Type Usage Map

| Element | Role | Weight | Notes |
|---------|------|--------|-------|
| Nav cart-link "Giỏ hàng" | Label | 600 | 14px, inline with brand; carries a badge |
| Cart-link badge (item count) | Label | 600 | 14px, pill, `--accent` bg + white text |
| Cart page heading "Giỏ hàng" | Heading | 600 | 24px |
| Cart line-item product name | Body | 400 | 16px, #1F2937 |
| Cart line-item unit price | Label | 400 | 14px, #6B7280, `format_price` |
| Cart line-item quantity input | Body | 400 | 16px input (prevents iOS zoom) |
| Cart line-item line total | Body | 600 | 16px, #2563EB, `format_price` |
| Cart total label "Tổng cộng" | Label | 600 | 14px, #6B7280 |
| Cart total value | Display | 600 | 32px, #2563EB, `format_price` |
| Cart remove-link "Xóa" | Label | 600 | 14px, #DC2626 |
| Empty cart heading "Giỏ hàng trống" | Body | 600 | 16px |
| Empty cart body | Body | 400 | 16px, #6B7280 |
| Empty cart CTA "Tiếp tục mua sắm" | Label | 600 | 14px, btn-primary |
| Checkout section heading "Thông tin đặt hàng" | Heading | 600 | 24px |
| Checkout field labels (Tên, SĐT, Địa chỉ, Ghi chú) | Label | 400 | 14px, #1F2937 |
| Checkout required asterisk | Label | 400 | 14px, #DC2626 |
| Checkout field errors | Label | 400 | 14px, #DC2626 |
| Checkout submit "Đặt hàng" | Label | 600 | 14px, btn-primary |
| Success flash "Đặt hàng thành công..." | Label | 400 | 14px, #059669 |

---

## Color

Base palette inherited unchanged from Phase 1 + Phase 2 badge palette inherited from Phase 2. Phase 6 adds **no new hex values** — only new **accent reservations**.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | #F9FAFB | Page background (inherited) |
| Secondary (30%) | #FFFFFF | Cart card, checkout form card, nav header (inherited) |
| Accent (10%) | #2563EB | Add-to-cart button, checkout submit button, cart total, cart line total, active cart-link hover |
| Destructive | #DC2626 | Remove-link "Xóa" in cart, checkout field errors, required asterisk, honeypot border (never visible — `display: none`) |
| Success semantic | #059669 | Success flash "Đặt hàng thành công..." |
| Neutral semantic | #6B7280 | Cart-link badge text, unit price text, field help-text, "Tổng cộng" label, cart empty-state body |
| Border | #D1D5DB | Inputs (idle), cart table border (inherited) |
| Table header bg | #F9FAFB | Cart table header (inherited `.data-table`) |
| Row hover | #F9FAFB | Cart line-item hover (inherited `.data-table tbody tr:hover`) |

**Accent reserved for (Phase 1 + 2 list, extended for Phase 6):**
1. Primary buttons — "Thêm vào giỏ hàng" (detail), "Đặt hàng" (checkout) (NEW)
2. Price display — product detail price (existing), cart line total, cart total, "Giá" column header (NEW)
3. Cart-link hover text (NEW)
4. Links — back link, brand hover (inherited)
5. Input focus ring / focus border (inherited)
6. Cart-link badge background (`--accent` + white text) (NEW)

**Color usage rules (inherited + Phase 6):**
- All non-link text: #1F2937
- Add-to-cart button: only rendered when `product.status == 'available'` — inherits `.btn-primary` (#2563EB bg, white text, hover #1D4ED8)
- Out-of-stock/discontinued: add-to-cart block hidden; the existing "Sản phẩm hiện đang hết hàng." note (red #B91C1C) remains for out_of_stock; discontinued shows no note (matches existing detail behavior for discontinued — D-07 #5 decision)
- Cart-link badge: `--accent` (#2563EB) background, white text, radius 999px (pill); shows numeric count; hidden entirely when cart is empty (0 items → no badge, but the link "Giỏ hàng" stays visible)
- Cart remove "Xóa" link: #DC2626 (destructive), Label 14px/600
- Checkout honeypot field: `display: none` — invisible, not focusable, never rendered visually; bots that fill it trigger a silent rejection (no flash, no DB write)
- Success flash: #059669 (inherited success semantic)

---

## Layout & Component Contract

### 1. Add-to-Cart Block (product detail page — replaces Messenger CTA)

**Location:** `app/templates/public/product_detail.html` — the `<a class="btn btn-primary messenger-cta">Mua qua Messenger</a>` line is **replaced** by the add-to-cart block. The `.contact-strip` on the **homepage** (`public/index.html`) is **unchanged** — the Messenger CTA stays there.

**Condition:** The entire block renders **only** when `product.status == 'available'`. When `product.status == 'out_of_stock'`, the existing `<p class="out-of-stock-note">Sản phẩm hiện đang hết hàng.</p>` remains (red #B91C1C, D-07 #3). When `product.status == 'discontinued'`, neither block renders (no out-of-stock note, no add-to-cart — matches the "Ngừng bán" badge already shown).

```
[Product info column — .product-info]
  ├── [h1] product name
  ├── [.product-price] price (Display 32px / accent — unchanged)
  ├── [status badge — unchanged]
  │
  │ [NEW — only when status == 'available']
  ├── [.add-to-cart]
  │   ├── [form-field]
  │   │   ├── [label] "Số lượng"        (14px, #1F2937)
  │   │   ├── [input type="number" name="quantity" min="1" max="{{ product.quantity }}"]  (height 44px, border #D1D5DB, focus #2563EB)
  │   │   └── [help-text optional] "Còn {{ product.quantity }} sản phẩm trong kho"  (14px, #6B7280)
  │   └── [a.btn.btn-primary] "Thêm vào giỏ hàng"  → POST to cart-add route  (width 100%, max-width 320px — matches old .messenger-cta sizing)
  │
  ├── [out-of-stock-note — only when status == 'out_of_stock']
  │   [p.out-of-stock-note] "Sản phẩm hiện đang hết hàng."
  │
  ├── [product-meta dl — unchanged]
  └── [product-description — unchanged]
```

**Markup (mirrors existing `.form-field` + `.btn` exactly):**
```html
{% if product.status == 'available' %}
<form class="add-to-cart-form" method="post" action="{{ url_for('public.cart_add', product_id=product.id) }}">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <div class="form-field">
    <label for="cart-quantity">Số lượng</label>
    <input type="number" id="cart-quantity" name="quantity"
           min="1" max="{{ product.quantity }}"
           value="1" required>
    <p class="help-text">Còn {{ product.quantity }} sản phẩm trong kho</p>
  </div>
  <button type="submit" class="btn btn-primary" style="width: 100%; max-width: 320px;">
    Thêm vào giỏ hàng
  </button>
</form>
{% elif product.status == 'out_of_stock' %}
<p class="out-of-stock-note">Sản phẩm hiện đang hết hàng.</p>
{% endif %}
```

**Interaction contract:**
- Form POSTs to `public.cart_add` route (new, see Cart routes below)
- `quantity` input: `min="1"`, `max="{{ product.quantity }}"` — client-side hint; **server re-validates** that 1 ≤ qty ≤ product.quantity at add-time (CONTEXT.md "Server-side validate lại mọi thứ ở checkout"; cart add validates against current stock)
- Default value: `1`
- Input has `required` attribute — no empty submission
- The `.messenger-cta` CSS rule (currently `width: 100%; max-width: 320px; margin-bottom: 8px;`) is repurposed — the new button gets the same sizing via inline style or a shared `.cart-cta` class that mirrors `.messenger-cta`
- No JS on the detail page for the add-to-cart — plain form POST

### 2. Cart-link Badge (public nav header)

**Location:** `app/templates/public/_nav.html` — the brand link "Cửa hàng" gains a sibling "Giỏ hàng" link with a count badge.

```
[Header — .site-header (inherited)]
  └── [.container.site-header__inner — flex row]
      ├── [a.brand] Cửa hàng
      └── [a.cart-link] Giỏ hàng [span.cart-badge — only when count > 0] {N}
```

**Markup:**
```html
<a class="cart-link" href="{{ url_for('public.cart') }}">
  Giỏ hàng
  {% with cart_count = session.get('cart', {}) | length %}
    {% if cart_count > 0 %}
    <span class="cart-badge">{{ cart_count }}</span>
    {% endif %}
  {% endwith %}
</a>
```
```css
.cart-link { font-size: 14px; font-weight: 600; color: var(--text); }
.cart-link:hover { color: var(--accent); }
.cart-badge {
  display: inline-block;
  margin-left: 4px;
  padding: 0 8px;
  height: 20px;
  background: var(--accent);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  border-radius: 999px;
  line-height: 1.5;
}
```
- Badge shows **item count** (number of distinct products in cart, i.e. `len(session['cart'])`), not total quantity
- Badge **hidden entirely** when cart is empty (0 items → no badge rendered; link still visible)
- `session` must be available in template context — Flask `session` is globally accessible in Jinja2 templates when `flask.session` is imported (it is, via Flask context). If not, use a context processor.

**Responsive:** Below 768px, the nav stacks or the cart-link moves inline; at all breakpoints the badge must be ≥44px touch target combined with the link (the link itself is text; badge is non-interactive). The header at ≥768px is single row (brand | search form | cart-link). Below 768px, the existing header stacks (brand on top, search full-width second row) — cart-link appends after search in the stacked layout.

### 3. Cart Page

**Route:** `/cart` (GET) — `public.cart`

**Layout:**
```
[Public header/nav (sticky)]
[Container max 1200px, padding md]
  ├── [Flash zone — inherited]
  ├── [h1.page-heading] Giỏ hàng
  │
  ├── [IF cart is empty]
  │   [.empty-state (inherited style)]
  │   ├── [h2] Giỏ hàng trống
  │   ├── [p] Bạn chưa thêm sản phẩm nào vào giỏ.
  │   └── [a.btn.btn-primary] Tiếp tục mua sắm  → url_for('public.home')
  │
  ├── [IF cart has items]
  │   [.cart-list]
  │   └── [table.data-table — full width]
  │       ├── [thead]
  │       │   ├── [th] Sản phẩm
  │       │   ├── [th] Đơn giá
  │       │   ├── [th] Số lượng
  │       │   ├── [th] Thành tiền
  │       │   └── [th] Xóa
  │       └── [tbody — one row per cart item]
  │           ├── [td]
  │           │   [img thumb 80×80, object-fit cover, radius sm] OR [.thumb 48×48 with "—" if no image]
  │           │   [span] product name (Body 16px/400 #1F2937)
  │           ├── [td] unit price (Label 14px/400 #6B7280, format_price)
  │           ├── [td]
  │           │   [form.cart-qty-form — POST to cart-update]
  │           │   ├── [input type="number" name="quantity" min="1" max="{stock}" value="{qty}"]  (width 72px)
  │           │   └── [button type="submit"] Cập nhật  (btn-secondary, 44px height)
  │           ├── [td] line total (Body 16px/600 #2563EB, format_price)
  │           └── [td]
  │               [a.link-danger] Xóa  (Label 14px/600 #DC2626 → POST to cart-remove)
  │
  │   [...] Checkout form (see below)
  │
  └── [.cart-total]
      ├── [p] "Tổng cộng:" (Label 14px/600 #6B7280) + [span] total (Display 32px/600 #2563EB, format_price)
  └── [.cart-actions]
      ├── [a.btn.btn-secondary] "Tiếp tục mua sắm"  → url_for('public.home')
      └── [button.btn.btn-primary] "Đặt hàng"  (scrolls to / anchors checkout form, OR checkout form is below the table on the same page)
```

**Cart table specifics:**
- Reuses `.data-table` base class (border `#E5E7EB`, header bg `#F9FAFB`, hover `#F9FAFB`)
- Thumbnail: 80×80px `object-fit: cover`, `border-radius: 4px` (sm radius); no-image → `.thumb` placeholder 48×48 with "—" (inherited pattern)
- Quantity input: `width: 72px` (3-digit qty + spinner), height 44px (inherited `.form-field input`), border #D1D5DB, focus #2563EB
- "Cập nhật" button: `.btn.btn-secondary` (white bg, border #D1D5DB, 44px height)
- "Xóa" link: `.link-danger` (#DC2626), Label 14px/600 — **performs a POST** (form + CSRF) to `public.cart_remove` with the product_id; a plain `<a>` cannot make a cross-site-safe POST, so it wraps in a tiny form or uses a GET-to-POST form pattern. Decision (from CONTEXT.md): server-side — use a POST form with CSRF token. The "Xóa" link is a styled submit button inside a minimal inline form.
- Line total + grand total use `format_price` filter (inherited, renders `1.200.000₫`)
- Each row has its own tiny form for quantity update; each remove is its own tiny form

**Cart total:** sum of `(product.price × qty)` for all items — rendered via `format_price` (Display 32px/600)

**Layout decision:** checkout form is **below the cart table on the same page** (single-page cart + checkout, per CONTEXT.md "nghiêng về 1 trang giỏ + checkout liền"). A "Đặt hàng" primary button at the cart-actions area scrolls to / anchors the checkout form. If the user prefers a separate checkout page, the planner may split — but the default contract is single-page.

### 4. Checkout Form (on the cart page, below the table)

**Visible only when cart has items.**

```
[.checkout-section]
  ├── [h2] "Thông tin đặt hàng"  (Heading 24px/600)
  └── [form.checkout-form method="post" action="{{ url_for('public.checkout') }}"]
      ├── [input type="hidden" name="csrf_token" value="{{ csrf_token() }}"]
      ├── [input type="text" name="website" class="honeypot" autocomplete="off"]  (display: none — honeypot)
      │
      ├── [.form-field]
      │   ├── [label] "Họ và tên *"  (Label 14px, #1F2937)
      │   └── [input type="text" name="customer_name"]  (height 44px, border #D1D5DB, focus #2563EB)
      │
      ├── [.form-field]
      │   ├── [label] "Số điện thoại *"  (Label 14px, #1F2937)
      │   └── [input type="tel" name="customer_phone"]  (height 44px)
      │     <p class="help-text">8–11 chữ số, có thể có dấu cách, gạch ngang hoặc dấu cộng</p>
      │
      ├── [.form-field]
      │   ├── [label] "Địa chỉ *"  (Label 14px, #1F2937)
      │   └── [textarea name="customer_address"]  (min-height 120px, border #D1D5DB, focus #2563EB)
      │
      ├── [.form-field]
      │   ├── [label] "Ghi chú (tùy chọn)"  (Label 14px, #6B7280)
      │   └── [textarea name="customer_note"]  (min-height 120px, placeholder "Ví dụ: giao sau 18h, gọi trước khi đến...")
      │
      └── [.form-field]
          └── [button.btn.btn-primary type="submit"] "Đặt hàng"  (width 100%, max-width 320px)
```

**Field contract:**
- `customer_name`: required, `max=100` chars
- `customer_phone`: required, 8–11 digits after stripping spaces/`-`/`+` prefix; regex pattern `^\+?[\d\s-]{8,15}$` and server-side digit-count validation (8–11 digits)
- `customer_address`: required, `max=500` chars
- `customer_note`: optional, `max=1000` chars
- `website` (honeypot): `display: none` — never shown to users; if non-empty on submit → silent rejection (no flash, no DB write, redirect back to cart with no message)
- All inputs: height 44px, padding 0 12px, border 1px #D1D5DB, radius 8px, Body 16px/400 — inherited `.form-field input` styling
- Textareas: min-height 120px, padding 12px, same border/focus — inherited `.form-field textarea`
- Required asterisk: `<span class="required" aria-hidden="true">*</span>` after label text — inherited pattern from admin form
- Field errors: `.field-error` span, Label 14px #DC2626 — inherited

**Responsive behavior:**
- Below 768px: all fields are full-width single column (inherited `.form-field` behavior)
- At ≥768px: optional 2-column row for name + phone (reuses `.form-row-2` from admin form)

---

## Interaction Contracts

### Route Map (all public, no login required)

| Route | Method | Purpose |
|-------|--------|---------|
| `/products/<int:product_id>` | GET | Product detail — add-to-cart block replaces Messenger button (status-gated) |
| `/cart` | GET | View cart (table of items + checkout form) |
| `/cart/add/<int:product_id>` | POST | Add item to session cart (validates qty ≤ stock) |
| `/cart/update/<int:product_id>` | POST | Update item quantity in session cart (validates qty ≤ stock) |
| `/cart/remove/<int:product_id>` | POST | Remove item from session cart |
| `/cart/checkout` | POST | Create Order + OrderItems, clear cart, redirect with success flash |

### Cart Session Shape

```python
# session['cart'] = { product_id (int as str): quantity (int) }
# e.g. {'1': 2, '3': 1}
```
- Stored as string keys (Flask session serializes via JSON; dict keys must be strings)
- Server reads → converts to int → queries Product for fresh data (name, price, images, stock, status)
- Items where the product was deleted, discontinued, or out-of-stock are **filtered out at render time** with a flash notice "Sản phẩm '{name}' đã ngừng bán / hết hàng và được xóa khỏi giỏ."
- Cart is never stale-persisted beyond the session — if product is discontinued after add, it is dropped on next cart view

### Add-to-Cart Flow

1. GET `/products/<id>` — detail page renders add-to-cart block (only when `available`)
2. POST `/cart/add/<id>` with `quantity` field + CSRF token
3. Server: load product → check `status == 'available'` and `quantity > 0` → validate `1 ≤ qty ≤ product.quantity`
4. If invalid: flash error "Số lượng không hợp lệ hoặc sản phẩm đã hết hàng.", redirect back to detail
5. If valid: `session['cart'][str(product_id)] = qty` (replace, not increment — the form sends absolute qty), flash success "Đã thêm {qty} sản phẩm vào giỏ.", redirect to cart page

### Cart Page Flow

1. GET `/cart` — load session cart, fetch fresh product data for each item_id
2. Filter out invalid items (deleted/discontinued/out-of-stock), flash per-item notice
3. Render cart table (line items with thumb + name + price + qty form + line total) + total
4. Below table: checkout form (same page)

### Update Quantity (inline, per-row)

1. POST `/cart/update/<id>` with `quantity` + CSRF
2. Server: validate `1 ≤ qty ≤ product.quantity` (re-check stock — it may have changed)
3. If invalid: flash error "Số lượng vượt quá tồn kho."
4. If valid: update `session['cart'][str(id)] = qty`
5. Redirect back to `/cart`

### Remove Item

1. POST `/cart/remove/<id>` with CSRF (a POST form with a styled "Xóa" link/button)
2. Server: `session['cart'].pop(str(id), None)`
3. Flash success "Đã xóa sản phẩm khỏi giỏ."
4. Redirect back to `/cart`

### Checkout Flow

1. POST `/cart/checkout` with all customer fields + CSRF + honeypot check
2. Honeypot: if `website` field is non-empty → **silent reject**: clear nothing, flash nothing, redirect to `/cart` with no message (bot trap)
3. CSRF: Flask-WTF `CSRFProtect` is already initialized app-wide (`app/__init__.py:54`) — all POST routes protected; template renders `csrf_token()` in every form
4. Validate all fields (name/address/note length, phone 8–11 digits)
5. Server re-validates cart: for each item, reload product → check `status == 'available'` and `quantity > 0` → check `1 ≤ qty ≤ product.quantity`
   - If any item is invalid (sold out, discontinued, qty tampered over stock): flash error "Một số sản phẩm trong giỏ không còn khả dụng. Vui lòng kiểm tra lại giỏ hàng." → redirect to `/cart` (no order created)
6. If all valid: create `Order` (customer_name, customer_phone, customer_address, customer_note, status='Chờ xác nhận') + `OrderItem` rows (product_id FK SET NULL nullable, product_name, product_price, product_cost_price snapshot per item, quantity) in a single `db.session.commit()`
7. Clear `session['cart']` (empty dict)
8. Flash success (green #059669): "Đặt hàng thành công! Chúng tôi sẽ liên hệ xác nhận qua SĐT."
9. Redirect to `public.product_detail` (first product, or home if cart has a single item — CONTEXT.md says "redirect về trang chi tiết")

### Flash Messages (new)

| Type | Message | Trigger |
|------|---------|---------|
| success | "Đặt hàng thành công! Chúng tôi sẽ liên hệ xác nhận qua SĐT." | After successful checkout |
| success | "Đã thêm {qty} sản phẩm vào giỏ." | After add-to-cart |
| success | "Giỏ hàng đã cập nhật." | After quantity update |
| success | "Đã xóa sản phẩm khỏi giỏ." | After remove |
| error | "Số lượng không hợp lệ hoặc sản phẩm đã hết hàng." | Invalid add-to-cart qty |
| error | "Số lượng vượt quá tồn kho." | Invalid update qty |
| error | "Vui lòng nhập đầy đủ Họ và tên, Số điện thoại, và Địa chỉ." | Checkout form validation summary |
| info | "Sản phẩm '{name}' đã ngừng bán / hết hàng và được xóa khỏi giỏ." | Cart page render, stale item removed |

### Accessibility (inherited + Phase 6)

- `lang="vi"`, `charset="utf-8"`, skip link (inherited from `base.html`)
- All form inputs have associated `<label>` (WTForms-generated labels + manual for hand-rolled cart qty forms)
- Add-to-cart, checkout, cart-update, cart-remove all use POST forms with CSRF tokens
- Cart table uses `<table>` + `<thead>` + `<th scope="col">` + `<caption class="visually-hidden">` "Giỏ hàng của bạn"
- Remove link: `<a class="link-danger">Xóa</a>` inside a `<form method="post">` — visually a link, behavior is POST (CSRF-safe). To keep it link-styled but accessible, render it as a `<button type="submit" class="link-danger">Xóa</button>` inside the form, or a styled submit button.
- Touch targets ≥44px (inherited rule); cart qty input is 44px height, buttons 44px, cart-link badge is non-interactive (display only)
- Honeypot field: `display: none` — not focusable, not visible to AT — correct for a trap field
- Phone input: `type="tel"` — brings numeric keypad on mobile (no iOS zoom since it's not a text field)
- All flash messages render in the inherited `.flash-zone` / `.flash` system

---

## Responsive Behavior

| Breakpoint | Max-width | Phase 6 Behavior |
|------------|-----------|------------------|
| Mobile | 480px | Detail: stacked (gallery above info — inherited); cart table horizontally scrollable (`.table-scroll` wrapper) or stacked cards if table overflows; checkout form single-column; cart-link in nav below search |
| Tablet | 768px | Detail: 2-col (gallery 360px — inherited); cart table full-width (no scrollable wrapper needed at 768); checkout form single-column; nav single row (brand | search | cart-link) |
| Desktop | 1200px | Cart table full-width; checkout form uses `.form-row-2` for name + phone; nav single row |

**CSS approach:** Plain CSS — reuse `.data-table`, `.form-field`, `.form-row-2`, `.btn`, `.empty-state`, `.page-heading` classes. New classes: `.cart-badge`, `.cart-link`, `.cart-qty-form`, `.checkout-form`, `.honeypot`, `.cart-total`. Add cart-link to `.site-header__inner` responsive rule. Keep total CSS under inherited ~20KB target.

**Templates touched / created:**
- `app/templates/public/_nav.html` — add cart-link with badge
- `app/templates/public/product_detail.html` — replace Messenger CTA with add-to-cart block (status-gated)
- `app/templates/public/cart.html` — NEW — cart table + empty state + checkout form on one page
- `app/static/css/style.css` — add `.cart-badge`, `.cart-link`, `.honeypot`, reuse `.data-table` for cart

---

## Copywriting Contract

All copy in Vietnamese (`lang="vi"`, PLAT-01). All new copy for Phase 6:

| Element | Copy |
|---------|------|
| Primary CTA (detail page) | "Thêm vào giỏ hàng" |
| Primary CTA (cart page) | "Đặt hàng" |
| Secondary CTA (cart page) | "Tiếp tục mua sắm" |
| Nav cart-link | "Giỏ hàng" |
| Cart page heading | "Giỏ hàng" |
| Cart table headings | "Sản phẩm" · "Đơn giá" · "Số lượng" · "Thành tiền" · "Xóa" |
| Cart qty button | "Cập nhật" |
| Cart total label | "Tổng công:" |
| Empty cart heading | "Giỏ hàng trống" |
| Empty cart body | "Bạn chưa thêm sản phẩm nào vào giỏ." |
| Empty cart CTA | "Tiếp tục mua sắm" |
| Checkout section heading | "Thông tin đặt hàng" |
| Field label — name | "Họ và tên *" |
| Field label — phone | "Số điện thoại *" |
| Field label — address | "Địa chỉ *" |
| Field label — note | "Ghi chú (tùy chọn)" |
| Field help — phone | "8–11 chữ số, có thể có dấu cách, gạch ngang hoặc dấu cộng" |
| Field placeholder — note | "Ví dụ: giao sau 18h, gọi trước khi đến..." |
| Success flash — checkout | "Đặt hàng thành công! Chúng tôi sẽ liên hệ xác nhận qua SĐT." |
| Success flash — add-to-cart | "Đã thêm {qty} sản phẩm vào giỏ." |
| Success flash — update | "Giỏ hàng đã cập nhật." |
| Success flash — remove | "Đã xóa sản phẩm khỏi giỏ." |
| Error — invalid qty (add) | "Số lượng không hợp lệ hoặc sản phẩm đã hết hàng." |
| Error — qty over stock (update) | "Số lượng vượt quá tồn kho." |
| Error — checkout incomplete | "Vui lòng nhập đầy đủ Họ và tên, Số điện thoại, và Địa chỉ." |
| Error — cart stale | "Sản phẩm '{name}' đã ngừng bán hoặc hết hàng và được xóa khỏi giỏ." |
| Field error — name required | "Vui lòng nhập họ và tên." |
| Field error — phone required | "Vui lòng nhập số điện thoại." |
| Field error — phone format | "Số điện thoại phải có 8–11 chữ số." |
| Field error — address required | "Vui lòng nhập địa chỉ." |
| Destructive confirmation | none — no destructive action in this phase (remove is a soft cart action, not a data-destroying operation) |

**Non-goals:** The homepage "Mua qua Messenger" button in `.contact-strip` stays unchanged — only the detail-page Messenger CTA is replaced. No new "Mua qua Messenger" button on cart or checkout pages.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not applicable — shadcn not used (Flask project, not React/Next/Vite) |
| Third-party | none | not applicable — no component registries declared |

**Note:** The shadcn initialization gate does not apply. Tech stack is Python Flask with Jinja2 templates and hand-written CSS (CLAUDE.md "What NOT to Use" bans Tailwind, Bootstrap, React/Vue, shadcn). No new dependencies are added in this phase — CSRF via Flask-WTF (already initialized app-wide in `app/__init__.py:54`), form rendering via WTForms, price formatting via inherited `format_price` filter. The honeypot is a hand-rolled hidden input, not a third-party spam library.

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS — Vietnamese throughout; specific CTA labels ("Thêm vào giỏ hàng", "Đặt hàng", "Tiếp tục mua sắm"); every empty/error state carries actionable copy; phone help-text guides the user on format; no destructive confirmation needed (remove is non-destructive).
- [ ] Dimension 2 Visuals: PASS — add-to-cart replaces Messenger CTA in the same layout slot (no restructure); cart table reuses `.data-table`; checkout reuses `.form-field`/`.form-row-2`; accent reserved for primary CTAs + price display only.
- [ ] Dimension 3 Color: PASS — no new hex values; accent #2563EB reserved for specific elements list; destructive #DC2626 scoped to remove-link + field errors; success #059669 for success flash only.
- [ ] Dimension 4 Typography: PASS — maps onto 4 inherited roles (14/16/24/32); 2 weights (400/600); body line-height 1.5; display 1.1 for total.
- [ ] Dimension 5 Spacing: PASS — all values multiples of 4 from the inherited scale; 12px input padding + 72px qty-input width + 8px cart-badge padding declared as justified exceptions.
- [ ] Dimension 6 Registry Safety: PASS — no third-party registries, no shadcn, no new dependencies; all components hand-rolled.

**Approval:** pending
