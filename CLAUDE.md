# CLAUDE.md — Giftarium

A simple app for creating gift wishlists and sharing them with different groups (family/friends). Your close ones can then register for a gift. You know you might get it at some point, but you dont know from who.

This project is built on **webapptemplate**, a reusable Django SaaS scaffold.

## Running the project

```bash
# Create virtualenv
python -m venv .venv
source .venv/bin/activate  # or .venv/bin/activate.fish

pip install -r requirements.txt
cp .env.example .env  # fill in SECRET_KEY etc.

# Dev server (uses config/settings/development.py by default)
python manage.py migrate
python manage.py runserver

# Run checks
python manage.py check
```

## Settings

| File | Purpose |
|------|---------|
| `config/settings/base.py` | Shared settings; imports `webapptemplate.default_settings` |
| `config/settings/development.py` | Local dev overrides |
| `config/settings/production.py` | Production / Docker |

Key project settings in `config/settings/base.py`:
- `APP_NAME = "Giftarium"` — displayed in sidebar and emails
- `ALLOWED_HOSTS` — loaded from `.env`

## Infrastructure
- SQLite database (`db.sqlite3` in project root)
- Docker Compose files for local dev and production

## App layout

```
apps/
  <your apps here>
config/
  settings/
  urls.py       # extends webapptemplate.urls — no manual URL registration needed
templates/      # project-level template overrides (rarely needed)
static/
```

## Adding a new feature app

```bash
python manage.py startapp myfeature apps/myfeature
```

In `apps/myfeature/apps.py`:

```python
from webapptemplate.app_config import WebAppConfig

class MyFeatureConfig(WebAppConfig):
    name = "apps.myfeature"
    url_prefix = "myfeature/"       # auto-includes apps/myfeature/urls.py
    nav_items = [
        {"url": "myfeature:index", "label": "My Feature", "icon": "cog", "order": 20},
    ]
    # Optional — auto-registers a Ninja router at /api/v1/myfeature/
    # api_router_module = "apps.myfeature.api"
    # api_router_prefix = "/myfeature/"
```

Then add `"apps.myfeature"` to `INSTALLED_APPS` in `config/settings/base.py`.
No changes to `config/urls.py` or templates required.

## What webapptemplate provides

- Custom `User` model with email login (no username), avatar, `current_workspace`
- Multi-tenant **Workspace** system with `Membership` (owner/admin/member) and email **Invitations**
- Google OAuth via django-allauth
- Email verification gate (`REQUIRE_EMAIL_VERIFICATION`)
- Django Ninja REST API at `/api/v1/` with session + API key auth
- Sidebar layout with Alpine.js workspace switcher and HTMX partials
- Tailwind CSS, HTMX 2, Alpine.js 3, Font Awesome 6 (all CDN — no build step)

## Production domain

`darky.blda.cz` — update `CSRF_TRUSTED_ORIGINS` in `config/settings/production.py` if this changes.
