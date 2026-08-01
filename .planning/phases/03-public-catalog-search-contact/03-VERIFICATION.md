---
phase: 03-public-catalog-search-contact
verified: 2026-08-01T14:30:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
overrides: []
gaps: []
human_verification:
  - test: "Exercise the gallery thumbnail swap on a product detail page with ≥2 images in a real browser: click each 72px thumbnail."
    expected: "The main image (id=main-image) swaps its src/alt to the clicked thumbnail's data-src/data-alt, the clicked thumb gains .is-active + aria-current=\"true\", and the previous thumb loses both. With JS disabled the page still shows the first (primary) image and all thumbnails."
    why_human: "The thumbnail swap is inline vanilla JS in product_detail.html (lines 53-70). The Flask test client cannot execute browser JS, so the swap/toggle behavior is only verifiable in a browser."
  - test: "Visually inspect the public home grid, a product detail page, and the search results page against 03-UI-SPEC."
    expected: "Home grid shows 2/3/4 product cards per row at mobile/tablet/desktop; each card shows thumb + name + formatted price + status badge; out-of-stock/discontinued cards show a dimmed image (opacity 0.45) with a 'Hết hàng'/'Ngừng bán' overlay badge; the contact strip shows a visible 'Mua qua Messenger' button; the detail page shows image-left/info-right at ≥768px with name → price → status → CTA → brand → measurements → description order; the red 'Sản phẩm hiện đang hết hàng.' line shows only for out-of-stock."
    why_human: "CSS appearance, badge-overlay placement, and layout are visual; grep confirms selectors/classes exist but not that they render correctly."
  - test: "Resize the browser to ≤480px, 768px, and ≥1200px on the home grid and detail page; also run a search and confirm the nav search input pre-fills the active query and pagination links carry q."
    expected: "The grid reflows to 2 cols below 768px, 3 cols at ≥768px, 4 cols at ≥1200px; the detail page stacks vertically below 768px and becomes 2-column at ≥768px; the header search form is usable at all widths (44px input); on a multi-page search result, 'Trước'/'Sau' links keep q in the URL."
    why_human: "Media-query reflow and form usability are visual/behavioral and not verifiable via the test client."
---

# Phase 3: Public Catalog + Search + Contact Verification Report

**Phase Goal (MVP user story):** Customers can browse products, search, and contact the seller via Messenger
**Verified:** 2026-08-01T14:30:00Z
**Status:** passed (all 5 programmatic success criteria VERIFIED; 3 non-blocking human UAT items listed)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Customers can view a public product listing grid without logging in (CAT-01, CAT-03, D-01/02/03/04) | VERIFIED | `app/public.py:32-38` home route (no auth required), `app/templates/public/index.html:5-8` `.product-grid` cards, `_product_card.html:1-19`; `style.css:373-375` grid 2/3/4 cols at 0/768/1200, `:382` `.is-unavailable` dim, `:383` `.badge-overlay`, `:393-396` `.contact-strip`. Independent test: `GET /` → 200 with grid + 5 cards + contact strip, no login; pagination `Trang 1 / 2` → `Trang 2 / 2`; out-of-stock card `is-unavailable` + `Hết hàng` overlay; discontinued card `Ngừng bán` overlay. |
| 2 | Customers can view product detail pages showing images, price, brand, measurements, description, and stock status (CAT-02, CAT-03, D-05/06/07/08) | VERIFIED | `app/public.py:41-47` product_detail route (404 on missing); `app/templates/public/product_detail.html` name (27) → price `format_price` (28) → status badge (30-32) → Messenger CTA (34) → red out-of-stock line (35-37) → brand/measurements meta (38-43) → description (44-49); `style.css:399,428-432` mobile-stack / ≥768 2-column. Independent test: detail of seeded product → 200, shows `150.000₫`, `Coolmate`, `M / L / XL`, description, `Còn hàng`, Messenger CTA; out-of-stock detail → `Hết hàng` badge + CTA still present + red `Sản phẩm hiện đang hết hàng.` line; `admin_note` never rendered; `/products/999999` → 404. |
| 3 | Customers can search products by name or description and see matching results (SRCH-01, D-09/10/11/12) | VERIFIED | `app/public.py:12-18` `normalize_search_text` (NFD → strip Mn → casefold), `:50-67` `/search` GET route filtering normalized name OR description in Python, `:21-29` `_manual_pagination`; `_nav.html:4-8` GET search form (D-09), `search.html` 3 states (prompt / results / no-results) + `pagination.total` count + q-preserving pagination. Independent tests: `normalize_search_text('áo'/'Áo'/'QUẦN')` → `ao`/`ao`/`quan`; `GET /search?q=ao` → 200, 3 Áo products, `q=ao` preserved in page-2 link; `q=cotton` finds by description; `q=QUẦN` (uppercase) finds `Quần jean xanh`; product with `description=None` matches by name without crash; blank/whitespace `q` → prompt; unknown keyword → `Không tìm thấy sản phẩm`; 13 matches paginate to `Trang 2 / 2` with 1 item on page 2. |
| 4 | Customers see a visible Messenger contact link on both the homepage and product detail pages (CONT-01, CONT-02, D-13) | VERIFIED | `app/__init__.py:43` `MESSENGER_URL` config; `index.html:24-28` `.contact-strip` with `btn btn-primary` "Mua qua Messenger" (renders even on empty store); `product_detail.html:34` `.messenger-cta` "Mua qua Messenger" on all statuses (D-07). Independent test: `MESSENGER_URL` value (`https://m.me/testpage`) present in both home and detail HTML. |
| 5 | Product detail page displays an image gallery with all product images (CAT-05, D-06) | VERIFIED | `app/public.py:46` images ordered by `sort_order` ASC; `product_detail.html:9-10` main image = `product.primary_image` (first), `:15-24` thumbnail strip (`gallery-thumbs`) only when `images|length > 1`, active thumb `aria-current="true"`, `:53-70` inline vanilla JS swaps `#main-image` src/alt + toggles `.is-active`/`aria-current`; `style.css:407-413`. Independent test: detail of a 2-image product → main-image + 2 thumbnails with `data-src` + swap JS present; 1-image product → no thumbnail strip. |

