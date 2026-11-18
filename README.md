# Heaven Essence Ice Creams — multi-page site

A self-contained local recreation of the Heaven Essence Ice Creams website,
built from the reference at
<https://project-leader-overview-703620.onhercules.app>.

> **Deployed on cPanel:** the live site uses `php-backend/` (PHP 8.5 + MySQL)
> because the hosting account has no Python 3.12+ / Node support. The Django
> `backend/` remains available for local development. See
> [`php-backend/README.md`](php-backend/README.md).

## Pages

| Route | What it is |
| --- | --- |
| `/` | Home — copied from the reference build |
| `/flavours` | Full flavour menu — copied from the reference build (filters, prices, WhatsApp ordering) |
| `/our-story` | Custom-designed story page: kitchen photo, timeline, values and stats |
| `/events` | Custom-designed events & catering page: occasion cards, packages and booking flow |
| `/gallery` | Custom-designed masonry gallery with category filters and a lightbox |
| `/visit` | Custom-designed visit/contact page with an illustrated area map and info cards |
| `/faq` | Custom-designed FAQ with an animated accordion |

All pages share the site's original fonts, colours and header/footer, default
to **light mode**, and have no third-party badge.

`assets/native-nav.js` forces nav links on the copied React pages to do a real
page load, so clicking them opens the designed pages above instead of the
reference build's "coming soon" placeholders.

## Run it

```bash
node server.js
```

Then open <http://localhost:4173>. The server gzips text assets and serves the
directories as clean routes. It also proxies `/api`, `/admin` and `/static` to
the Django backend on port 8000, so the browser only talks to one origin.

## Backend

See [`backend/README.md`](backend/README.md) for the Django REST API. Start it
alongside the frontend:

```bash
cd backend && source .venv/bin/activate && python manage.py runserver 0.0.0.0:8000
```

### Connected forms

- `/events` → `POST /api/enquiries/` — catering/events enquiry form
- `/visit` → `POST /api/orders/` — quick order form
- `/visit` → `POST /api/contact/` — contact message form

`assets/forms.js` submits them as JSON through the same-origin proxy and shows
inline success/error messages. Submissions appear in `/admin/` immediately.

## Assets

- `assets/` — original styles, JS bundles, local font CSS and `custom.css`
  (utilities used by the custom pages)
- `images/` — all flavour, hero and kitchen images
- `_hercules/font/` — Fraunces, Outfit and Caveat webfonts
