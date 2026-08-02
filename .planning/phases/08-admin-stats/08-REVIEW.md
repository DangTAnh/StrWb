---
phase: 08-admin-stats
reviewed: 2026-08-03T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - app/admin.py (stats route, lines 150-208)
  - app/templates/admin/stats.html
  - app/templates/admin/dashboard.html (nav addition only)
  - app/static/css/style.css (Phase 8 section, lines 493-515)
  - .planning/tmp/verify_08_stats_full.py
findings:
  critical: 0
  warning: 0
  info: 6
  total: 6
status: issues_found
---

# Phase 8: Code Review Report — Admin Stats Dashboard

**Reviewed:** 2026-08-03
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found (no Critical/Warning; 6 Info items, 2 actionable in verify script)

## Summary

Reviewed Phase 8 (admin stats dashboard: `GET /admin/stats` → `admin.stats()`). Read `08-CONTEXT.md`, `08-UI-SPEC.md`, and prior `06-REVIEW.md` / `07-VERIFICATION.md` for established patterns, then read every code file under review and grounded in `app/models.py`, `app/__init__.py`, `app/forms.py`.

**Tổng thể: implementation chắc chắn về security và logic.** Các điểm security và logic chính đều đúng:
- **Auth/CSRF**: GET-only, server-rendered, được bảo vệ bởi blueprint-wide `@login_required` (admin.py:45-49). Unauthorized → 302 redirect tới `auth.login`.
- **No SQL injection**: mọi predicate đều là SQLAlchemy expression object; giá trị interpolated là module constants (`REVENUE_STATUSES`).
- **No XSS**: status labels và `profit_note` đều server-controlled; Jinja autoescaping bật.
- **STAT-01/02/03/04 compliance**: revenue filter `status IN ('Đã gửi', 'Đã nhận')`; profit loại item `product_cost_price IS NULL`; inventory buckets khớp STAT-04; template dùng `status_counts.get(s, 0)` cho all 5 statuses.
- **Empty-state safety**: mọi SUM đều có `coalesce(..., 0)`; `format_price`'s `int(value)` không bao giờ nhận `None`. Verify script test cả full-seed và empty-DB.

Không tìm thấy Critical hoặc Warning. Các finding chủ yếu là Info-level về code quality (query redundancy, dead code trong verify script, style consistency). 2 item trong verify script nên được sửa ngay.

---

## Critical Issues

Không có finding Critical.

Load-bearing paths đã được verify:
- `coalesce(..., 0)` xung quanh mọi SUM (admin.py:157, 169) → `format_price` không bao giờ crash với `int(None)`.
- `count()` aggregates (admin.py:170, 179, 192) không trả về NULL.
- `OrderItem.product_price` / `quantity` là non-nullable, `quantity >= 1` (CheckConstraint models.py:90, 97-98) → arithmetic không chạm NULL operand.
- `Product.quantity` non-nullable (models.py:32) → `quantity > 0` / `quantity == 0` chia đủ mọi non-discontinued product đúng 1 nhóm.

---

## Warning Issues

Không có finding Warning.

Đã verify các điểm sau là đúng:
- **Revenue/profit correctness**: revenue chỉ tính đơn `Đã gửt`/`Đã nhận`; profit loại `product_cost_price IS NULL`, note chỉ hiện khi có item bị loại (admin.py:185).
- **Inventory buckets**: `total` (incl discontinued), `in_stock` (qty>0 AND not discontinued), `out_of_stock` (qty==0 AND not discontinued), `discontinued` (discontinued=True) — khớp STAT-04, không overlap (admin.py:198-201).
- **Deleted-product resilience**: stats join trên `order_id`, snapshot columns giữ nguyên khi `OrderItem.product_id` bị SET NULL (models.py:94), nên xóa product không làm thay đổi doanh thu lịch sử.

---

## Info Issues

### IN-01: `verify_08_stats_full.py:88-89` — vòng lặp placeholder dead code + typo

**File:** `.planning/tmp/verify_08_stats_full.py:88-89`

**Issue:** Vòng lặp `for status in ['Chờ xác nhận', 'Đã hủy', 'Đã nhận', 'Đã gửt', 'Đóng gói']: pass` là no-op, chỉ có comment `# placeholders`. Thật nữa còn có typo `'Đóng gói'` (đúng là `'Đã gói'`). Các assertion thực sự là các lời gọi `_badge_count` ở dòng 92-95.

**Fix:** Xóa vòng lặp và comment.

### IN-02: `verify_08_stats_full.py:146` — gán `BASE_DIR` dư thừa

