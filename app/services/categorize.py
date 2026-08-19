"""Auto-classify products into categories based on keyword matching.

Used by admin product CRUD as a one-shot suggestion: when an admin saves a product
with a name like "Áo sơ mi nam", any Category whose keywords CSV contains "áo"
(or "ao" after normalization) will be auto-added — unless the admin unchecked them
in the form (the form's category_ids is the source of truth, this helper only
SUGGESTS additions for products that have zero categories assigned yet).
"""
from __future__ import annotations

import re
import unicodedata

from ..models import Category, Product


def normalize_search_text(text):
    """NFD -> strip combining marks -> casefold. 'Áo' -> 'ao'. Mirrors public.normalize_search_text."""
    if not text:
        return ''
    decomposed = unicodedata.normalize('NFD', text)
    stripped = ''.join(ch for ch in decomposed if unicodedata.category(ch) != 'Mn')
    return stripped.casefold()


def _keyword_match(keyword: str, text: str) -> bool:
    """Check if keyword matches as a whole word/token in text.

    Uses word-boundary-aware matching to avoid false positives like "ao" matching "giay the thao".
    - Splits text into tokens by non-alphanumeric chars
    - Checks if keyword matches any token (exact or prefix)
    """
    if not keyword or not text:
        return False
    # Tokenize: split by non-alphanumeric
    tokens = re.split(r'[^\w]+', text)
    for token in tokens:
        if not token:
            continue
        if token == keyword or token.startswith(keyword + ' ') or token.startswith(keyword):
            return True
    return False


def _category_matches(category: Category, name_norm: str) -> bool:
    """Category khớp tên sản phẩm (đã normalize) theo keywords CSV."""
    if not category or not category.keywords:
        return False
    for kw in category.keywords.split(','):
        kw_norm = normalize_search_text(kw.strip())
        if kw_norm and _keyword_match(kw_norm, name_norm):
            return True
    return False


def auto_classify(product: Product) -> list[Category]:
    """Compute which categories a product should belong to based on keyword match.

    Returns a list of Category objects. Empty list if no keywords match.
    Caller is responsible for assigning product.categories = matched.
    """
    if not product or not product.name:
        return []

    name_norm = normalize_search_text(product.name)
    cats = Category.query.all()
    return [cat for cat in cats if _category_matches(cat, name_norm)]


def auto_assign_products(category: Category) -> int:
    """Gán category vào tất cả sản phẩm có tên khớp keywords (additive — không bỏ gán cũ).

    Dùng khi tạo/sửa danh mục để back-fill sản phẩm đã có sẵn. Trả về số sản phẩm mới gán.
    """
    if category is None or not category.keywords:
        return 0
    count = 0
    for product in Product.query.all():
        name_norm = normalize_search_text(product.name)
        if category not in product.categories and _category_matches(category, name_norm):
            product.categories.append(category)
            count += 1
    return count


def merge_with_explicit(product: Product, explicit_ids: list) -> list[Category]:
    """Combine explicit category_ids from form with auto-classified suggestions.

    Logic:
      - Start with explicit IDs from form (admin's choice).
      - Auto-add any category that matches keywords BUT was not in explicit list
        (so admin doesn't lose their uncheck). Only additive.

    Returns Category list to assign to product.categories.
    """
    explicit_cats = Category.query.filter(Category.id.in_([int(i) for i in explicit_ids if str(i).isdigit()])).all() if explicit_ids else []
    explicit_ids_set = {c.id for c in explicit_cats}
    suggested = [c for c in auto_classify(product) if c.id not in explicit_ids_set]
    return explicit_cats + suggested
