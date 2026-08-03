---
phase: 5
slug: data-model-migration
status: approved
shadcn_initialized: false
preset: none
created: 2026-08-02
reviewed_at: 2026-08-02
---

# Phase 5 — UI Design Contract

> Visual and interaction contract for the data-model + migration phase. Unlike prior phases, Phase 5 adds **no new pages and no new components** — it is infrastructure-heavy (Order model + idempotent SQLite migration). The ONLY user-facing UI change is **one optional "Giá nhập (VND)" field** added to the existing admin product create/edit form (`app/templates/admin/products/form.html`). This contract therefore specifies only that single field, referencing the established design system rather than re-specifying it.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — Flask server-rendered Jinja2 templates with hand-written CSS |
| Preset | not applicable |
| Component library | none (hand-rolled form fields; no new components) |
| Icon library | none |
| Font | Noto Sans VN (fallback chain per Phase 1) |

**Authoritative design system references (not re-specified here):**
- `01-UI-SPEC.md` — baseline: colors `#2563EB`/`#F9FAFB`/`#FFFFFF`/`#1F2937`/`#6B7280`/`#DC2626`, type 14/16/24/32, spacing 4/8/16/24/32/48/64, breakpoints 480/768/1200
- `02-UI-SPEC.md` — admin product form contract: `.form-field` rhythm, `.form-row-2`, input styling, `.help-text`, `.field-error`, `.btn` variants

**Phase 5 extension:** a single new field on the existing admin product form. No token, class, or style changes. No public-page template is touched.

---

## Spacing Scale

Inherited unchanged. No new tokens.

| Token | Value | Phase 5 Usage |
|-------|-------|---------------|
| md | 16px | New field's vertical rhythm (`margin-bottom: 16px` via existing `.form-field` — identical to every existing field) |

**Exceptions:** none.

The new field uses only existing classes (`.form-field`, `.input`, `.help-text`) so no spacing additions are required. It must NOT introduce custom margin/padding values.

---

## Typography

Inherited unchanged. The new field maps onto the existing form roles — no new sizes, no new weights.

