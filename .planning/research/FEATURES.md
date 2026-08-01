# Feature Research — v1.1 Buy System (order placement + tracking + stats)

**Domain:** Vietnamese web bán hàng product catalog (single admin, Flask, SQLite, self-hosted)
**Researched:** 2026-08-02
**Overall confidence:** HIGH for table stakes / anti-features; MEDIUM for differentiators (Vietnamese-specific UX patterns)

## Category 1: Public Order Placement

### Table Stakes (users expect these)
| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Order form on product detail (name, phone, address, quantity, note) | Vietnamese buyer who decides to buy fills the form directly instead of switching to Messenger | LOW–MEDIUM | Reuses `OrderForm`; replaces the "Mua qua Messenger" CTA |
| Required name/phone/address, quantity ≥ 1 | Seller needs contact + delivery info to fulfil | LOW | WTForms `DataRequired` + `NumberRange(min=1)` |
| Quantity capped at stock | Prevents ordering more than available | MEDIUM | Validate against `product.quantity` server-side |
| Clear success feedback after submit | Buyer must know the order went through | LOW | Flash success + hide the form / show "Đơn hàng đã gửi" |
| Unavailable products cannot be ordered | Hết hàng / Ngừng bán items shouldn't accept orders | LOW | Hide form when status != available |
| CSRF on the public form | Prevents cross-site order spam | LOW | Global CSRFProtect already active; render `hidden_tag()` |

### Differentiators
| Feature | Complexity | Notes |
|---------|------------|-------|
| VN-specific phone validation (10–11 digits, 0x/84x prefixes) | MEDIUM | Regex; loose enough to not reject landlines |
| Note field (ghi chú) | LOW | Optional; buyer can add size/color/delivery notes |
| Keep Messenger contact strip alongside the order form | LOW | Buyer who has questions still reaches the seller; CTA becomes "Liên hệ hỏi thêm" not "Mua" |

### Anti-features (don't build)
- Cart / multi-product order — out of scope (each order = 1 product)
- Customer accounts / login — anonymous order is simpler
- Online payment — transaction settles on delivery
- Email/SMS order confirmation — no infra, seller contacts by phone

## Category 2: Admin Order Tracking

### Table Stakes
| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Order list (paginated, status filter) | Admin sees all orders without scrolling | MEDIUM | Reuse `pagination` pattern from products/list |
| Order detail (customer info, product, quantity, price, note, timestamps) | Admin has everything to fulfil | MEDIUM | One route + template |
| Advance status: đã gói → đã gửi → đã nhận | Milestone explicitly requires the flow | LOW | `OrderStatusForm` (SelectField, integer enum) |
| Cancelled bucket (admin-only) | Data hygiene — no hard deletes; stats stay cumulative | LOW | `ORDER_STATUS_CANCELLED = 0` |
| Status badge colors | Admin scans list quickly | LOW | Reuse badge CSS pattern |

### Differentiators
| Feature | Complexity | Notes |
|---------|------------|-------|
| Updated timestamp per status change | Audit trail "when did this move?" | LOW | `updated_at` onupdate |
| Reject invalid transitions (skip backwards) | Prevents accidental regressions | LOW | Guard in route: new status must be a forward step |

### Anti-features
- Multi-role staff accounts — single admin only
- Notifications to customer (SMS/email) — none
- Auto stock decrement on order — see PITFALLS #9 (defer: seller manages stock manually)

## Category 3: Cost Price (giá nhập)

### Table Stakes
| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Optional `cost_price` field on product form (admin-only) | Milestone requirement | LOW | `Integer` nullable, rendered after `price` |
| Never rendered to public | Price disclosure is business-sensitive | LOW | Only in admin templates |

### Differentiators
| Feature | Complexity | Notes |
|---------|------------|-------|
| Show profit margin hint on the admin product form | Immediate feedback to seller | LOW | Optional; not required |

### Anti-features
- Public cost display — never
- Float precision — integer VND only

## Category 4: Admin Stats Dashboard

### Table Stakes
| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Total revenue (đã gửi + đã nhận orders) | Core money metric | MEDIUM | `SUM(price_at_order * quantity)` with status filter |
| Profit = revenue − cost | Requires cost price snapshot | MEDIUM | `SUM((price_at_order - cost_price_at_order) * quantity)`; NULL-safe |
| Number of orders (by status / total) | Operational overview | LOW | `COUNT` grouped by status |
| Products sold (units in delivered+shipped orders) | Sales volume | LOW | `SUM(quantity)` with status filter |
| Inventory counts (total products, hết hàng, ngừng bán) | Stock overview | LOW | Existing product data |

### Differentiators
| Feature | Complexity | Notes |
|---------|------------|-------|
| Stat cards with `format_price` (₫) | Clear money presentation | LOW | Reuse filter |
| Status-filter scope (revenue only from shipped+delivered) | Accurate money, not overcounting pending | LOW | Consistent `WHERE status >= SHIPPED` |

### Anti-features
- Charts / graphs — plain cards suffice for single admin
- Date-range filters / export CSV — defer to later milestone
- Per-product profit table — not requested

## Cross-cutting Notes
- All money: integer VND (existing `price` pattern), never Float.
- Every order records `price_at_order` + `cost_price_at_order` snapshots so later price edits never corrupt historical revenue/profit (see ARCHITECTURE.md anti-patterns).
- Stats computed live via SQL aggregates at request time; no summary/cache table (low volume).

---
*Feature research for: StoreWeb v1.1 Buy System (order placement + tracking + stats)*
*Researched: 2026-08-02*
