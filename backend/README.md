# Heaven Essence — Backend API

Django 6 + Django REST Framework backend for the Heaven Essence Ice Creams site.
It stores the catalogue (flavours, categories, gallery, FAQs, testimonials,
site settings) and all customer leads (orders, event enquiries, contact
messages), with a full Django admin panel for staff.

## Quick start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data         # loads all real site content
python manage.py createsuperuser   # or use the admin account below
python manage.py runserver 0.0.0.0:8000
```

A superuser was created for local development:

- **Username:** `admin`
- **Password:** `kc4qLLuiZXL135ea`

Change this before exposing the API publicly.

## API endpoints

Base URL: `http://localhost:8000`

### Public, read-only catalogue

| Method | Endpoint | Notes |
| --- | --- | --- |
| GET | `/api/catalog/categories/` | Category list with flavour counts |
| GET | `/api/catalog/flavours/` | `?category=<slug>` and `?q=<text>` filters |
| GET | `/api/catalog/flavours/grouped/` | Flavours grouped by category |
| GET | `/api/catalog/flavours/<slug>/` | Single flavour |
| GET | `/api/catalog/gallery/` | `?category=flavours\|kitchen\|scoops` |
| GET | `/api/catalog/faqs/` | Active FAQs |
| GET | `/api/catalog/testimonials/` | Active testimonials |
| GET | `/api/catalog/settings/` | Site settings (key/value) |
| GET | `/api/catalog/settings/<key>/` | One setting |

### Public, write (anyone may submit; only staff may read)

| Method | Endpoint | Notes |
| --- | --- | --- |
| POST | `/api/orders/` | Customer order — name, phone, flavour, quantity… |
| POST | `/api/enquiries/` | Event/catering enquiry — date, guests, event type… |
| POST | `/api/contact/` | Contact message |

### Staff-only (`IsAdminUser`)

| Method | Endpoint | Notes |
| --- | --- | --- |
| GET | `/api/orders/` | List/filter orders |
| PATCH | `/api/orders/<id>/status/` | Update order status |
| GET | `/api/enquiries/` | List enquiries |
| PATCH | `/api/enquiries/<id>/status/` | Update enquiry status |
| GET | `/api/contact/` | List messages |
| GET | `/api/dashboard/` | Counts for an admin dashboard |

Use Django's session login (`/admin/login/`) or a logged-in session to call
staff endpoints from a browser. Catalogue writes are disabled entirely — edit
catalogue data in the admin panel at **`/admin/`**.

## Configuration

Copy `.env.example` to `.env` and set `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
and `CORS_ORIGINS`. CORS already allows the local frontend (`localhost:4173`)
and any `*.trycloudflare.com` share link.

## Tests

```bash
python manage.py test      # 9 tests, all passing
```

## Production

Set `DEBUG=False`, a real `SECRET_KEY`, your domains in `ALLOWED_HOSTS`, then:

```bash
python manage.py collectstatic --noinput
gunicorn heaven_api.wsgi:application --bind 0.0.0.0:8000
```

For Postgres, replace the `DATABASES` block with your connection settings and
re-run migrations.
