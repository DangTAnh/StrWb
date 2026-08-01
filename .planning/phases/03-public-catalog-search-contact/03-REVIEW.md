---
phase: 03-public-catalog-search-contact
reviewed: 2026-08-01T15:10:00Z
depth: deep
files_reviewed: 14
files_reviewed_list:
  - app/public.py
  - app/templates/base.html
  - app/templates/public/base.html
  - app/templates/public/_nav.html
  - app/templates/public/_product_card.html
  - app/templates/public/index.html
  - app/templates/public/product_detail.html
  - app/templates/public/search.html
  - app/static/css/style.css
  - app/models.py
  - app/image_utils.py
  - app/__init__.py
  - app/templates/errors/404.html
  - app/templates/errors/500.html
findings:
  blocker: 0
  high: 0
  medium: 1
  low: 5
  total: 6
status: issues_found
---

# Phase 3: Public Catalog + Search + Contact — Code Review Report

**Reviewed:** 2026-08-01T15:10:00Z
**Depth:** deep (cross-file trace + empirical probes via Flask test client)
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Phase 3 delivers the public catalog (home grid with 12/page pagination ordered by `sort_order` then `id`), the product detail page (gallery + info order + Messenger CTA + back link), and diacritic-insensitive search (`normalize_search_text` NFD→strip-Mn→casefold applied to both keyword and name/description, in-Python filter + manual pagination). All routes render 200/404 correctly, XSS is fully neutralized (Jinja autoescape everywhere, zero `|safe`, all `{{ q }}` / product-field interpolations confirmed escaped), no auth leak on public routes (`admin_note` never rendered), no SQL injection (no raw SQL), and `normalize_search_text` is ReDoS-safe (`unicodedata` is linear, no regex). `page` is int-coerced everywhere, so non-int page values never 500. `pagination.total` in search correctly reflects the FILTERED match count. Search correctly includes discontinued/out-of-stock products (consistent with the grid, which hides nothing).

Review found **1 medium and 5 low** issues; no blocker/high defects. Each finding was reproduced with a Flask test client against the real app (isolated temp DB), not merely read from source. All findings are reachable via normal URL input or a documented deployment path.

**Verification method:** Flask test client (`GET /`, `/?page=9999`, `/?page=abc`, `/?page=0`, `/?page=-3`, `/search?q=...`, `/products/999999`) against a fresh temp DB; `normalize_search_text` unit checks; rendered-HTML assertions for escaping.

## Medium Issues

### WR-01: Home catalog pagination out-of-range `page` renders a misleading "store is empty" state

**File:** `app/public.py:34-38` (root cause) + `app/templates/public/index.html:5,18-23`

**Issue:** `home` passes the raw `page` into `Query.paginate(page=..., error_out=False)`. Flask-SQLAlchemy's `_prepare_page_args` only coerces `page < 1` to 1; a `page` *above* the last page is left untouched, so `pagination.items` is `[]` and `pagination.page` stays at the requested value (e.g. 9999). The template's `{% if products %}` / `{% else %}` then renders the **"Chưa có sản phẩm nào"** empty state — the same copy used for a genuinely empty store. A customer (or the store owner) hitting `/?page=9999` is told the shop has no products even though 18 products exist. The search route handles this correctly via `_manual_pagination`'s clamp — the two routes are inconsistent.

**Empirical proof:**
```
GET / (18 products)        -> 200, grid "Trang 1 / 2"
GET /?page=9999            -> 200, "Chưa có sản phẩm nào"  (false empty-store state, no "Trang" indicator)
GET /search?q=sản&page=9999 -> 200, clamps to "Trang 2 / 2"  (search clamps correctly)
GET /?page=abc / 0 / -3    -> 200, product shown (int-coercion + page<1 clamp OK)
```

**Fix:** clamp or redirect `page` in the home route the same way search does, e.g.:

```python
pagination = Product.query.order_by(Product.sort_order.asc(), Product.id.asc()).paginate(
    page=page, per_page=12, error_out=False
)
if pagination.total and pagination.page > pagination.pages:
    return redirect(url_for('public.home', page=pagination.pages))
```