**File:** `.planning/tmp/verify_08_stats_full.py:146`

**Issue:** `app_module.BASE_DIR = tmpdir2` gán lại trùng với `_setup_app(tmpdir2)` đã gán sẵn ở dòng 31. Dòng này vô nghĩa (harmless) nhưng gây hiểu nhầm rằng nó đang làm gì đó mà `_setup_app` chưa làm.

**Fix:** Xóa dòng 146.

### IN-03: `admin.py:178-183` — query thứ ba thừa (merge với Q1)

**File:** `app/admin.py:178-183`

**Issue:** Q3 (`total_qual_items`) dùng cùng join + filter với Q1 và là aggregate subset. Thêm `db.func.count(OrderItem.id)` vào SELECT của Q1 (dòng 157) và unpack 3 giá trị sẽ loại bỏ 1 full scan của `order_items JOIN orders`. Với khố lượng data hiện tại không ảnh hưởng; merge nếu dashboard mở rộng.

**Fix (tù chọn):**
```python
revenue, units_sold, total_qual_items = (
    db.session.query(
        db.func.coalesce(db.func.sum(OrderItem.product_price * OrderItem.quantity), 0),
        db.func.coalesce(db.func.sum(OrderItem.quantity), 0),
        db.func.count(OrderItem.id),
    )
    .join(Order, OrderItem.order_id == Order.id)
    .filter(Order.status.in_(REVENUE_STATUSES))
    .one()
)
```

### IN-04: `admin.py:173` — style operator không nhất quán

**File:** `app/admin.py:173`

**Issue:** Dùng `OrderItem.product_cost_price.isnot(None)` (legacy alias `isnot`) trong khi cùng route dùng `.is_(True)` / `.is_(False)` cho boolean (dòng 199-201). Cả hai compile ra SQL giống nhau và không deprecated, nhưng nên dùng `is_not(None)` để nhất quán.

**Fix (tù chọn):** `.is_not(None)`.

### IN-05: `admin.py:186` — profit note đếm line items, không phải distinct products

**File:** `admin.py:186`

**Issue:** `profit_items` là `count(OrderItem.id)` (admin.py:170), nên 2 line items cùng 1 product render "Lợi nhuận tính trên 2 sản phẩm" dù thực tế là 1 product / 2 dòng. Wording này **phù hợp với STAT-02 locked decision** ("Lợi nhuận tính trên N sản phẩm có giá nhập"), nên chấp nhận được — chỉ ghi chú semantic mismatch nếu spec muốn distinct products trong tương lai.

**Fix:** Không áp dụng trừ khi thay đổi spec; ghi chú.

### IN-06: `verify_08_stats_full.py:87-89` — assertion cho `'Đã gói'` chưa kiểm tra badge count

**File:** `.planning/tmp/verify_08_stats_full.py:88-96`

**Issue:** Trong full-seed scenario, `Đã gói` = 0 (không có order nào ở trạng thái này). Verify script chỉ assert `'Đã gói' in html` (dòng 90) nhưng không verify badge count = 0 cho status này, khác biệt với 4 status còn lại đều có `_badge_count`. Dòng 88 vòng lặp placeholder có chứa `'Đóng gói'` (typo) thay vì `'Đã gói'`, gợi ý người viết đã có 1 assertion draft cho `Đã gói = 0` nhưng chưa hoàn thiện.

**Fix (tù chọn):** Thêm `assert _badge_count(html, 'Đã gói') == 0`.

---

## Phương pháp xác minh (đã chạy)

Subagent đã đọc toàn bộ code và grounded logic trong `app/models.py` (các constraint, nullable), `app/__init__.py` (format_price filter, CSRF, auth), `app/forms.py` (Optional validators). Đã verify:
- Mọi SUM có `coalesce(..., 0)`.
- `count()` aggregates không trả về NULL.
- `quantity >= 1` CheckConstraint + non-nullable price → arithmetic an toàn.
- Inventory: non-nullable `Product.quantity` + boolean `discontinued` → `quantity > 0` / `quantity == 0` chia đủ exact cover cho non-discontinued; `discontinued` count tách biệt.
- Template dùng `status_counts.get(s, 0)` cho all 5 statuses → không crash dù group_by bỏ qua zero-count.
- Profit note chỉ set khi `total_qual_items - profit_items > 0` (admin.py:185).
- Auth: `before_request` + `@login_required` bảo vệ route; GET-only không cần CSRF token.

---

_Reviewed: 2026-08-03_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
