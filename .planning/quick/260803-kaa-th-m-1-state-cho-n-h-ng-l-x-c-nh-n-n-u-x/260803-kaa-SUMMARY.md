---
quick_id: 260803-kaa
phase: quick
plan: 260803-kaa
status: complete
tasks_total: 2
tasks_completed: 2
commits:
  - 9730dd1
  - 613740e
completed_date: "2026-08-03"
---

# Quick Task 260803-kaa Summary

## Thêm state "Đã xác nhận" + trừ tồn kho khi xác nhận

**Thay đổi luồng đơn hàng:** `Chờ xác nhận → {Đã xác nhận, Đã hủy}`; `Đã xác nhận → {Đã gói, Đã hủy}` (thay `Chờ xác nhận → Đã gói` trực tiếp). Admin phải xác nhận trước khi gói — không nhảy cóc.

**Trừ tồn kho:** Khi chuyển `Chờ xác nhận → Đã xác nhận`, trừ `OrderItem.quantity` của từng sản phẩm (sàn 0), bỏ qua item có `product_id` NULL (sản phẩm đã xóa). Idempotent nhờ forward-only map — POST lặp bị từ chối, không trừ kép. Atomic: cùng 1 `db.session.commit()`. Không hoàn lại tồn kho khi hủy sau khi đã xác nhận (nằm ngoài phạm vi yêu cầu, đánh dấu `ponytail:` trong code).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Backend: state + stock decrement | 9730dd1 | `app/admin.py`, `.planning/tmp/verify_quick_kaa.py` |
| 2 | UI: stepper + buttons + badge + stats | 613740e | `app/templates/admin/orders/detail.html`, `app/templates/admin/stats.html`, `app/static/css/style.css`, `.planning/tmp/verify_quick_kaa.py` |

## Files Created/Modified

- **app/admin.py** — `ORDER_STATUSES` (+`Đã xác nhận`), `TRANSITION_MAP` (rebuild cạnh edge), `order_badge_class` (+`badge-order-confirmed`), `update_order_status` (+stock decrement block trước commit)
- **app/templates/admin/orders/detail.html** — stepper 5 bước, `flow` list cập nhật, nhánh `Chờ xác nhận` chuyển nút sang `Đã xác nhận`, thêm nhánh `Đã xác nhận → Đã gói`
- **app/templates/admin/stats.html** — thêm dòng `Đã xác nhận` trong status breakdown
- **app/static/css/style.css** — `.badge-order-confirmed` (purple/ivory, WCAG AA)
- **.planning/tmp/verify_quick_kaa.py** — verify script (temp DB, never touches `data/app.db`)

## Verification

`python .planning/tmp/verify_quick_kaa.py` → **TASK_OK** (all 20 checks pass):
- ORDER_STATUSES 6 states, `Đã xác nhận` ở vị trí 2
- TRANSITION_MAP: `Chờ xác nhận → {Đã xác nhận, Đã hủy}`, `Đã xác nhận → {Đã gói, Đã hủy}`, `Đã gói` NOT in `Chờ xác nhận`
- `order_badge_class('Đã xác nhận') == 'badge-order-confirmed'`
- POST `Đã gói` từ `Chờ xác nhận` bị reject (status + stock không đổi)
- POST `Đã xác nhận`: stock 5 → 2 (trừ 3, bỏ qua item deleted qty=2)
- POST lặp `Đã xác nhận` bị reject (stock vẫn 2, không trừ kép)
- UI: detail stepper 5 bước + `badge-order-confirmed` + "Chuyển sang: Đã gói"; filter dropdown có `Đã xác nhận`; stats breakdown có `Đã xác nhận`

## Deviations

None — plan executed exactly as written. All scope changes were within plan spec.

## Notes

- **No new dependencies**; **no DB schema migration** (`orders.status` là free-string, default không đổi).
- `data/app.db` thật không bị đụng — verify dùng temp DB theo pattern `verify_0701.py`.
- `app/templates/admin/orders/list.html` không sửa — filter dropdown tự động có `Đã xác nhận` từ `ORDER_STATUSES`.

## Self-Check

- [x] Created files exist: `app/admin.py`, `detail.html`, `stats.html`, `style.css`, `verify_quick_kaa.py`
- [x] Commits exist: 9730dd1, 613740e
- [x] Verification passes: TASK_OK (20/20 checks)
- [x] data/app.db untouched
- [x] No new dependencies
