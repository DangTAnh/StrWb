---
phase: quick-260824-nxr
plan: 01
subsystem: public-ui
tags: [bugfix, css, navbar, responsive]
---

# Quick Task 260824-nxr: Sửa nav bar desktop (mobile đã đúng)

## Vấn đề (bản desktop ≥768px)

1. Nút "Tìm kiếm" (chỉ dành cho mobile) vẫn hiện: media query đặt
   `.search-toggle { display: none }` ở section 4, nhưng chính nút mang class
   `.btn` với `display: inline-flex` ở section 5 (sau trong file) → cùng đặc
   hiệu (0,1,0), `.btn` thắng → không bao giờ ẩn.
2. `.mobile-menu-cart` / `.mobile-menu-logout` trong `.site-nav` không bị ẩn
   trên desktop → trùng lặp với `.desktop-header-actions` (Giỏ hàng + Đăng
   xuất x2), và làm nav wrap thành 2 dòng.

Bản mobile: cấu trúc hamburger + search toggle đã đúng, không đụng.

## Task 1: Sửa khối media query desktop trong style.css

**Files:** `app/static/css/style.css` (section 4, khối `@media (min-width: 768px)`)

**Action:**
1. `.search-toggle` → `.mobile-search-shell .search-toggle` (đặc hiệu 0,2,0
   thắng `.btn` 0,1,0).
2. Thêm: `.site-nav .mobile-menu-cart, .site-nav .mobile-menu-logout { display: none; }`

**Verify:** grep CSS chứa 2 rule mới; render `/login` + `/` 200.

**Done:** Desktop: 1 dòng nav (5 link), 1 nút Tìm kiếm ẩn, Giỏ hàng + Đăng
xuất chỉ ở cụm phải. Mobile: không đổi.
