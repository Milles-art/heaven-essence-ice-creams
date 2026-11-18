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
| GET | `/api/orders/` | List/filter orders (each can contain multiple `items`) |
| PATCH | `/api/orders/<id>/status/` | Update order status |
| GET | `/api/enquiries/` | List enquiries |
| PATCH | `/api/enquiries/<id>/status/` | Update enquiry status |
| GET | `/api/contact/` | List messages |
| PATCH | `/api/contact/<id>/read/` | Mark a message as read |
| GET | `/api/dashboard/` | Counts for an admin dashboard |

Also public: `GET /api/health/` returns `{"status":"ok"}`.

### Staff API tokens

```bash
curl -X POST http://localhost:8000/api/token/ \
  -d 'username=admin&password=<password>'
# => {"token":"..."}
curl -H 'Authorization: Token <token>' http://localhost:8000/api/orders/
```

Use Django's session login (`/admin/login/`), a logged-in session, or the token
above to call staff endpoints. Catalogue writes are disabled entirely — edit
catalogue data in the admin panel at **`/admin/`**, where each list also has a
**CSV export** action. New submissions send an email notification (console
backend in development; configure SMTP with the `EMAIL_*` env vars).

### Orders with multiple items

`POST /api/orders/` accepts either the simple fields (`flavour`, `quantity`) or
an `items` array, e.g.:

```json
{
  "customer_name": "Neema", "phone": "0712345678",
  "items": [
    {"flavour": "Vanilla", "product_type": "cup", "quantity": 2},
    {"flavour": "Mango", "product_type": "tub", "quantity": 1}
  ]
}
```

## Real contact facts

Sourced from <https://familychoiceminimarket.co.tz/> and stored as site
settings (editable in admin):

| Setting | Value |
| --- | --- |
| phone / whatsapp | `+255 768 641 810` / `255768641810` |
| email | `info@familychoiceminimarket.co.tz` |
| location | `Mafiga Shell, Morogoro, Tanzania` |
| opening hours | `Daily, 8:00 AM – 9:00 PM` |
| parent business | `Family Choice Supermarket` |
| delivery / pickup | flexible, arranged with the store / order ahead and collect |

## Configuration

Copy `.env.example` to `.env` and set `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
and `CORS_ORIGINS`. CORS already allows the local frontend (`localhost:4173`)
and any `*.trycloudflare.com` share link.

## Tests

```bash
python manage.py test      # 12 tests, all passing
```

## Production

Set `DEBUG=False`, a real `SECRET_KEY`, your domains in `ALLOWED_HOSTS`, then:

```bash
python manage.py collectstatic --noinput
gunicorn heaven_api.wsgi:application --bind 0.0.0.0:8000
```

For Postgres, replace the `DATABASES` block with your connection settings and
re-run migrations.