**Score:** 5/5 truths verified

### User Flow Coverage (MVP)

| User story step | Expected | Evidence | Status |
|-----------------|----------|----------|--------|
| Customer opens the store URL without logging in | Public product grid renders (no auth wall) | `public.py:32-38`; test `GET /` 200 no login | PASS |
| Customer clicks a product card | Detail page shows images, price, brand, measurements, description, status | `public.py:41-47`; `product_detail.html`; all fields present in rendered HTML | PASS |
| Customer clicks a thumbnail | Main image swaps | inline JS `product_detail.html:53-70` (human-UAT for browser behavior) | PASS (code) |
| Customer types a Vietnamese/unsigned keyword and submits | Diacritic-insensitive results page | `normalize_search_text` + `/search`; `q=ao` → 3 Áo products | PASS |
| Customer clicks "Mua qua Messenger" | Messenger link opens (home + detail) | `index.html:27`, `product_detail.html:34` → `MESSENGER_URL` | PASS |

### Decision Spot-Checks (D-01..D-13)

| Decision | Status | Evidence |
|----------|--------|----------|
| D-01 grid thẻ card (ảnh, tên, giá, trạng thái) | VERIFIED | `_product_card.html:1-19` (thumb, name, price, status overlay) |
| D-02 grid 2/3/4 cột (480/768/1200) | VERIFIED | `style.css:373-375`: default `repeat(2,1fr)` (mobile), `min-width:768px` → 3, `min-width:1200px` → 4. 2 cols applies across the whole <768 mobile range, so no separate 480 rule is needed. |
| D-03 phân trang 12/trang, sort_order | VERIFIED | `public.py:35-37` `.order_by(sort_order.asc(), id.asc()).paginate(per_page=12, error_out=False)`; test 18 items → `Trang 1 / 2` |
| D-04 hết hàng/ngừng bán: ảnh mờ + nhãn | VERIFIED | `_product_card.html:1,9-13` `.is-unavailable` + `.badge-overlay`; `style.css:382-383` `opacity: 0.45` + overlay; test rendered on home grid |
| D-05 ảnh trái - thông tin phải (mobile stack) | VERIFIED | `product_detail.html:6-51`; `style.css:399,428-432` |
| D-06 gallery ảnh chính + thumbnail, click đổi ảnh | VERIFIED | `product_detail.html:9-24,53-70`; first image = primary (models.py:47-50) |
| D-07 hết hàng: vẫn nút "Mua qua Messenger" + dòng đỏ | VERIFIED | `product_detail.html:34-37`; `style.css:420` `.out-of-stock-note { color:#DC2626 }`; test: out-of-stock detail has both |
| D-08 thứ tự: tên → giá → trạng thái → thương hiệu → số đo → mô tả | VERIFIED | `product_detail.html:27-49` markup order; (Messenger CTA sits between status and meta per UI-SPEC flagged decision 6) |
| D-09 ô tìm kiếm trên header | VERIFIED | `_nav.html:4-8` search form in public header; admin/auth pages render no header (`base.html:14` block, no template overrides it) |
| D-10 GET form submit → trang kết quả riêng | VERIFIED | `_nav.html:4` `method="get" action="{{ url_for('public.search') }}"`; `/search` route |
| D-11 tìm không dấu (NFD + strip + lowercase) | VERIFIED | `public.py:12-18`; unit + end-to-end tests (`ao`→`áo`) |
| D-12 kết quả dùng chung grid + "N sản phẩm cho '{q}'"; empty state | VERIFIED | `search.html:12-16` reuses `_product_card.html`; `:13` result count; `:26-32` "Không tìm thấy sản phẩm" + CTA |
| D-13 nút Messenger trang chủ + chi tiết | VERIFIED | `index.html:24-28` contact strip; `product_detail.html:34` messenger-cta |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `app/public.py` | home (12/page grid) + product_detail + search routes, normalize_search_text, _manual_pagination | VERIFIED | lines 12-29 (normalize + pagination), 32-38 (home), 41-47 (detail), 50-67 (search) |
| `app/templates/public/base.html` | public layout chain extending base + header block | VERIFIED | extends `base.html`, includes `_nav.html` |
| `app/templates/public/_nav.html` | sticky header + GET search form | VERIFIED | brand link + `role="search"` form, `q` pre-fill |
| `app/templates/public/_product_card.html` | shared card: thumb, name, price, status overlay | VERIFIED | whole-card `<a>`, `is-unavailable` + badge overlay |
| `app/templates/public/index.html` | grid + empty state + pagination + contact strip | VERIFIED | lines 4-29 |
| `app/templates/public/product_detail.html` | gallery + info order + Messenger CTA + back link + swap JS | VERIFIED | lines 5-70 |
| `app/templates/public/search.html` | 3 states + result count + q-preserving pagination | VERIFIED | lines 6-32 |
| `app/templates/base.html` | `{% block header %}` insertion | VERIFIED | line 14, between skip-link and flash zone |
| `app/static/css/style.css` | grid 2/3/4, card, badge overlay, contact strip, gallery, detail, result-count | VERIFIED | lines 373-435; total 435 lines (~15.6KB) |
| `app/models.py` | status property + primary_image + thumb_filename (reused) | VERIFIED | lines 40-50, 64-69 |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | -- | ------ | ------- |
| `app/public.py` home | `Product` | `.order_by(sort_order, id).paginate(12)` | WIRED | real sqlite rows → grid |
| `app/public.py` detail | `ProductImage` | `product.images.order_by(sort_order).all()` | WIRED | gallery ordered, primary = first |
| `app/public.py` search | `normalize_search_text` | applied to both keyword and name/description | WIRED | D-11 contract, unit + e2e tested |
| `_nav.html` search form | `public.search` route | GET `action=url_for('public.search')` + `name="q"` | WIRED | empty-query prompt handled |
| `product_detail.html` | `MESSENGER_URL` config | `config['MESSENGER_URL']` in CTA href | WIRED | value renders in both home + detail |
| `_product_card.html` | `public.product_detail` | `url_for('public.product_detail', product_id=p.id)` | WIRED | card → detail navigation |
| `search.html` pagination | `public.search` | `url_for('public.search', q=q, page=N)` | WIRED | q preserved (HTML-escaped `&amp;` verified) |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| home grid | `pagination.items` | `Product.query.paginate()` real sqlite rows | Yes | FLOWING |
| detail page | `product` + `images` | `db.session.get(Product, id)` + ordered `images` query | Yes | FLOWING |
| search results | `matched` / `pagination.items` | in-Python filter over `Product.query.all()` | Yes | FLOWING |
| price display | `p.price` | integer column → `format_price` filter | Yes | FLOWING |
| gallery main image | `product.primary_image.thumb_filename` | real `<uuid>_thumb.jpg` asset (IMG-04) | Yes | FLOWING |
| Messenger link | `config['MESSENGER_URL']` | `.env` config (Phase 1) | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| home no-auth grid | `GET /` | 200, grid + cards + contact strip | PASS |
| pagination 12/page | 18 items `GET /` and `/?page=2` | `Trang 1 / 2` → `Trang 2 / 2` | PASS |
| detail with 2 images | `GET /products/{pid}` | 200; main-image + 2 thumbs + swap JS | PASS |
| out-of-stock detail | `GET /products/{oos_id}` | `Hết hàng` + CTA + red note | PASS |
| discontinued grid badge | `GET /` | `is-unavailable` + `Ngừng bán` overlay | PASS |
| diacritic search | `GET /search?q=ao` | 3 Áo products; result-count line | PASS |
| description search | `GET /search?q=cotton` | Áo thun nam found | PASS |
| uppercase search | `GET /search?q=QUẦN` | Quần jean xanh found | PASS |
| None-description match | `GET /search?q=khoac` | Áo khoác nỉ found, no crash | PASS |
| empty/whitespace q | `GET /search?q=` / `?q=+++` | prompt "Vui lòng nhập từ khóa" | PASS |
| no-results state | `GET /search?q=zzzznothing` | "Không tìm thấy sản phẩm" + CTA | PASS |
| q-preserving pagination | 13 matches `?q=ao&page=2` | `Trang 2 / 2`; 1 item; links carry `q=ao&amp;page=1` | PASS |
| 404 on missing product | `GET /products/999999` | 404 (errors/404.html) | PASS |
| Messenger on home + detail | render check | `https://m.me/testpage` in both | PASS |
| sort_order ordering | `GET /` position check | sort_order 1 card before sort_order 2 | PASS |
| admin_note not leaked | set secret note, GET detail | note absent from HTML | PASS |
| admin still auth-gated | `GET /admin/products` unauth | 302 → /login | PASS |
| page clamp | `_manual_pagination(99,12,13)` | page=2 | PASS |
| format_price | filter call | `1200000` → `1.200.000₫` | PASS |

