// Public search AJAX handler — submit form without page reload, render result HTML.
//
// Behavior:
// - Intercept .search-form submit, prevent default reload
// - POST form data with X-Requested-With: XMLHttpRequest (matches Flask is_ajax)
// - Server returns JSON: { q, html, pagination } — full <article> markup already rendered server-side
// - Replace .product-grid innerHTML with new markup (include _product_card.html duplicated)
// - Update pagination <nav> with rendered links
// - Update URL bar with ?q=...&page=... via history.pushState (so refresh / share works)
// - On popstate (back button), re-fetch the corresponding page
//
// Requires: public/_search.html template that returns JSON. The product-card markup is rendered
// server-side in JSON under key `html` (a string of <article>...</article> elements).

(function () {
  'use strict';

  function init() {
    const form = document.querySelector('.search-form');
    if (!form) return;
    // Only intercept if results area exists (we're on /search page).
    const grid = document.querySelector('.product-grid');
    if (!grid) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const q = (form.querySelector('input[name="q"]') || {}).value || '';
      runSearch(q, 1);
    });

    window.addEventListener('popstate', function () {
      const params = new URLSearchParams(window.location.search);
      runSearch(params.get('q') || '', parseInt(params.get('page') || '1', 10), false);
    });

    // Delegated handler for pagination clicks inside result container.
    document.addEventListener('click', function (e) {
      const link = e.target.closest('.pagination a');
      if (!link) return;
      // Only intercept when inside search result container (next to .product-grid).
      if (!link.closest('.search-results')) return;
      e.preventDefault();
      const params = new URLSearchParams(link.getAttribute('href').split('?')[1] || '');
      const q = params.get('q') || '';
      const page = parseInt(params.get('page') || '1', 10);
      runSearch(q, page);
    });
  }

  function runSearch(q, page, push) {
    push = push === undefined ? true : push;
    const form = document.querySelector('.search-form');
    const grid = document.querySelector('.product-grid');
    const paginationEl = document.querySelector('.search-results .pagination');
    if (!form || !grid) return;

    const fd = new FormData(form);
    fd.set('q', q);
    fd.set('page', String(page));
    fd.set('ajax', '1');

    // Show subtle loading state.
    grid.style.opacity = '0.5';

    fetch(form.getAttribute('action') || window.location.pathname, {
      method: 'POST',
      body: fd,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        grid.innerHTML = data.html || '';
        if (paginationEl) paginationEl.innerHTML = data.pagination_html || '';
        // Update URL bar (so refresh/share/back-button works).
        const qs = new URLSearchParams({ q: q, page: String(page) }).toString();
        if (push) history.pushState({}, '', '?' + qs);
        grid.style.opacity = '1';
      })
      .catch(function (err) {
        console.error('search AJAX failed', err);
        grid.style.opacity = '1';
        // Fallback: submit form normally (full reload).
        form.submit();
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
