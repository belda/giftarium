# Giftarium

> Create gift wishlists and share them with your family and friends.
> They can register for a gift — you know you might get it, but not from whom.

Self-hostable. Docker deploy in under 5 minutes.

---

## Features

- **Wishlists** — add gifts with name, description, link, and price range
- **Sharing** — share a wishlist with a group (family, friends, colleagues)
- **Anonymous reservations** — others can reserve a gift; you only see it's taken, not by whom
- **Workspaces** — separate wishlists per group, with member invitations
- **Google OAuth** — optional social login alongside email/password
- **Multi-language** — Czech and English

---

## Self-hosted quickstart (Docker)

**Requirements:** Docker + Docker Compose, a domain with HTTPS (nginx/Caddy/Traefik).

```bash
# 1. Clone and configure
git clone https://github.com/your-org/giftarium.git
cd giftarium
cp .env.example .env
```

Open `.env` and set these required values:

```env
SECRET_KEY=<random string>
ALLOWED_HOSTS=gifts.example.com
CSRF_TRUSTED_ORIGINS=https://gifts.example.com
DB_PASSWORD=<strong password>
DEFAULT_FROM_EMAIL=noreply@gifts.example.com
SECURE_SSL_REDIRECT=False   # if your reverse proxy handles HTTPS
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
# 2. Start
docker compose up -d

# 3. Create an admin account
docker compose exec web python manage.py createsuperuser
```

The app is now running on port `8000`. Point your reverse proxy at it.

> **Reverse proxy tip:** Set `SECURE_SSL_REDIRECT=False` in `.env` when nginx/Caddy/Traefik
> terminates TLS and forwards plain HTTP to gunicorn internally.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | yes | Django secret key — random string, keep it secret |
| `ALLOWED_HOSTS` | yes | Comma-separated hostnames, e.g. `gifts.example.com` |
| `CSRF_TRUSTED_ORIGINS` | yes | Comma-separated origins with scheme, e.g. `https://gifts.example.com` |
| `DB_PASSWORD` | yes | PostgreSQL password |
| `DEFAULT_FROM_EMAIL` | | Sender address for invitation and notification emails |
| `EMAIL_BACKEND` | | Set to SMTP backend + configure `EMAIL_HOST` etc. for real email |
| `SECURE_SSL_REDIRECT` | | `False` if reverse proxy handles HTTPS (default `True`) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | | Optional: enables Google OAuth login |
| `ADMIN_EMAIL` | | Admin contact for Django error emails |

See `.env.example` for the full list with comments.

---

## Local development

```bash
python -m venv .venv
source .venv/bin/activate      # or activate.fish

pip install -r requirements.txt
cp .env.example .env           # defaults work out of the box for local dev

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000. Uses SQLite and the console email backend by default.

### Docker dev (hot reload)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## Tech stack

- [Django](https://www.djangoproject.com/) + [webapptemplate](https://pypi.org/project/webapptemplate/) scaffold
- PostgreSQL (production) / SQLite (development)
- Tailwind CSS, HTMX, Alpine.js — no build step
- Gunicorn, Docker Compose