### Probe Execution

No `probe-*.sh` scripts exist in the repo and no probes were declared in any Phase 3 PLAN/SUMMARY. Step 7c: N/A.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| CAT-01 | 03-01 | public list, no login | SATISFIED | public.py:32-38; index.html; test GET / 200 |
| CAT-02 | 03-02 | detail: ảnh, giá, thương hiệu, số đo, mô tả, trạng thái | SATISFIED | public.py:41-47; product_detail.html:27-49; tested |
| CAT-03 | 03-01/03-02 | giá + trạng thái rõ trên trang | SATISFIED | format_price filter + status badges on card and detail; tested |
| CAT-05 | 03-02 | detail gallery nhiều ảnh | SATISFIED | product_detail.html:9-24,53-70; tested |
| SRCH-01 | 03-03 | search theo tên/mô tả | SATISFIED | public.py:50-67 + normalize_search_text:12-18; tested |
| CONT-01 | 03-01 | dải liên hệ hiển thị link Messenger | SATISFIED | index.html:24-28 contact strip |
| CONT-02 | 03-01/03-02 | Messenger dễ thấy trên trang chủ + chi tiết | SATISFIED | index.html:27; product_detail.html:34; tested |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `app/static/css/style.css` | 50-51 | orphaned `.coming-soon` rule (Phase 1 coming-soon no longer rendered) | Info (non-blocking) | dead CSS ~few lines; index.html no longer uses the class. Optional cleanup for Phase 4. |