| Role | Size | Weight | Line Height | Phase 5 Usage |
|------|------|--------|-------------|---------------|
| Label | 14px | 400 | 1.5 | "Giá nhập (VND)" field label; help-text "Chỉ quản trị viên xem được" |
| Body | 16px | 400 | 1.5 | Cost-price input text (16px minimum — prevents iOS auto-zoom on focus) |
| Field error | 14px | 400 | 1.5 | "Giá nhập không được âm" (inherited `.field-error`, color #DC2626) |

**Declared weights:** exactly 2 — regular (400) and semibold (600). The cost-price field uses 400 only (it is optional, not a heading).

---

## Color

Inherited unchanged. No new tokens. The new field reuses the existing form color contract.

| Role | Value | Phase 5 Usage |
|------|-------|---------------|
| Dominant (60%) | #F9FAFB | Page background (unchanged) |
| Secondary (30%) | #FFFFFF | Form card background (unchanged) |
| Accent (10%) | #2563EB | Input focus ring + focus border on the cost-price input only |
| Neutral semantic | #6B7280 | Help-text "Chỉ quản trị viên xem được" under the cost-price input |
| Destructive | #DC2626 | Field error text (negative-value validation) |

**Color rules applied (inherited, not new):**
- Input border #D1D5DB idle → #2563EB on focus (2px ring, offset 2px).
- Field label color #1F2937.
- No required asterisk — the field is optional (no `.required` span, no `aria-required`, no `required` attribute).

---

## Copywriting Contract

All copy in Vietnamese (PLAT-01). This phase introduces exactly **one new label** and **one new field error**; everything else is inherited.

| Element | Copy |
|---------|------|
| New field label | "Giá nhập (VND)" |
| New field help text | "Chỉ quản trị viên xem được" (reused verbatim from the existing "Ghi chú nội bộ" field — reinforces admin-only + COST-02) |
| New field error (negative value) | "Giá nhập không được âm" (parallels existing "Giá không được âm") |
| Primary CTA | not applicable — no new CTA in this phase; inherited "Lưu sản phẩm" (Phase 2) |
| Empty state | not applicable — no new empty state; inherited product list empty state (Phase 2) |
| Error state | not applicable — no new error state; inherited form summary "Vui lòng kiểm tra lại các trường nhập." (Phase 2) |
| Destructive confirmation | not applicable — no destructive action in this phase |

**Explicit non-goals (COST-02):** the label "Giá nhập" and the help-text must **never appear on any public-facing template** (`app/templates/public/**`). The cost price is admin-only, matching the existing `admin_note` visibility rule. No public page copy changes.

---

## Layout & Component Contract

### The Single Field Addition

```
[Form card — app/templates/admin/products/form.html]
  ...
  ├── [Field row 2-col]  Giá (VND) * [input number] | Thương hiệu [input text]
  ├── [NEW Field]  Giá nhập (VND)  [input number]     ← added here, full-width
  │                [help-text] Chỉ quản trị viên xem được
  ├── [Field row 2-col]  Mã sản phẩm (SKU) [input text] | Thứ tự hiển thị [input number]
  ...
```

- **Placement:** immediately after the existing "Giá (VND) | Thương hiệu" `form-row-2`, as its own full-width `.form-field`. This groups the two price fields together (Giá bán + Giá nhập) and requires **no restructuring** of any existing row.
- **Markup** (mirrors the existing field pattern exactly):
  ```html
  <div class="form-field">
    {{ form.cost_price.label }}
    {{ form.cost_price(class="input", min="0", step="1") }}
    <p class="help-text">Chỉ quản trị viên xem được</p>
    {% for error in form.cost_price.errors %}<span class="field-error">{{ error }}</span>{% endfor %}
  </div>
  ```
- **No `required` attribute, no `.required` span, no `aria-required`** — optional field (matches `sku`, `sort_order`, `admin_note` treatment).
- **Input attributes:** `type="number"`, `min="0"`, `step="1"` (integer VND, D-05). Height 44px, padding 0 12px, border 1px #D1D5DB, radius 8px — all inherited from the existing `.input` styling. No new CSS.
- **Responsive:** full-width field, single column, no `.form-row-2` — nothing to collapse. No CSS changes.

---

## Interaction Contracts

### WTForms + Model Contract

- `app/models.py` — add nullable `cost_price` column to `Product`:
  `cost_price = db.Column(db.Integer, nullable=True)` — VND integer only, never Float (D-05). NULL = not entered.
- `app/forms.py` — add field to `ProductForm`:
  ```python
  cost_price = IntegerField('Giá nhập (VND)', validators=[Optional(), NumberRange(min=0, message='Giá nhập không được âm')])
  ```
  - `Optional()` — empty input → stored as NULL (matches `sku`, `sort_order` pattern).
  - `NumberRange(min=0)` — negative rejected, matching the existing "Giá không được âm" validation behavior.
- `app/admin.py` — no route change needed; `ProductForm(obj=product)` already binds the new field. Verify create + edit both persist `cost_price`.
- **No public route, template, or model property exposes `cost_price`** (COST-02). The `format_price` filter is never applied to it on public pages.

### Migration (non-UI, documented for plan traceability)

- `app/db.py` `init-db` CLI: `PRAGMA table_info(products)` guard before `ALTER TABLE products ADD COLUMN cost_price INTEGER`; `create_all` creates the new `orders` table (PLAT-05). Idempotent — runs safely on fresh and existing v1.0 DBs. No UI interaction.

### Flash messages

- No new flash messages. Existing success flash "Lưu sản phẩm thành công" / "Đã cập nhật sản phẩm “{tên}”" (Phase 2) already cover the cost-price save.

### Accessibility (inherited)

- `<label>` associated with the input (WTForms `form.cost_price.label` renders it).
- Input reachable via keyboard; focus ring 2px #2563EB inherited.
- Help-text is a `<p>` adjacent to the field (screen-reader reachable; the `admin_note` field already establishes this pattern).
- No `required` semantics — correct, since the field is optional.

---

## Responsive Behavior

No new behavior. The added full-width field inherits the existing single-column form layout at all breakpoints (480 / 768 / 1200). No media queries change.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not applicable — shadcn not used (Flask project, not React/Next/Vite) |
| Third-party | none | not applicable — no component registries declared |

**Note:** The shadcn initialization gate does not apply. Tech stack is Python Flask with Jinja2 templates and hand-written CSS. No new dependencies are added in this phase (research SUMMARY: "zero new dependencies"). All form elements are hand-rolled per CLAUDE.md "What NOT to Use".

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PENDING — one new label ("Giá nhập (VND)"), one reused help-text, one new field error; COST-02 public-visibility guard specified
- [ ] Dimension 2 Visuals: PENDING — single field addition; no new layout, no new component
- [ ] Dimension 3 Color: PENDING — no new tokens; inherited #2563EB focus / #6B7280 help / #DC2626 error
- [ ] Dimension 4 Typography: PENDING — maps onto existing Label/Body/Field-error roles; no new sizes/weights
- [ ] Dimension 5 Spacing: PENDING — single 16px `.form-field` rhythm; no exceptions
- [ ] Dimension 6 Registry Safety: PENDING — no registry, no shadcn, no new dependencies

**Approval:** pending
