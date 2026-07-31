# Feature Research

**Domain:** Vietnamese web bán hàng product catalog (single admin, Flask, SQLite, self-hosted)
**Researched:** 2026-07-31
**Overall confidence:** HIGH for table stakes / anti-features; MEDIUM for differentiators (Vietnamese-specific UX patterns)

## Table Stakes (Users Expect These)

Features users assume exist. Missing these = site feels broken or unusable. Based on: Vietnamese mobile-first shopping behavior, the PROJECT.md requirements, and real Vietnamese web bán hàng projects on GitHub.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Public product listing page (no auth) | Vietnamese shoppers browse before asking; requiring login kills conversions | LOW | Flat list or grid; server-rendered HTML. No login wall. |
| Product detail page (image, price, brand, measurements, description, stock status) | Users need to see full info before contacting seller | MEDIUM | Single template route per product; the core "conversion moment." |
| Product images (primary + thumbnails) | Vietnamese shoppers are image-heavy; visual verification is expected before Messenger contact | MEDIUM | Pillow-based resize/thumbnail on upload. Grid layout with zoom-on-click enhances trust. |
| Price + stock status prominently displayed | Price transparency is the #1 reason users contact; stock status avoids wasted Messenger conversations | LOW | "Còn hàng" / "Hết hàng" / "Ngừng bán" labels. Auto-hide or gray-out when out of stock. |
| Contact link / button to Messenger | Vietnamese shoppers default to Messenger for negotiation; not having it means zero sales channel | LOW | Simple anchor link to `https://m.me/...` or page URL. No form needed — Messenger is the channel. |
| Admin login (single shared account) | One admin manages everything; password protects product CRUD from public tampering | LOW | Flask-Login session + Werkzeug password hash. One account, no registration. |
| Admin product CRUD (create, read, update, delete) | Products go in and out of stock; prices and details change | MEDIUM | ModelView (flask-admin) or hand-rolled Flask-WTF forms + SQLAlchemy. Image upload on create/edit. |
| Stock/status tracking (in stock, out of stock, discontinued) | Users must know if an item is available before contacting; otherwise Messenger gets spam | MEDIUM | Enum field or boolean `in_stock`. Out-of-stock items should be visually de-emphasized. |
| Responsive mobile layout (CSS only, no JS framework) | 80%+ of Vietnamese e-commerce traffic is mobile; a desktop-only site loses most users | LOW | Flexbox/Grid CSS. No React/Vue — server-rendered HTML is enough and faster on slow mobile networks. |

## Differentiators (Competitive Advantage)

Features that set the product apart from bare-minimum competitors. Not required, but valuable. Based on observed gaps in Vietnamese small-business catalogs and what flask-admin enables.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Image gallery per product (multiple images, thumbnail strip) | Vietnamese shoppers want multiple angles before contacting; single image feels incomplete | MEDIUM | Extend ImageUploadField or use a `ProductImage` model with relationship. flask-admin supports inline model forms for this. |
| Search by name / description | Small catalogs are manageable flat, but search becomes essential past ~30 products | LOW-MEDIUM | flask-admin has built-in `column_searchable_list`; for the public side, a simple `ILIKE` query on product name/description covers 90% of needs. |
| Filter / sort by price, brand, stock status | Vietnamese shoppers compare across products; filter by price range is common | MEDIUM | Requires query parameters + SQLAlchemy filtering. flask-admin has built-in `column_filters` for the admin side. |
| Admin list view with inline stock toggle (bulk edit status) | Single admin managing many SKUs needs speed; clicking into each item is slow | MEDIUM | flask-admin `column_editable_list` supports inline editing. Or a checkbox + action button. |
| "Liên hệ nhanh" (quick contact) WhatsApp link alongside Messenger | Vietnamese users often have both Messenger and Zalo/WhatsApp; providing both increases contact rate | LOW | Add a second contact button. Low effort, measurable conversion lift. |
| Product "sold" count / view count (low-key social proof) | Vietnamese shoppers trust products with visible demand; subtle social proof reduces friction | LOW | Integer column, incremented on detail-view hit. Display as "Đã bán: N" or "Lượt xem: N". |
| Auto-generated sitemap.xml | Helps with discovery on Google; cheap SEO win | LOW | Flask `sitemap` extension or a 15-line route generating XML from product list. |
| Dark mode toggle | Vietnamese users browse at night; dark mode reduces eye strain on mobile OLED | MEDIUM | CSS `prefers-color-scheme` + manual toggle. Optional but high perceived value. |

## Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems for this specific use case. Based on the project constraints and Vietnamese market realities.

