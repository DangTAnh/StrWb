---
phase: quick-260824-v9m
plan: 01
subsystem: admin-export
tags: [bugfix, xlsx, export, viettel-post]
requires: [EXPORT-01 route export_orders_xlsx]
provides: [xlsx file mo duoc bang Excel, header 30 cot Viettel Post, build_orders_xlsx(orders) -> bytes]
affects: [app/admin.py::export_orders_xlsx (khong doi signature)]
key-files:
  created: []
  modified: [app/xlsx_export.py]
decisions:
  - "Bo han part xl/theme/theme1.xml thay vi sua day du fontScheme/fmtScheme — theme la optional part"
  - "Kieu cell khai bao tuong minh per-cot (NUMBER_COLS = {0,10,11,12,17,24}) thay vi heuristic float()"
  - "Khong them openpyxl — giu stdlib zipfile theo ghi chu plan"
metrics:
  duration: "~5 phut"
  completed: 2026-08-24
---

# Quick Task 260824-v9m: Sửa xlsx export — file Excel xuất ra bị lỗi — Summary

**One-liner:** Viết lại `build_orders_xlsx`: bỏ part theme hỏng khiến Excel từ chối mở, đúng 30 header template Viettel Post, kiểu cell tường minh giữ số 0 SĐT, mapping Y/N + COD + "Người gửi trả" đúng nghĩa.

## What Was Done

### Task 1 — Viết lại `build_orders_xlsx`

- **Bỏ lỗi chính:** xóa `theme_xml` + `zf.writestr("xl/theme/theme1.xml", ...)`; `xl/_rels/workbook.xml.rels` chỉ còn worksheet (`rId1`) + styles (`rId2`); `[Content_Types].xml` bỏ Override theme. Theme thiếu `<a:fontScheme>`/`<a:fmtScheme>` vi phạm schema → Excel báo "found a problem with some content"; theme là optional part nên bỏ hẳn là fix gốc.
- **Header:** thay list `"*"` bị che bằng đúng **30 tên đầy đủ A..AD** theo template gốc `collect_fee_mass_order_creation_template_vn_2level_addr.xlsx` (sheet name đổi `"Đơn hàng"` → `"Tạo đơn (địa chỉ mới)"` trong workbook.xml).
- **Kiểu cell:** bỏ heuristic `try: float()`; thêm `NUMBER_COLS = {0, 10, 11, 12, 17, 24}` (mã đơn, số lượng, giá tiền, cân nặng, giá trị đơn, tiền COD). Cột còn lại ghi `t="inlineStr"` — SĐT `"0909999999"` giữ nguyên số 0 đầu.
- **Mapping sửa nghĩa:**
  - Cột A mã đơn lặp trên **mọi dòng item** của cùng đơn (trước chỉ dòng đầu).
  - S (Giao hàng một phần) = `"N"` cố định; T (Cho phép thử hàng) = flag `allow_try`; U = flag `allow_view_only` — không còn nhét `allow_try` vào cả S và T.
  - AA (Hình thức thanh toán, bắt buộc) = `"Người gửi trả"`.
  - R (Giá trị đơn) và Y (Số tiền COD) = tổng `product_price * quantity`, điền dòng đầu.
- Route `app/admin.py::export_orders_xlsx` không đổi — chữ ký `build_orders_xlsx(orders)` trả `bytes` giữ nguyên.

### Task 2 — Self-check stdlib cuối file

Khối `if __name__ == "__main__":` dùng `types.SimpleNamespace` (1 đơn, 2 items, chạy đứng độc lập không import Flask/models), assert đủ (a)-(g): theme vắng mặt, mọi part parse được XML, `C2` inlineStr `"0909999999"`, 30 cell header A1..AD1 có text, `A2`=`A3`=`1`, `AA2`="Người gửi trả", `S2`="N"/`T2`="Y"/`U2`="N", `R2`/`Y2` number cells. In `OK` khi hết.

## Verification

```
$ python app/xlsx_export.py
OK            # exit 0
```

Self-check pass toàn bộ assert (a)-(g). Commit chứa đúng 1 file (`git show --stat`: 253 insertions, 0 deletions); các file WIP khác của user không bị stage.

## Deviations from Plan

None — plan executed exactly as written.

## Ghi chú (theo plan)

- **E, F, G (Tỉnh/Thành phố, Quận/Huyện, Xã/Phường) để trống:** web chỉ lưu địa chỉ dạng text tự do, không tách được 2 cấp hành chính. Admin tự bổ sung tay sau khi tải file nếu Viettel Post yêu cầu.
- Không thêm dependency mới — stdlib zipfile giữ nguyên (openpyxl không có sẵn trong môi trường).

## Self-Check: PASSED

- FOUND: app/xlsx_export.py (commit `2ec2f86`)
- FOUND: commit `2ec2f86 fix(export): xlsx mo duoc bang Excel + dung mau 30 cot Viettel Post`
- FOUND: self-check `python app/xlsx_export.py` → `OK`, exit 0
