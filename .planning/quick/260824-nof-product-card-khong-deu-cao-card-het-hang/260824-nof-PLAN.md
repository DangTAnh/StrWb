---
phase: quick-260824-nof
plan: 01
subsystem: public-ui
tags: [bugfix, css, product-card]
---

# Quick Task 260824-nof: Product card không đều cao

## Vấn đề

Trên một hàng `.product-grid`, wrapper bị grid kéo giãn đều nhưng
`.product-card` bên trong không → card hết hàng (thiếu dòng "Còn: N") thấp
hơn card còn hàng; nút Sửa (`position: absolute; bottom` của wrapper) rớt
xuống dưới mép card.

## Task 1: Card cao đều + nút Sửa bám mép card

**Files:** `app/static/css/style.css`, `app/templates/public/_product_card.html`

**Action:**
1. `.product-card`: thêm `display: flex; flex-direction: column; height: 100%;`
2. `.product-card-body`: thêm `flex: 1;`
3. `.product-card-stock`: thêm `min-height: 1.55em;` (cao 1 dòng text-xs)
4. Template: luôn render `<p class="product-card-stock">` (rỗng khi hết hàng)
   → giá thẳng hàng giữa các card.

**Verify:** render `/` qua test_client — số `.product-card-stock` bằng số
sản phẩm; CSS có flex rules.

**Done:** Card trong cùng hàng bằng cao, nút Sửa nằm trên mép card.
