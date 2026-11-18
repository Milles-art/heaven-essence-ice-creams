# Deploying on cPanel (SSH)

The site is split into two parts:

1. **Frontend** — static HTML/CSS/JS. Upload to the domain's `public_html`.
2. **API** — Django app. Run it as a cPanel **Python App**, ideally on a
   subdomain such as `api.yourdomain.com`.

Both are already configured for this layout: forms read the API address from a
`<meta name="heaven-api-base">` tag, and Django allows the frontend origin via
`CORS_ORIGINS` / `CSRF_TRUSTED_ORIGINS`.

---

## 1. DNS / cPanel setup

- Point `yourdomain.com` (or a subdomain) at the cPanel account.
- In cPanel, create a subdomain **api.yourdomain.com**. Its document root will
  be something like `/home/USER/public_html/api` or
  `/home/USER/api.yourdomain.com` — note the path cPanel shows you.

## 2. Frontend (main domain)

Upload everything **except** `backend/`, `.git/`, `node_modules/` and
`server.js` into `public_html`. You can do this over SSH:

```bash
cd "/home/millen/Documents/Default Project/heaven-essence-ice-creams"
scp -r index.html flavours our-story events gallery visit faq assets images \
    _hercules favicon.ico USER@YOUR_SERVER:~/public_html/
```

Then set the API address in every page (run this on the server):

```bash
cd ~/public_html
bash set-api-base.sh https://api.yourdomain.com
```

That rewrites `content=""` in the meta tag to your API subdomain. Leave it
empty if the API ends up on the same domain.

Copy `deploy/cpanel/htaccess.example` to `public_html/.htaccess` if you want
pretty URLs and basic hardening. Apache will serve `/our-story` from the
`our-story/index.html` automatically.

## 3. API (cPanel Python App)

In cPanel → **Software → Setup Python App**:

- Python version: **3.11+** (the app is developed on 3.14; 3.11 works)
- App root: the `backend/` folder you uploaded, e.g. `~/api.yourdomain.com/backend`
- App URL: `api.yourdomain.com`
- Entry point: `heaven_api.wsgi:application`
- It creates a virtualenv; SSH into it and install dependencies:

```bash
cd ~/api.yourdomain.com/backend
source virtualenv/bin/activate      # path cPanel shows in the app screen
pip install -r requirements.txt
```

Create `~/.env_cpanel` (or set these in cPanel's Environment Variables UI):

```bash
SECRET_KEY=<generate-a-long-random-string>
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourhost.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=<password>
EMAIL_USE_TLS=True
EMAIL_TO=info@familychoiceminimarket.co.tz
```

Load them in cPanel's app environment, then prepare the database:

```bash
export $(grep -v '^#' ~/.env_cpanel | xargs)     # if using a file
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Restart the Python App from the cPanel UI. Verify:

```
https://api.yourdomain.com/api/health/     -> {"status":"ok"}
https://api.yourdomain.com/admin/login/    -> admin login
```

## 4. Go live

Open `https://yourdomain.com`, submit a test enquiry/order from `/events` and
`/visit`, and confirm it appears in `https://api.yourdomain.com/admin/`.

## Notes

- SQLite is used by default. For busier traffic, switch `DATABASES` to MySQL
  (cPanel usually provides it) and re-run migrations.
- Never commit `.env` or `db.sqlite3` — both are gitignored.
- To update later: `git pull`, then re-run `set-api-base.sh` on the frontend and
  `migrate` / `collectstatic` for the API.
