---
quick_id: 260803-kaa
description: Them state 'Da xac nhan' cho don hang + tru ton kho khi xac nhan
status: in_progress
type: execute
wave: 1
depends_on: []
autonomous: true
files_modified:
  - app/admin.py
  - app/templates/admin/orders/detail.html
  - app/templates/admin/stats.html
  - app/static/css/style.css
  - .planning/tmp/verify_quick_kaa.py
---

# Quick Plan: Thêm state "Đã xác nhận" + trừ tồn kho khi xác nhận

## Objective

Thêm trạng thái **Đã xác nhận** vào luồng đơn hàng, chèn giữa "Chờ xác nhận" và "Đã gói". Khi admin chuyển đơn từ "Chờ xác nhận" → "Đã xác nhận", hệ thống trừ tồn kho của từng sản phẩm trong đơn theo số lượng đặt (không phải cố định 1 — đơn mua 3 áo thì trừ 3).

**Thay đổi luồng hiện tại** (`app/admin.py`, Phase 7 forward-only):
- Cũ: `Chờ xác nhận → {Đã gói, Đã hủy}`
- Mới: `Chờ xác nhận → {Đã xác nhận, Đã hủy}`; `Đã xác nhận → {Đã gói, Đã hủy}`
- Edge trực tiếp `Chờ xác nhận → Đã gói` bị bỏ — bắt buộc xác nhận trước khi gói. Vẫn giữ cho hủy đơn ở "Chờ xác nhận" và "Đã xác nhận" (khớp pattern hủy ở "Đã gói" sẵn có).

**Không cần migration DB:** `orders.status` là cột free-string, default `'Chờ xác nhận'` không đổi. Đơn cũ đang ở "Đã gói"/"Đã gửi" không bị đụng.

## Design Decisions

1. **Trừ theo `OrderItem.quantity`**, không phải 1: `item.product.quantity = max(0, item.product.quantity - item.quantity)`. Sàn ở 0 (không âm) — `Product.status` tự suy `out_of_stock` khi quantity == 0.
2. **Bỏ qua item có product đã bị xóa** (`OrderItem.product_id` NULL qua ON DELETE SET NULL) — không có hàng để trừ.
3. **Idempotent nhờ forward-only map:** edge duy nhất đi vào `'Đã xác nhận'` là từ `'Chờ xác nhận'`, route server-side validate bằng `TRANSITION_MAP` → trừ đúng 1 lần/đơn, không trừ kép khi POST lặp.
4. **Cùng 1 commit** cho đổi status + trừ tồn kho (atomic).
5. **Không hoàn lại tồn kho khi hủy đơn sau khi xác nhận** — user chỉ yêu cầu chiều xác nhận → trừ; admin tự chỉnh `quantity` thủ công nếu cần. `ponytail:` đánh dấu trong code.

## Context

- Luồng trạng thái: `app/admin.py` `ORDER_STATUSES` / `TRANSITION_MAP` / `order_badge_class` / `update_order_status`; `app/models.py` `Order.status` (String(20), free label VN) + `OrderItem.product_id` (nullable SET NULL) + `Product.quantity`.
- UI stepper + nút chuyển: `app/templates/admin/orders/detail.html`; filter dropdown tự lặp `ORDER_STATUSES` (list.html không cần sửa); stats status breakdown: `app/templates/admin/stats.html`; badge CSS: `app/static/css/style.css` `.badge-order-*`.
- Mẫu verify: `.planning/tmp/verify_0701.py` (temp DB qua `create_app`, CSRF off, `check()` + `TASK_OK`). Không có tests/ dir — verification = script tmp như repo.
- `app/public.py` checkout **không** trừ tồn kho (ORD-12 v1.1 deferred) — giữ nguyên; việc trừ chỉ xảy ra ở route admin khi xác nhận.

<tasks>

