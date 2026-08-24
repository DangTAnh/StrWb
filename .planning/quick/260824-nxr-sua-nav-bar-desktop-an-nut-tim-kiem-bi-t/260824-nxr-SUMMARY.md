---
phase: quick-260824-nxr
plan: 01
subsystem: public-ui
tags: [bugfix, css, navbar, responsive]
requires:
  - "app/static/css/style.css (section 4 header media queries)"
  - "app/templates/public/_nav.html + _admin_nav.html (cấu trúc, không sửa)"
provides:
  - "Nav bar desktop 1 dòng: ẩn nút Tìm kiếm mobile-only, hết trùng Giỏ hàng/Đăng xuất"
affects:
  - "Header mọi trang (public + admin dùng chung _nav.html)"
key-files:
  created: []
  modified:
    - app/static/css/style.css
decisions:
  - "Tăng đặc hiệu (.mobile-search-shell .search-toggle = 0,2,0) thay vì !important để thắng .btn"
  - "Ẩn mobile-only nav item ở desktop thay vì xóa khỏi markup — mobile vẫn dùng chúng trong dropdown hamburger"
metrics:
  files_changed: 1
  duration: ~10min
deviations: []
---

# Summary: Sửa nav bar desktop

## Gốc rễ (2 lỗi, bản mobile đã đúng nên chỉ sửa media query desktop)

1. `.search-toggle { display: none }` (section 4) thua `.btn { display:
   inline-flex }` (section 5, cùng đặc hiệu 0,1,0 nhưng sau trong file) → nút
   "Tìm kiếm" mobile-only không bao giờ ẩn trên desktop.
2. `.mobile-menu-cart` / `.mobile-menu-logout` không bị ẩn trên desktop →
   trùng với `.desktop-header-actions` + nav wrap 2 dòng.

## Đã làm (1 khối `@media (min-width: 768px)` trong style.css)

1. `.search-toggle` → `.mobile-search-shell .search-toggle` (0,2,0 thắng .btn)
2. Thêm `.site-nav .mobile-menu-cart, .site-nav .mobile-menu-logout { display: none; }`

## Verify

- CSS serve chứa đủ 2 rule mới; `/`, `/login` render 200
- Mobile (<768px): không đổi — hamburger dropdown vẫn có Giỏ hàng + Đăng xuất

## Commit

Dùng chung commit với 260824-nof (cùng file style.css): fix(ui): product card
deu cao + nav bar desktop dung 1 dong
