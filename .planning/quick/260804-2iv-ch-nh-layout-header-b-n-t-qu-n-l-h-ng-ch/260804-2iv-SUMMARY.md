---
phase: quick-260804-2iv
plan: 1
type: execute
status: complete
---

# Quick 260804-2iv: Header layout refine — drop brand, nav left of search — Summary

## What was done

Refined the header layout so the section nav sits left of the search bar, the "Quản lý hàng" brand link is removed (the **Trang chủ** link in the nav already covers home), and all header elements (nav, search, cart) align on one baseline.

- `app/templates/public/_nav.html`: removed the `<a class="brand">` link; moved `{% include "_admin_nav.html" %}` to the **left** of `<form class="search-form">` so the Trang chủ/Sản phẩm/Đơn hàng/Thống kê links render left of the search input. Existing search form + cart link preserved.
- `app/templates/admin/base.html`: removed the brand link (nav partial is now the only header child).
- `app/static/css/style.css`: `.site-nav` now has `align-items: center; flex-shrink: 0;` and `.logout-form` is `inline-flex; align-items: stretch; flex-shrink: 0` so nav/search/cart share a single vertical alignment.

## Verification
- Route registration: `routes-ok` — `/products`, `/orders`, `/stats` present; no `/admin*` rules.
- `/products`, `/orders`, `/stats` all 302 → `/login` (auth gate intact).
- `/login` → 200; login page extends `base.html` (no admin nav header).
- Jinja render smoke test: `_admin_nav.html` + `admin/base.html` render without errors.

## Manual Verify (Pending)
Not run interactively — layout is CSS+template only. Open `/` and `/products` in a browser: confirm nav links (Trang chủ/Sản phẩm/Đơn hàng/Thống kê) appear to the left of the search bar on the same row as the cart link and are vertically aligned. Confirm "Quản lý hàng" brand link is gone from both the home and admin headers.

## Commit
`bd3bd0d` — ui(quick-260804-2iv): header layout — drop brand, nav left of search, height balance

## Deviations
None.