<task type="auto">
  <name>Task 1: Backend — thêm state "Đã xác nhận" + trừ tồn kho trong admin.py</name>
  <files>app/admin.py, .planning/tmp/verify_quick_kaa.py</files>
  <action>
    Sửa `app/admin.py`:

    1. `ORDER_STATUSES` (dòng 11) → chèn `'Đã xác nhận'` sau `'Chờ xác nhận'`:
       `ORDER_STATUSES = ('Chờ xác nhận', 'Đã xác nhận', 'Đã gói', 'Đã gửi', 'Đã nhận', 'Đã hủy')`

    2. `TRANSITION_MAP` (dòng 19-25) → cập nhật:
       - `'Chờ xác nhận': {'Đã xác nhận', 'Đã hủy'}` (thay edge `'Đã gói'` cũ bằng `'Đã xác nhận'`)
       - thêm `'Đã xác nhận': {'Đã gói', 'Đã hủy'}`
       - giữ nguyên `'Đã gói': {'Đã gửi', 'Đã hủy'}`, `'Đã gửi': {'Đã nhận'}`, terminal `'Đã nhận'`/`'Đã hủy'`

    3. `order_badge_class` (dòng 35-42) → thêm `'Đã xác nhận': 'badge-order-confirmed'`.

    4. `update_order_status` (dòng 222-239) → khi `next_status == 'Đã xác nhận'`, trừ tồn kho TRƯỚC commit duy nhất:
       ```python
       if next_status == 'Đã xác nhận':
           for item in order.items.all():
               if item.product is not None:  # sản phẩm đã bị xóa thì bỏ qua (product_id NULL)
                   item.product.quantity = max(0, item.product.quantity - item.quantity)
       ```
       Đặt khối này ngay trước `order.status = next_status`; KHÔNG commit riêng — giữ nguyên một `db.session.commit()` duy nhất (atomic). Giữ nguyên thông báo flash hiện tại. `ponytail:` chú thích ngắn gọn rằng không hoàn lại tồn kho khi hủy đơn sau xác nhận (ngoài phạm vi yêu cầu).

    Tạo `.planning/tmp/verify_quick_kaa.py` theo mẫu `.planning/tmp/verify_0701.py` (temp DB qua gán `app_module.BASE_DIR`, `create_app`, `WTF_CSRF_ENABLED=False`, `check()` + `TASK_OK`). Seed: admin + 1 Product (quantity=5) + 1 Order "Chờ xác nhận" với 2 OrderItem (sản phẩm live qty=3, sản phẩm deleted `product_id=None` qty=2). Assert:
    - `ORDER_STATUSES` == 6 state, `'Đã xác nhận'` ở vị trí 2
    - `TRANSITION_MAP['Chờ xác nhận'] == {'Đã xác nhận', 'Đã hủy'}`; `TRANSITION_MAP['Đã xác nhận'] == {'Đã gói', 'Đã hủy'}`; `'Đã gói' not in TRANSITION_MAP['Chờ xác nhận']`
    - `order_badge_class('Đã xác nhận') == 'badge-order-confirmed'`
    - POST `/admin/orders/<id>/status` `next_status='Đã gói'` từ "Chờ xác nhận" bị reject (status + stock không đổi)
    - POST `next_status='Đã xác nhận'` → order.status == 'Đã xác nhận', stock 5 → 2 (trừ 3 của item live, item deleted qty=2 bị bỏ qua)
    - POST lặp `next_status='Đã xác nhận'` → reject, stock vẫn 2 (không trừ kép)
  </action>
  <verify>
    <automated>python .planning/tmp/verify_quick_kaa.py</automated>
  </verify>
  <done>
    Trạng thái backend mới hoạt động: luồng Chờ xác nhận → Đã xác nhận → Đã gói; trừ tồn kho đúng theo item quantity (sàn 0, bỏ qua sản phẩm đã xóa), đúng 1 lần/đơn; verify script in TASK_OK.
  </done>
</task>