(or reuse `_manual_pagination`'s clamp before building the query). This keeps the "empty store" copy reserved for a store with zero products.

## Low Issues

### WR-02: Query that normalizes to empty (lone combining marks) renders the no-results state instead of the empty-query prompt

**File:** `app/public.py:56-57` + `app/templates/public/search.html:6`

**Issue:** The route's empty check is on the **normalized** string (`if not nq:` → render prompt template with `products=None`), but the template's state check is on the **raw** string (`{% if not q %}`). A query such as a lone combining acute (`q=%CC%81`) strips to a truthy raw `q` but normalizes to `''`, so the route sends the prompt template while the template falls through `not q` → `elif products` (products is None, falsy) → the **"Không tìm thấy sản phẩm"** branch — claiming zero results for a search that never ran. Verified empirically.

**Fix:** key the prompt state on `products is none` (the route sets it only for the empty-normalized case), not on raw `q`:

```jinja
{% if products is none %}
<div class="empty-state">... Vui lòng nhập từ khóa ...</div>
{% elif products %}
...results...
{% else %}
...no-results...
{% endif %}
```

### WR-03: Detail-page "Quay lại" same-site check breaks behind a TLS reverse proxy (no ProxyFix) — back link silently falls to home

**File:** `app/templates/public/product_detail.html:5`

**Issue:** `{% if request.referrer and request.referrer.startswith(request.host_url) %}` compares the referrer against `request.host_url`, which is built from `request.scheme` + host. The documented production path (CLAUDE.md) is nginx terminating TLS in front of waitress/gunicorn, and `app/__init__.py` installs no `ProxyFix` and sets no `PREFERRED_URL_SCHEME`. In that topology `request.host_url` is `http://...` while browser referrers are `https://...`, so every same-site referrer fails the `startswith` check and "Quay lại" always falls back to `public.home` — a customer browsing page 3 of search results loses their place on every detail visit. Not a crash (graceful fallback), but the intended back-navigation silently never works in the target deployment. Latent today (dev is http); will manifest at Phase 4 deploy.

**Fix:** compare only the origin (scheme + netloc), e.g.:

```python
# context-processor or template helper, or inline:
from urllib.parse import urlsplit
same_site = bool(
    request.referrer and urlsplit(request.referrer).netloc == request.host
)
```

or configure `ProxyFix` / `PREFERRED_URL_SCHEME='https'` for the deployment.

### WR-04: Orphaned `.coming-soon` CSS rule (dead code)

**File:** `app/static/css/style.css:50-51`

**Issue:** The `.coming-soon` block is the Phase 1 "Cửa hàng đang chuẩn bị" layout; Phase 3 replaced the coming-soon page with the real catalog grid, and no template renders an element with this class (grep confirms it appears only in the CSS). Harmless, but it is dead code that misleads future edits — the same class of issue the Phase 1 review flagged (WR-07).

**Fix:** delete the rule (and its `/* Public coming-soon */` comment) during Phase 4 cleanup.

### WR-05: Public 404/500 pages render without the public header/search (inconsistent public UX)

**File:** `app/templates/errors/404.html:1`, `app/templates/errors/500.html:1` + `app/__init__.py:74-81`

**Issue:** Both error templates `{% extends "base.html" %}` directly, so the `{% block header %}` inserted by Phase 3 is empty — a customer landing on a stale product link (e.g. `/products/999999`) gets a bare 404 page with no site brand, no search box, and no nav; the only escape is the inline "Quay lại trang chủ" link. Before Phase 3 this was consistent (no public header existed); now the error pages are the only public-reachable pages without the header. Verified: 404 HTML contains no `.site-header` / `.search-form`.

**Fix:** have the error templates extend the public chain when the error is on a public route, e.g. `{% extends "public/base.html" %}` when the request is not under `/admin/` or `/auth/`, or extract the public header into a partial both `public/base.html` and the error pages include.

### WR-06: `_manual_pagination` `prev_num`/`next_num` boundary branches are dead code and diverge from the SQLAlchemy `Pagination` contract

**File:** `app/public.py:27-28`

**Issue:** `prev_num = page - 1 if page > 1 else 1` and `next_num = page + 1 if page < pages else pages` — because `page` is clamped to `[1, pages]`, the `else 1` / `else pages` branches are only hit exactly at the boundary where `has_prev`/`has_next` are `False`, so `search.html`'s `{% if pagination.has_prev %}` guard never renders those values. Flask-SQLAlchemy's `Pagination` returns `None` at the boundaries (pagination.py:208-213, 238-243); this helper returns `1`/`pages` instead. Harmless today, but a future caller that reads `prev_num` without checking `has_prev` (or swaps this for the real `Pagination` object) would get a wrong page number.

**Fix:** mirror the SQLAlchemy contract:

```python
prev_num = page - 1 if page > 1 else None,
next_num = page + 1 if page < pages else None,
```

---

## Explicit "No Findings" Confirmation

- **Blocker / critical:** none found.
- **Security:** no XSS (zero `|safe`; every `{{ q }}`, product name/description/brand/measurements, and attribute-context `value="{{ request.args.get('q') }}"` auto-escaped — verified with a `<script>` payload); no SQL/command/path injection (in-Python search filter, UUID image filenames only); no auth leak (`admin_note` absent from all public templates); `normalize_search_text` is ReDoS-safe (linear `unicodedata`, no regex); public routes are read-only GET with no CSRF surface.
- **Search correctness:** `pagination.total` reflects the FILTERED match set (search) and the full product set (home); `page` non-int never 500; `page=0`/negative coerced to 1; out-of-range search pages clamp to the last page; q is preserved and HTML-escaped in pagination links; `đ`/`Đ` is correctly not folded to `d` (distinct Vietnamese letter; matches the D-11 contract — documented in 03-VERIFICATION.md).
- **Detail page:** 404 on missing product renders via the global handler; gallery main image = `primary_image` (first by `sort_order`) consistent with `images` ordering; out-of-stock shows the red note + CTA (D-07); `MESSENGER_URL` always present in config (default documented in `.env.example`).
- **Consistency with Phase 2:** home ordering (`sort_order` asc, `id` asc, 12/page) matches `admin.products` (20/page); grid/detail status rendering matches the admin badge classes (`.badge-available/-out_of_stock/-discontinued`).

---

_Reviewed: 2026-08-01T15:10:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
