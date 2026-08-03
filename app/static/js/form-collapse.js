/* Collapsible form groups: toggle caret + persist open/closed per group key.
   State stored in localStorage under form-collapse:{key} → "1"/"0".
   No framework — pure DOM. */
(function () {
  'use strict';
  var PREFIX = 'form-collapse:';
  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  function loadState(key) {
    return localStorage.getItem(PREFIX + key);
  }
  function saveState(key, val) {
    try { localStorage.setItem(PREFIX + key, val); } catch (e) { /* quota/readonly ignore */ }
  }

  function applyGroup(group) {
    var key = group.getAttribute('data-collapse-key');
    if (!key) return;
    var btn = qs('.collapse-toggle', group);
    var body = qs('.collapse-body', group);
    var caret = qs('.caret', group);
    if (!btn || !body || !caret) return;
    var saved = loadState(key);
    var expanded = saved === null ? true : (saved === '1');
    setExpanded(group, body, caret, btn, expanded);
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      expanded = !expanded;
      setExpanded(group, body, caret, btn, expanded);
      saveState(key, expanded ? '1' : '0');
    });
  }

  function setExpanded(group, body, caret, btn, expanded) {
    body.style.display = expanded ? '' : 'none';
    caret.textContent = expanded ? '▼' : '▶';
    btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  }

  // init
  qsa('.form-group-collapsible').forEach(applyGroup);
})();