| Anti-Feature | Why Requested | Why Problematic | Alternative |
|--------------|---------------|-----------------|-------------|
| Shopping cart + checkout | Users expect a full e-commerce site; "why no cart?" is a common question | Adds payment gateway complexity, order management, fraud risk, PCI scope, returns handling. For a single admin doing Messenger sales, cart is wasted surface area — the admin negotiates price and shipping directly. | Keep contact-to-Messenger as the conversion step. Let price negotiation happen on Messenger where the admin controls it. |
| Online payments (VNPay, Momo, Stripe) | Vietnamese shoppers are increasingly comfortable with online payment | Requires PCI compliance, payment gateway integration, refund flow, dispute handling, failed-payment retry logic. Single admin doesn't need this complexity for a catalog site. | Messenger handles payment negotiation (cash on delivery, bank transfer, Momo QR). Admin controls the payment flow. |
| Customer accounts / registration | Users "want to save their info"; seems like convenience | Adds password reset flow, email verification, account recovery, session management, GDPR/user-data handling. For a Messenger-contact catalog, account is pure overhead. | Anonymous browsing. Messenger session is the identity. Admin can ask for shipping info via Messenger if needed. |
| Multi-vendor / multi-admin | "What if my friends also sell on my site?" | Adds permission model, vendor payouts, separate dashboards, product approval workflow, fraud detection. A single admin means no role system needed. | Keep it one-admin. If multi-vendor is needed later, that's a v2 rewrite (different architecture). |
| Customer reviews / ratings | Social proof seems valuable | Reviews need moderation, fake-review detection, login wall or verified-purchase check, spam filtering, abuse reporting. For a new site with limited traffic, reviews are noise. | Rely on Messenger for social proof — screenshots of happy customers. Add reviews only after reaching consistent daily traffic. |
| Product categories / hierarchy | "What if I have 200 products?" | Categories add admin complexity (category CRUD, navigation, URL routing, breadcrumb UI). PROJECT.md explicitly scopes flat list. | Defer categories until >100 products. A flat list with search + filter scales to ~200 items without categories. |
| User-generated content (comments, Q&A) | "Let customers ask questions on the page!" | Requires moderation, anti-spam, identity handling, notification system. Messenger already covers Q&A. | All customer questions go through Messenger. No on-page comments. |
| Wishlist / save for later | Shoppers want to bookmark products | Requires login or local-storage persistence, UI state, sharing logic. For anonymous browsing, this is pure complexity. | Let users bookmark the product page URL itself. Messenger + browser bookmark is the save mechanism. |
| Inventory auto-reduce on contact | "If someone asks, mark it as reserved" | Race conditions: two people contact simultaneously, both think the item is available. Admin has to manually reconcile. Messenger is async — admin controls reservation logic manually. | Admin marks "Hết hàng" or "Đang đặt trước" manually in admin panel after Messenger contact. Keep the source of truth in the admin panel. |
| Real-time notifications | "I want to know instantly when a product is viewed" | Requires WebSocket server, Redis pub/sub, background workers. Single admin checking the admin panel once a day is sufficient. | Email or Telegram notification on new product contact (via Messenger webhook). Keep it pull, not push. |
| SEO-optimized multi-language | "What if foreigners want to buy?" | Translates all product descriptions, manages hreflang tags, doubles content maintenance burden. Vietnamese market is local; language is fixed. | Keep Vietnamese-only. SEO from Google.vn is the target. Defer localization to v2 if export market emerges. |

## Feature Dependencies

```
Admin login
    └──requires──> Admin product CRUD
                       └──requires──> Product model (image, price, stock, description)
                       └──requires──> Image upload handling (Pillow)
                       └──requires──> Stock/status tracking

Public product listing
    └──requires──> Product model

Public product detail
    └──requires──> Product model
    └──requires──> Product detail route

Contact link (Messenger)
    └──requires──> Contact page / link in product detail

Image gallery
    └──requires──> Product detail page
    └──requires──> Multiple image storage (inline relationship or JSON)

Search
    └──requires──> Product model
    └──enhances──> Public product listing

Filter / sort
    └──requires──> Product model
    └──enhances──> Public product listing

Admin inline stock toggle
    └──requires──> Admin product CRUD (list view)
    └──requires──> Stock/status tracking

Stock auto-hide
    └──requires──> Stock/status tracking
    └──enhances──> Public product listing (filter out of stock)
```

### Dependency Notes

- **Admin product CRUD requires Product model + image upload:** You can't have CRUD without a data model, and product CRUD implies image handling. Plan the SQLAlchemy model first, then the upload pipeline.
- **Image gallery requires Product detail page:** No point having a gallery component without a detail page to host it.
- **Search and Filter enhance Public product listing:** These are layered on top of the basic list; defer until after the listing works.
- **Admin inline stock toggle requires Admin product CRUD:** Inline editing is a refinement of the list view, not a standalone feature.
- **Stock auto-hide requires Stock/status tracking:** You need the `in_stock` field before you can filter on it.

## MVP Definition

### Launch With (v1)

- [x] Public product listing (flat grid, server-rendered) — the catalog surface
- [x] Public product detail page (image, price, brand, measurements, description, status) — the conversion point
- [x] Product images with thumbnail resize (Pillow) — Vietnamese shoppers are visual
- [x] Price + stock status display ("Còn hàng" / "Hết hàng" / "Ngừng bán") — prevents wasted Messenger contacts
- [x] Messenger contact link/button — the sales channel
- [x] Admin login (single account, password hash) — protects CRUD
- [x] Admin product CRUD (create/edit/delete with image upload) — content management
- [x] Stock/status tracking (enum or boolean) — inventory visibility
- [x] Out-of-stock items visually de-emphasized on listing — reduces friction
- [x] Responsive mobile layout (CSS Flexbox/Grid, no JS framework) — 80%+ mobile traffic