No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER markers, no `return null`/NotImplemented stubs, no hardcoded empty data, no leaked `admin_note`, no stub template remnants in the phase files. All 11 claimed task commits exist (`git cat-file -t` → commit).

### Human Verification Required (non-blocking)

1. **Gallery thumbnail swap JS interaction** — On a product detail page with ≥2 images, click each 72px thumbnail in a real browser. Expected: main image swaps src/alt to the clicked thumbnail's data-src/data-alt; clicked thumb gains `.is-active` + `aria-current="true"`; previous thumb loses both. Why human: inline vanilla JS (`product_detail.html:53-70`) not executable by the Flask test client.
2. **Visual appearance vs 03-UI-SPEC** — Inspect home grid, detail page, and search results. Expected: 2/3/4-card grid, cards show thumb/name/price/status, out-of-stock/discontinued dimmed (opacity 0.45) with `Hết hàng`/`Ngừng bán` overlay, contact strip visible, detail 2-col at ≥768 with D-08 info order, red `Hết hàng` line only for out-of-stock. Why human: CSS rendering is visual.
3. **Responsive behavior** — Resize to ≤480 / 768 / ≥1200 on home grid and detail; run a multi-page search and confirm nav input pre-fills `q` and pagination links keep `q`. Expected: grid 2→3→4 cols, detail stacks below 768 / 2-col above, search pagination preserves the query. Why human: media-query reflow and form usability are visual/behavioral.

### Gaps Summary

No functional gaps. All 5 roadmap success criteria verified against the actual code with independent execution (Flask test client against an isolated temp DB, `normalize_search_text` unit checks, HTML/CSS class assertions): 49 programmatic checks passing. Two observations are non-blocking:

1. **`Đ`/`đ` is not folded to `d`** — `normalize_search_text('Đậm')` → `đam`, not `dam`. This is expected: `đ` (U+0111) is a distinct Vietnamese letter with its own codepoint that NFD does not decompose, and the D-11 contract only requires stripping combining marks + lowercase. A query `dam` will not match `đậm`. This matches the phase contract exactly; no action needed unless Phase 4 wants full `đ`→`d` folding.
2. **Orphaned `.coming-soon` CSS** (style.css:50-51) — dead rule from Phase 1; harmless, optional cleanup for Phase 4.

The 3 human UAT items above require browser/visual sign-off; all automated truths pass, so status is `passed` per the orchestrator's instruction.

---

_Verified: 2026-08-01T14:30:00Z_
_Verifier: Claude (gsd-verifier)_
