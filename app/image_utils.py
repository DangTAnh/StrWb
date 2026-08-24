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
MAX_DIMENSION = 10000  # Pitfall 7: decompression-bomb cap (D-16)
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


def save_image_file(file_storage):
    """Re-encode the upload to JPEG, save full-size + thumbnail under a UUID name.

    Returns (filesystem_name, original_filename).
    """
    original_filename = (file_storage.filename or '').strip()
    uuid_name = uuid.uuid4().hex  # IMG-02: UUID filesystem name, never the user's name
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_storage.stream.seek(0)
    img = Image.open(file_storage.stream)
    img.load()
    img = img.convert('RGB')  # re-encode strips EXIF/payloads, normalizes alpha (Pitfall 7 step 3)
    if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION))  # belt-and-suspenders after validation
    full_name = uuid_name + '.jpg'
    img.save(os.path.join(UPLOAD_DIR, full_name), 'JPEG', quality=85)
    thumb = img.copy()
    thumb.thumbnail(THUMBNAIL_SIZE)
    thumb_name = uuid_name + '_thumb.jpg'
    thumb.save(os.path.join(UPLOAD_DIR, thumb_name), 'JPEG', quality=82)
    return (full_name, original_filename)


def delete_image_files(filename):
    """Remove a saved image and its thumbnail from disk.

    Returns (deleted_count, failed_count). Missing files are treated as
    already-removed (not a failure); locked/permission errors are counted
    as failures so the caller can surface a D-09 warning without blocking.
    """
    deleted = 0
    failed = 0
    files = [filename]
    if filename and filename.endswith('.jpg'):
        files.append(filename[:-4] + '_thumb.jpg')
    for f in files:
        try:
            os.remove(os.path.join(UPLOAD_DIR, f))
            deleted += 1
        except FileNotFoundError:
            deleted += 1  # already gone -> not a failure
        except OSError:
            failed += 1
    return (deleted, failed)