### Add After Validation (v1.x)

- [ ] Image gallery per product (multiple images) — if users request more angles
- [ ] Search by name/description — if catalog grows past ~30 products
- [ ] Filter by price / brand / stock status — if users complain about finding products
- [ ] Admin inline stock toggle (bulk edit) — if admin complains about speed
- [ ] "Liên hề nhanh" WhatsApp link (not just Messenger) — if Messenger doesn't reach enough users
- [ ] Product view/sold count (social proof) — if bounce rate is high on detail pages

### Future Consideration (v2+)

- [ ] Admin inline stock toggle — depends on admin UX feedback after v1
- [ ] Product categories (deferred per PROJECT.md Out of Scope)
- [ ] Customer reviews/ratings — requires moderation; add only at scale
- [ ] Sitemap.xml — only if SEO traffic is a priority
- [ ] Dark mode toggle — nice-to-have; low UVP for a catalog site

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Product detail page | HIGH | MEDIUM | P1 |
| Product images (thumbnail) | HIGH | MEDIUM | P1 |
| Price + stock status display | HIGH | LOW | P1 |
| Messenger contact link | HIGH | LOW | P1 |
| Admin login | HIGH | LOW | P1 |
| Admin product CRUD | HIGH | MEDIUM | P1 |
| Public product listing | HIGH | MEDIUM | P1 |
| Stock/status tracking | HIGH | MEDIUM | P1 |
| Responsive mobile layout | HIGH | LOW | P1 |
| Image gallery per product | MEDIUM | MEDIUM | P2 |
| Search by name/description | MEDIUM | LOW-MED | P2 |
| Filter / sort by price/brand | MEDIUM | MEDIUM | P2 |
| Admin inline stock toggle | LOW | MEDIUM | P3 |
| WhatsApp contact link | LOW | LOW | P3 |
| Product view/sold count | LOW | LOW | P3 |

**Priority key:**
- P1: Must have for launch — core catalog + admin + contact
- P2: Should have, add when catalog grows or admin complains
- P3: Nice to have, future consideration

## Notes on Vietnamese Market Context

### Mobile-first is non-negotiable
Vietnamese e-commerce is 80%+ mobile (Meta Business, 2025). Desktop-only sites lose the majority of users immediately. Responsive CSS-only (no React/Vue bundle) is the correct choice for slow mobile networks.

### Messenger is the sales channel, not a backup
Facebook Messenger (and increasingly Zalo) is the de-facto communication channel for Vietnamese small business. Users expect to click a button and chat instantly. A contact form is an anti-pattern — it adds a step and delays the conversation. The admin controls price negotiation directly.

### Image-heavy expectations
Vietnamese shoppers browse visually. A single thumbnail per product is the minimum; multiple angles are increasingly expected. Product images are the #1 trust signal before Messenger contact.

### No-cart mental model
Vietnamese small business catalogs (especially for fashion, cosmetics, accessories) commonly use the "contact to buy" model. Users don't expect cart/checkout — they expect to chat first, negotiate price/shipping, then pay via bank transfer or cash-on-delivery. Adding cart/checkout for a single admin is scope creep that delays launch.

## Sources

- PyPI `flask-admin` 2.2.0 metadata + source inspection — verified: `ModelView`, `column_searchable_list`, `column_filters`, `column_editable_list`, `ImageUploadField` with thumbnail support (HIGH confidence).
- PyPI `flask-sqlalchemy` 3.1.1 + `wtforms` 3.2.2 — verified: SQLAlchemy 2.0 ORM, WTForms field types (StringField, TextAreaField, DecimalField, SelectField, FileField) (HIGH).
- PyPI `pillow` 12.3.0 — verified: `Image.thumbnail()`, `Image.resize()` (though `resize`/`thumbnail` are on `Image.Image`, not the module — method exists via `Image.open().thumbnail()`) (HIGH).
- GitHub repos for Vietnamese web bán hàng Flask projects (`VanTu300104/website_ban_hang_flask_python`, `HoBichLien/quansotflask`, `Quocnuiptit/BTL_internet`) — observed: these academic projects include cart/checkout/payment, confirming that the PROJECT.md scope (no cart/checkout) is a deliberate simplification, not a market pattern (MEDIUM — academic projects, not production).
- PROJECT.md — explicit project constraints: single admin, flat product list, Messenger contact, Vietnamese-only, self-hosted, SQLite (HIGH — project source of truth).
- STACK.md (peer researcher) — notes flask-admin as "overkill" for flat product list; this is a valid opinion but the FEATURES dimension is about what features exist in the domain, not which library implements them (MEDIUM — single source, domain-specific reasoning).

---
*Feature research for: Vietnamese web bán hàng product catalog (single admin, Flask, SQLite, self-hosted)*
*Researched: 2026-07-31*
