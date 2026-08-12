# Project Memory

## Quick Tasks
- [260804-10g: bỏ /admin prefix + nav](.planning/quick/260804-10g-b-ti-n-t-admin-kh-i-c-c-route-admin-admi/) — admin routes at `/products`,`/orders`,`/stats`; shared `_admin_nav.html` partial + `admin/base.html` header; logout POST+csrf. Manual browser UAT pending (login page renders no admin nav).
- [260804-2iv: header layout + hamburger](.planning/quick/260804-2iv-ch-nh-layout-header-b-n-t-qu-n-l-h-ng-ch/) — dropped brand, nav left of search; pure-CSS checkbox hamburger for mobile (zero JS).
- [260804-301: paste images Ctrl+V](.planning/quick/260804-301-cho-ph-p-ctrl-v-paste-nh-clipboard-tr-c-/) — extracted gallery JS to `app/static/js/form-gallery.js`; paste handler feeds clipboard image/* into the existing `gallery-file` input + `change` dispatch (same upload flow); server magic-byte gate intact.

## Pre-existing working-tree changes (NOT created by these tasks — left untouched)
- `README.md`, `app/admin.py`, `app/auth.py` (M) and `app/templates/admin/dashboard.html` (D).
- `use_worktrees=false` set in `.planning/config.json` for quick tasks (working tree has uncommitted changes that would be lost in a worktree).
