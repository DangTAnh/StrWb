/* Product form gallery: reorder + direct-delete + multi-file upload (D-12/D-13/D-17).
   Extracted from app/templates/admin/products/form.html inline script.
   Zero framework — reads/writes hidden image_order + delete_images fields that
   the server-side _process_image_batch expects (new:<i> tokens).

   Delete UX: each gallery item has a ✕ delete-btn. For existing images, the
   item's data-id is appended to delete_images (server removes the row + file on
   submit). For new/unsaved uploads, the item is removed from newItems/newFiles
   + the file input is re-synced immediately (no server round-trip). */
(function () {
  'use strict';
  var grid = document.getElementById('gallery-grid');
  if (!grid) return; // not a product form
  var fileInput = document.getElementById('gallery-file');
  var orderField = document.getElementById('image_order');
  var deleteField = document.getElementById('delete_images');
  var newFiles = [];
  var newItems = [];

  function syncOrder() {
    var order = [];
    grid.querySelectorAll('.gallery-item').forEach(function (item) {
      var id = item.getAttribute('data-id');
      if (id) {
        order.push(id);
      } else {
        order.push('new:' + newItems.indexOf(item));
      }
    });
    orderField.value = order.join(',');
  }
  // deleteField is populated directly by markExistingDeleted() (direct-delete UX).
  function syncFileInput() {
    var dt = new DataTransfer();
    newFiles.forEach(function (f) { dt.items.add(f); });
    fileInput.files = dt.files;
  }
  function updateDisabled() {
    var items = grid.querySelectorAll('.gallery-item');
    items.forEach(function (item, i) {
      var up = item.querySelector('.reorder-btn[data-dir="-1"]');
      var down = item.querySelector('.reorder-btn[data-dir="1"]');
      if (up) up.disabled = (i === 0);
      if (down) down.disabled = (i === items.length - 1);
    });
  }
  function updatePrimaryBadge() {
    var items = grid.querySelectorAll('.gallery-item');
    items.forEach(function (item) {
      var badge = item.querySelector('.badge-primary');
      if (badge) badge.remove();
    });
    if (items.length > 0) {
      var badge = document.createElement('span');
      badge.className = 'badge-primary';
      badge.textContent = 'Ảnh chính';
      items[0].insertBefore(badge, items[0].firstChild);
    }
  }
  // Remove a new (unsaved) upload item from the gallery + the file list.
  function removeNewItem(item) {
    var idx = newItems.indexOf(item);
    if (idx >= 0) {
      newFiles.splice(idx, 1);
      newItems.splice(idx, 1);
    }
    if (item.parentNode) item.parentNode.removeChild(item);
    syncFileInput();
    syncOrder();
    updateDisabled();
    updatePrimaryBadge();
  }
  // Mark an existing (saved) image for deletion on submit (soft — removed visually too).
  function markExistingDeleted(item) {
    var id = item.getAttribute('data-id');
    if (id) {
      var current = deleteField.value ? deleteField.value.split(',') : [];
      if (current.indexOf(id) === -1) current.push(id);
      deleteField.value = current.join(',');
    }
    if (item.parentNode) item.parentNode.removeChild(item);
    syncOrder();
    updateDisabled();
    updatePrimaryBadge();
  }
  function makeNewItem(file) {
    var item = document.createElement('div');
    item.className = 'gallery-item';
    var a = document.createElement('a');
    a.target = '_blank'; a.rel = 'noopener';
    var img = document.createElement('img');
    img.width = 96; img.height = 96; img.alt = file.name;
    img.src = URL.createObjectURL(file);
    a.href = img.src;
    a.appendChild(img);
    item.appendChild(a);
    var actions = document.createElement('div');
    actions.className = 'gallery-actions';
    ['-1', '1'].forEach(function (dir) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'reorder-btn';
      b.setAttribute('data-dir', dir);
      b.setAttribute('aria-label', dir === '-1' ? 'Chuyển lên' : 'Chuyển xuống');
      b.textContent = dir === '-1' ? '↑' : '↓';
      actions.appendChild(b);
    });
    // direct delete button (no checkbox) — removes the new upload immediately
    var del = document.createElement('button');
    del.type = 'button'; del.className = 'delete-btn';
    del.setAttribute('aria-label', 'Xóa ảnh');
    del.textContent = '✕';
    actions.appendChild(del);
    item.appendChild(actions);
    return item;
  }
  function renderNew() {
    newItems.forEach(function (item) { if (item.parentNode) item.parentNode.removeChild(item); });
    newItems = [];
    newFiles.forEach(function (file) {
      var item = makeNewItem(file);
      newItems.push(item);
      grid.appendChild(item);
    });
    updateDisabled();
    updatePrimaryBadge();
    syncOrder();
  }
  function moveNew(from, dir) {
    var to = from + dir;
    if (to < 0 || to >= newFiles.length) return;
    var tmp = newFiles[from]; newFiles[from] = newFiles[to]; newFiles[to] = tmp;
    renderNew();
    syncFileInput();
  }
  function moveExisting(item, dir) {
    var items = Array.prototype.filter.call(grid.children, function (c) { return c.classList.contains('gallery-item'); });
    var idx = items.indexOf(item);
    var to = idx + dir;
    if (to < 0 || to >= items.length) return;
    grid.insertBefore(item, to > idx ? items[to].nextSibling : items[to]);
    syncOrder();
    updateDisabled();
    updatePrimaryBadge();
  }
  grid.addEventListener('click', function (e) {
    var target = e.target;
    // direct-delete button: existing image -> mark for server delete; new upload -> remove from file list
    var delBtn = target.closest('.delete-btn');
    if (delBtn) {
      e.preventDefault();
      var item = delBtn.closest('.gallery-item');
      if (!item) return;
      var newIdx = newItems.indexOf(item);
      if (newIdx >= 0) {
        removeNewItem(item);
      } else {
        markExistingDeleted(item);
      }
      return;
    }
    // reorder buttons (unchanged behavior)
    var btn = target.closest('.reorder-btn');
    if (!btn) return;
    e.preventDefault();
    var item = btn.closest('.gallery-item');
    var dir = parseInt(btn.getAttribute('data-dir'), 10);
    var idx = newItems.indexOf(item);
    if (idx >= 0) {
      moveNew(idx, dir);
    } else {
      moveExisting(item, dir);
    }
  });
  fileInput.addEventListener('change', function () {
    newFiles = Array.prototype.slice.call(fileInput.files);
    renderNew();
    syncFileInput();
  });

  /* ---- Ctrl+V / clipboard paste -> feed into the existing file-input flow ----
     Only image/* blobs from the clipboard are accepted; non-images are ignored.
     Server-side _process_image_batch still runs magic-byte validation, so a
     fake/mismatched paste is rejected safely (Pitfall 3 gate). */
  function handlePaste(e) {
    var clipboardFiles = [];
    if (e.clipboardData && e.clipboardData.files) {
      var files = e.clipboardData.files;
      for (var i = 0; i < files.length; i++) {
        clipboardFiles.push(files[i]);
      }
    }
    var images = clipboardFiles.filter(function (f) { return f.type.indexOf('image/') === 0; });
    if (!images.length) return;
    e.preventDefault();
    var dt = new DataTransfer();
    // preserve already-selected uploads, then append the pasted images
    var existing = fileInput.files ? Array.prototype.slice.call(fileInput.files) : [];
    existing.forEach(function (f) { dt.items.add(f); });
    images.forEach(function (f) { dt.items.add(f); });
    fileInput.files = dt.files;
    fileInput.dispatchEvent(new Event('change'));
    if (grid.classList) {
      grid.classList.add('paste-received');
      setTimeout(function () { grid.classList.remove('paste-received'); }, 600);
    }
  }
  // listen on the form (works whether focus is on a field or the gallery)
  var form = grid.closest('form');
  if (form) {
    form.addEventListener('paste', handlePaste);
  }
})();
