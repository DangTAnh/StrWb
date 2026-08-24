---
phase: quick-260824-nof
plan: 01
subsystem: public-ui
tags: [bugfix, css, product-card]
requires:
  - "app/static/css/style.css (section 13 product card)"
  - "app/templates/public/_product_card.html"
provides:
  - "Card sản phẩm cao đều trong cùng hàng grid, giá thẳng hàng, nút Sửa bám mép card"
affects:
  - "Trang chủ + tìm kiếm (mọi nơi dùng _product_card.html)"
key-files:
  created: []
  modified:
    - app/static/css/style.css
    - app/templates/public/_product_card.html
decisions:
  - "Flex column + height:100% thay vì cố định height — card bằng cao theo hàng grid"
  - "Luôn render dòng stock (rỗng khi hết hàng) + min-height 1.55em — giá thẳng hàng giữa các card"
metrics:
  files_changed: 2
  duration: ~10min
deviations: []
---

# Summary: Product card không đều cao

## Gốc rễ

Grid kéo giãn `.product-card-wrapper` đều nhưng `.product-card` bên trong
không tự giãn → card hết hàng (thiếu dòng "Còn: N") thấp hơn; nút Sửa
(`position: absolute; bottom` của wrapper) rớt dưới mép card.

## Đã làm

1. `.product-card`: `display: flex; flex-direction: column; height: 100%`
2. `.product-card-body`: `flex: 1`
3. `.product-card-stock`: `min-height: 1.55em` + template luôn render `<p>`
   (rỗng khi hết hàng)

## Verify (test_client, session admin #1)

- `/` → 200: 12 card div = 12 dòng `product-card-stock` (8 hết hàng trước
  đây thiếu dòng, giờ đủ)
- CSS serve chứa đủ rule mới

## Commit

Dùng chung commit với 260824-nxr (cùng file style.css): fix(ui): product card
deu cao + nav bar desktop dung 1 dong
