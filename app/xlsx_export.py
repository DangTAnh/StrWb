"""EXPORT-01: xây dựng file .xlsx bằng stdlib zipfile (không dùng openpyxl).

Header khớp template gốc collect_fee_mass_order_creation_template_vn_2level_addr.xlsx,
sheet "Tạo đơn (địa chỉ mới)" — đủ 30 cột A..AD.
"""
import zipfile, io

# Cột ghi dạng số (0-indexed): A mã đơn, K số lượng, L giá tiền,
# M cân nặng, R giá trị đơn, Y số tiền COD. SĐT (C) là TEXT để giữ số 0 đầu.
NUMBER_COLS = {0, 10, 11, 12, 17, 24}


def _esc(text):
    if text is None:
        return ""
    s = str(text)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _col_letter(n):
    s = ""
    n += 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s


HEADERS = [
    "*Mã đơn hàng",
    "*Tên người nhận",
    "*Số điện thoại",
    "*Địa chỉ chi tiết",
    "Tỉnh/Thành Phố",
    "Quận/Huyện",
    "Xã/Phường",
    "Lưu ý về địa chỉ",
    "Mã bưu chính",
    "*Tên sản phẩm",
    "Số lượng (Thông tin bắt buộc khi chọn Giao hàng một phần)",
    "Giá tiền (Thông tin bắt buộc khi chọn Giao hàng một phần)",
    "*Tổng cân nặng bưu gửi (KG)",
    "Chiều dài (CM)",
    "Chiều rộng (CM)",
    "Chiều cao (CM)",
    "Mã khách hàng",
    "*Giá trị đơn hàng",
    "*Giao hàng một phần (Y/N)",
    "*Cho phép thử hàng (Y/N)",
    "*Cho xem hàng, không cho thử (Y/N)",
    "Thu phí từ chối nhận hàng (Y/N)",
    "Phí từ chối nhận hàng cần thu",
    "*Thu COD (Y/N)",
    "Số tiền COD",
    "bưu gửi giá trị cao (Y/N)",
    "*Hình thức thanh Toán",
    "Lưu ý giao hàng",
    "Nhắc nhở điền đúng số tiền COD",
    'Đơn chỉ hoàn thành nếu ở dưới hiện "Đủ điều kiện"',
]