<task type="auto">
  <name>Task 2: UI — stepper + nút chuyển + badge + stats cho "Đã xác nhận"</name>
  <files>app/templates/admin/orders/detail.html, app/templates/admin/stats.html, app/static/css/style.css, .planning/tmp/verify_quick_kaa.py</files>
  <action>
    1. `app/templates/admin/orders/detail.html`:
       - Stepper "Đã nhận" hoàn thành (dòng 56-59): thêm `<li class="is-done"><span class="dot"></span>Đã xác nhận</li>` giữa "Chờ xác nhận" và "Đã gói" (tổng 5 bước is-done).
       - `flow` (dòng 64): `['Chờ xác nhận', 'Đã xác nhận', 'Đã gói', 'Đã gửi', 'Đã nhận']`.
       - Branch "Chờ xác nhận" (dòng 70-81): đổi nút primary `value="Đã gói"` → `value="Đã xác nhận"`, label "Chuyển sang: Đã gói" → "Chuyển sang: Đã xác nhận". Giữ nguyên form Hủy.
       - Thêm branch mới `{% elif order.status == 'Đã xác nhận' %}` (giữa branch "Chờ xác nhận" và "Đã gói"): nút primary `value="Đã gói"` label "Chuyển sang: Đã gói" + form Hủy (same confirm pattern `onsubmit="return confirm(...)"`).

    2. `app/templates/admin/stats.html`: sau `<li>` "Chờ xác nhận" (dòng 36), thêm dòng:
       `<li><a href="{{ url_for('admin.orders', status='Đã xác nhận') }}">Đã xác nhận <span class="badge {{ order_badge_class('Đã xác nhận') }}">{{ status_counts.get('Đã xác nhận', 0) }}</span></a></li>`

    3. `app/static/css/style.css`: sau `.badge-order-pending` (dòng 463), thêm:
       `.badge-order-confirmed { color: #6D28D9; background: #F5F3FF; border-color: #DDD6FE; }`

    4. `app/templates/admin/orders/list.html` — KHÔNG sửa (filter dropdown lặp `ORDER_STATUSES` nên tự có "Đã xác nhận").

    Mở rộng `.planning/tmp/verify_quick_kaa.py`: sau khi confirm thành công (status "Đã xác nhận"), assert:
    - GET `/admin/orders/<id>` → body chứa `badge-order-confirmed` + "Chuyển sang: Đã gói" + cả 5 tên bước trong stepper ("Chờ xác nhận"…"Đã nhận")
    - GET `/admin/orders?status=Đã xác nhận` → filter dropdown có option "Đã xác nhận"
    - GET `/admin/stats` → body chứa `Đã xác nhận` trong status breakdown
  </action>
  <verify>
    <automated>python .planning/tmp/verify_quick_kaa.py</automated>
  </verify>
  <done>
    UI đầy đủ: stepper 5 bước, nút "Chuyển sang: Đã xác nhận" ở "Chờ xác nhận", nút "Chuyển sang: Đã gói" ở "Đã xác nhận", badge màu mới trên detail + list + stats; filter dropdown và stats breakdown có "Đã xác nhận"; verify script in TASK_OK.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| admin browser → POST /admin/orders/<id>/status | Untrusted `next_status` crosses here; route must not trust client-supplied status (server-side TRANSITION_MAP whitelist) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-kaa-01 | Tampering | update_order_status | mitigate | `next_status` validated against `TRANSITION_MAP.get(order.status, set())` before any change — già có, giữ nguyên; CSRF token bắt buộc trên form (Flask-WTF) |
| T-kaa-02 | Spoofing | update_order_status | mitigate | `@login_required` trên mọi admin route (`_protect_admin`) — già có; admin duy nhất |
| T-kaa-03 | Information disclosure | order.status free-string | accept | Không có PII mới; status là VN label đã hiển thị trên admin UI |
| T-kaa-04 | DoS / inventory corruption | stock decrement loop | mitigate | Trừ theo `OrderItem.quantity` (số nguyên), sàn `max(0, ...)`; idempotent nhờ forward-only edge — không trừ kép |
</threat_model>

<verification>
- `python .planning/tmp/verify_quick_kaa.py` in `TASK_OK` (cả 2 task).
- Không đụng `data/app.db` thật — verify script dùng temp DB (pattern `.planning/tmp/verify_0701.py`).
- Không dependency mới; không migration schema.
</verification>

<success_criteria>
- Admin thấy state "Đã xác nhận" giữa "Chờ xác nhận" và "Đã gói" (filter, stepper, badge, stats).
- Chuyển đơn sang "Đã xác nhận" trừ tồn kho từng sản phẩm đúng số lượng đặt (sàn 0, bỏ qua sản phẩm đã xóa).
- Forward-only giữ nguyên: không nhảy cóc, không trừ kép, không trừ khi reject.
- Giỏ hàng/checkout không đổi (vẫn không trừ tại thời điểm đặt — ORD-12 giữ nguyên).
</success_criteria>
