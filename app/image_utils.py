"""Image validation and storage engine (Phase 2, D-16).

The ONLY gate between untrusted client upload bytes and the filesystem.
All re-encoded JPEGs land in app/static/uploads/ under UUID filenames.
"""
import os
import uuid

from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_DIMENSION = 2000  # Pitfall 7: decompression-bomb cap (D-16)
THUMBNAIL_SIZE = (400, 400)  # serves 48px table cell + 96px gallery preview

_JPEG_MAGIC = b'\xff\xd8\xff'
_PNG_MAGIC = b'\x89PNG\r\n\x1a\n'


def check_magic_bytes(ext, head):
    """Return True if the first bytes of `head` match the signature for `ext` (Pitfall 3)."""
    ext = ext.lower()
    if ext in ('.jpg', '.jpeg'):
        return head[:3] == _JPEG_MAGIC
    if ext == '.png':
        return head[:8] == _PNG_MAGIC
    if ext == '.webp':
        return head[:4] == b'RIFF' and head[8:12] == b'WEBP'
    return False


def validate_image_upload(file_storage):
    """Validate a single uploaded file. Returns (ok: bool, reason: str)."""
    filename = (file_storage.filename or '').strip()
    if not filename:
        return (False, 'Không có file nào được chọn')
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return (False, f'Định dạng không hợp lệ ({ext or "không xác định"}). Chỉ chấp nhận .jpg, .jpeg, .png, .webp')
    file_storage.stream.seek(0)
    head = file_storage.stream.read(12)
    if not check_magic_bytes(ext, head):
        return (False, 'File không phải ảnh hợp lệ (sai định dạng thực tế)')
    file_storage.stream.seek(0)
    try:
        img = Image.open(file_storage.stream)
        img.verify()
    except Exception:
        return (False, 'File ảnh bị hỏng hoặc không đọc được')
    file_storage.stream.seek(0)
    try:
        img = Image.open(file_storage.stream)
        w, h = img.size
    except Exception:
        return (False, 'File ảnh bị hỏng hoặc không đọc được')
    if w > MAX_DIMENSION or h > MAX_DIMENSION:
        return (False, f'Ảnh quá lớn ({w}x{h}px). Tối đa {MAX_DIMENSION}x{MAX_DIMENSION}px')
    return (True, '')