def build_orders_xlsx(orders):
    num_cols = len(HEADERS)

    # Mỗi OrderItem 1 dòng. Mã đơn (A) lặp trên MỌI dòng item của cùng đơn
    # (theo sheet ví dụ của template); thông tin người nhận/Y/N chỉ dòng đầu.
    data_rows = []
    for seq, order in enumerate(orders, start=1):
        items = list(order.items)
        if not items:
            items = [None]
        total_value = sum(i.product_price * i.quantity for i in order.items) if order.items else 0
        for idx, item in enumerate(items):
            is_first = (idx == 0)
            row = [""] * num_cols
            # A: Mã đơn hàng — mọi dòng item
            row[0] = str(seq)
            if is_first:
                row[1] = order.customer_name or ""   # B: Tên người nhận
                row[2] = order.customer_phone or ""  # C: SĐT (TEXT, giữ "0…")
                row[3] = order.customer_address or ""  # D: Địa chỉ chi tiết
                # E-I: rỗng — web lưu địa chỉ text tự do, không tách 2 cấp
                row[17] = str(total_value)           # R: Giá trị đơn hàng
                row[18] = "N"                        # S: Giao hàng một phần
                row[19] = "Y" if order.allow_try else "N"          # T: Cho phép thử hàng
                row[20] = "Y" if order.allow_view_only else "N"    # U: Cho xem không thử
                row[23] = "Y"                        # X: Thu COD
                row[24] = str(total_value)           # Y: Số tiền COD
                row[26] = "Người gửi trả"            # AA: Hình thức thanh toán
            # J-L: tên SP / số lượng / giá tiền — mọi dòng item
            if item is not None:
                row[9] = item.product_name or ""
                row[10] = str(item.quantity)
                row[11] = str(item.product_price)
            # M: cân nặng — mọi dòng
            if order.total_weight is not None:
                row[12] = str(order.total_weight)
            data_rows.append(row)

    # XML worksheet: header row 1 + data rows
    xml_rows = ["<sheetData>"]
    xml_rows.append('<row r="1">')
    for i, h in enumerate(HEADERS):
        xml_rows.append(
            f'<c r="{_col_letter(i)}1" t="inlineStr"><is><t>{_esc(h)}</t></is></c>'
        )
    xml_rows.append("</row>")

    for r_idx, row_data in enumerate(data_rows, start=2):
        xml_rows.append(f'<row r="{r_idx}">')
        for c_idx, val in enumerate(row_data):
            c_ref = f"{_col_letter(c_idx)}{r_idx}"
            if val == "" or val is None:
                xml_rows.append(f'<c r="{c_ref}"/>')
            elif c_idx in NUMBER_COLS:
                xml_rows.append(f'<c r="{c_ref}"><v>{val}</v></c>')
            else:
                xml_rows.append(
                    f'<c r="{c_ref}" t="inlineStr"><is><t>{_esc(val)}</t></is></c>'
                )
        xml_rows.append("</row>")
    xml_rows.append("</sheetData>")

    worksheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        + ''.join(xml_rows)
        + '</worksheet>'
    )

    # Theme là optional part — bỏ hẳn khỏi package (theme thiếu fontScheme/fmtScheme
    # khiến Excel báo lỗi content). rels chỉ còn worksheet + styles.
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
        '</Relationships>'
    )
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<workbookPr/>'
        '<sheets><sheet name="Tạo đơn (địa chỉ mới)" sheetId="1" r:id="rId1"/></sheets>'
        '</workbook>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '</Types>'
    )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/>'
            '</Relationships>')
        zf.writestr("xl/_rels/workbook.xml.rels", rels_xml)
        zf.writestr("xl/styles.xml", styles_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/worksheets/sheet1.xml", worksheet_xml)
    buffer.seek(0)
    return buffer.read()


if __name__ == "__main__":
    import types
    import xml.etree.ElementTree as ET

    NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

    def _item(name, qty, price):
        return types.SimpleNamespace(product_name=name, quantity=qty, product_price=price)

    order = types.SimpleNamespace(
        customer_name="Nguyễn Văn A",
        customer_phone="0909999999",
        customer_address="123 Lê Lợi, Q1",
        total_weight=1.5,
        allow_try=True,
        allow_view_only=False,
        items=[_item("Áo sơ mi", 2, 150000), _item("Quần jean", 1, 300000)],
    )

    zf = zipfile.ZipFile(io.BytesIO(build_orders_xlsx([order])))
    names = zf.namelist()

    # (a) theme part đã bị loại
    assert "xl/theme/theme1.xml" not in names, names
    # (b) mọi part well-formed XML
    parts = {n: ET.fromstring(zf.read(n)) for n in names}

    sheet = parts["xl/worksheets/sheet1.xml"]

    def cell(ref):
        for c in sheet.iter(f"{NS}c"):
            if c.get("r") == ref:
                return c
        raise AssertionError(f"missing cell {ref}")

    def text(c):
        return c.find(f"{NS}is/{NS}t").text

    # (d) header đủ 30 cell A1..AD1, mỗi cell có text
    hdr_cells = [c for c in sheet.iter(f"{NS}c") if c.get("r").endswith("1")]
    letters = [_col_letter(i) for i in range(30)]
    assert [c.get("r")[:-1] for c in hdr_cells] == letters, len(hdr_cells)
    assert all(text(c) for c in hdr_cells)
    assert len(HEADERS) == 30
    # (c) SĐT giữ số 0 đầu
    assert cell("C2").get("t") == "inlineStr" and text(cell("C2")) == "0909999999"
    # (e) mã đơn lặp mọi dòng item
    assert cell("A2").find(f"{NS}v").text == "1"
    assert cell("A3").find(f"{NS}v").text == "1"
    # (f) hình thức thanh toán
    assert text(cell("AA2")) == "Người gửi trả"
    # (g) flag Y/N + number cells
    assert text(cell("S2")) == "N"
    assert text(cell("T2")) == "Y"
    assert text(cell("U2")) == "N"
    assert cell("R2").get("t") != "inlineStr" and cell("R2").find(f"{NS}v") is not None
    assert cell("Y2").get("t") != "inlineStr" and cell("Y2").find(f"{NS}v") is not None
    print("OK")
