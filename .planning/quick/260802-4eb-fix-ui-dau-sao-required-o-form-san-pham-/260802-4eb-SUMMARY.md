---
quick_id: 260802-4eb
status: complete
completed: 2026-08-02
---

# Quick Summary: Fix dấu sao required xuống dòng

**Fix:** `.form-field label` đổi `display: block` → `inline-block` (app/static/css/style.css). Span `.required *` giờ nằm cùng dòng với "Tên sản phẩm" (và price, quantity). Label không có `*` không đổi layout — input `width:100%` vẫn đẩy xuống dòng. `.checkbox-label` / `.img-delete` override riêng, không ảnh hưởng.

**Verified:** root cause = label block đẩy sibling span xuống dòng; 3 label có `*` (form.html:13,20,58) cùng dòng sau fix. Shared form → cả edit + new đều đúng.
