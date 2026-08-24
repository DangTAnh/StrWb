---
phase: quick-260824-n6i
plan: 01
subsystem: admin-orders-ui
tags: [bugfix, ajax, orders]
requires:
  - "app/templates/admin/orders/list.html (filter AJAX + wrapper bảng)"
  - "app/templates/admin/orders/_content.html (AJAX partial)"
provides:
  - "Filter trạng thái đơn hàng hoạt động lại (AJAX inject đúng chỗ, đúng style)"
affects:
  - "Trang /orders (admin)"
key-files:
  created: []
  modified:
    - app/templates/admin/orders/list.html
    - app/templates/admin/orders/_content.html
decisions:
  - "Nhắm target bằng id (#orders-table-card) thay vì class — chính xác, không phụ thuộc thứ tự DOM"
  - "Partial _content.html trả nội dung trong card (không wrapper) — tránh card lồng card khi gán vào innerHTML"
metrics:
  files_changed: 2
  duration: ~10min
deviations: []
---

# Summary: Fix bug lọc đơn hàng AJAX

## Vấn đề gốc

`loadFilteredOrders()` query `.admin-card` nhưng wrapper chỉ có modifier
`admin-card--wide` → `querySelector` trả `null` → filter chết im lặng. Cùng
gốc rễ: cả list.html lẫn _content.html thiếu base class `admin-card`
(modifier không base = mất style card).

## Đã làm

1. `list.html:43`: `<div class="admin-card admin-card--wide" id="orders-table-card">`
2. `_content.html`: bỏ wrapper card khỏi partial + dedent → chỉ trả
   table/pagination hoặc empty-state
3. `list.html:151`: `document.getElementById('orders-table-card')`

## Verify (test_client, LOGIN_DISABLED)

- Full page `/orders` → 200, có id + base class
- AJAX `/orders?ajax=1&status=Đã gửi` → 200, không còn wrapper card trong
  partial, có `data-table`
- AJAX status hợp lệ nhưng trống DB → 200, render `empty-state`, không wrapper

Script pay/status dùng event delegation trên `document` nên việc thay
innerHTML không mất handler.

## Commit

- fix(ui): loc don hang AJAX hoat dong lai — selector khop wrapper card
