# PHP backend (cPanel deployment)

This is the backend actually deployed on the cPanel account. The server has
PHP 8.5 + MySQL but no Python 3.12+ and no Node.js, so the Django backend in
`../backend/` is kept for local development only.

## Files

- `index.php` — JSON API front controller (all `/api/*` routes)
- `lib.php` — PDO database, CORS, auth, validation and mail helpers
- `config.php` — database credentials and allowed frontend origins (private)
- `database.sql` — MySQL schema + seed data (10 flavours, 19 gallery images,
  10 FAQs, 4 testimonials, 11 site settings with the real contact facts)
- `setup.php` — one-time CLI setup: imports the schema/seed and creates the admin
- `admin/index.php` — web admin panel (orders, enquiries, messages, settings, CSV export)
- `.htaccess` — routes `/api/*` to `index.php`, protects private files

## Local / cPanel setup

```bash
# Create a MySQL database and user in cPanel first, then:
cp config.php config.local.php   # edit DB credentials
php setup.php 'a-strong-admin-password'
```

`setup.php` prints the API token. Sign in at `/api/admin/`.

## API routes

| Method | Route | Access |
| --- | --- | --- |
| GET | `/api/health/` | public |
| GET | `/api/catalog/categories/`, `flavours/`, `flavours/grouped/`, `flavours/{slug}/` | public |
| GET | `/api/catalog/gallery/`, `faqs/`, `testimonials/`, `settings/` | public |
| POST | `/api/orders/`, `/api/enquiries/`, `/api/contact/` | public |
| GET | `/api/orders/`, `/api/enquiries/`, `/api/contact/`, `/api/dashboard/` | staff |
| PATCH | `/api/orders/{id}/status/`, `/api/enquiries/{id}/status/`, `/api/contact/{id}/read/` | staff |
| POST | `/api/token/` | staff (username + password → token) |

Staff requests authenticate with a cPanel session cookie or
`Authorization: Token <token>`. New submissions send an email to the address in
`config.php`. Orders support both simple fields and a multi-item `items` array.

## Live deployment

- Document root: `/home/afyabgzo/family-choice/backend/public`
- Frontend files are at that root; the PHP API is in its `api/` folder.
- Forms use a same-origin `/api` base (the `heaven-api-base` meta tag is empty).
- If the site is later moved to `heavenessence.co.tz`, point that domain's
  document root at the same folder — no path changes are needed.
