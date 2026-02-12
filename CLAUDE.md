# CLAUDE.md — template-engine

## Project Overview

A Django-based template engine for managing and merging plain-text mail templates with dynamic `{{variable}}` placeholders. Users can create, edit, delete templates and fill in variables via a live-preview merge view.

## Repository Structure

```
template-engine/
├── CLAUDE.md                # AI assistant guidelines (this file)
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .gitignore
├── config/                  # Django project settings
│   ├── settings.py          # Main config (SIGNUP_ENABLED toggle here)
│   ├── urls.py              # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
├── templates_app/           # Main application
│   ├── models.py            # MasterTemplate, Variable, TemplateVariable
│   ├── views.py             # Auth + CRUD + Merge API views
│   ├── forms.py             # SignUpForm, MasterTemplateForm
│   ├── urls.py              # App-level URL routing
│   ├── admin.py             # Django admin registration
│   └── tests.py             # 16 tests covering models, auth, CRUD, API
├── templates/               # Django HTML templates
│   ├── base.html            # Base layout with navbar
│   ├── landing.html         # Landing page
│   ├── registration/        # Login & signup forms
│   └── templates_app/       # Template CRUD & merge views
└── static/
    └── css/style.css        # Application styles
```

## Database Schema

| Table | Purpose |
|-------|---------|
| `MasterTemplate` | Stores template name, subject, body (with `{{var}}` placeholders) |
| `Variable` | Stores unique variable names |
| `TemplateVariable` | Join table linking templates to their variables |

## Development Workflow

### Getting Started

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin access
python manage.py runserver
```

### Running Tests

```bash
python manage.py test templates_app -v2
```

### Key Settings

- **`SIGNUP_ENABLED`** in `config/settings.py` — set to `False` to disable user registration
- SQLite database at `db.sqlite3`
- Language: `de-de`, Timezone: `Europe/Berlin`

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable release branch |
| `claude/*` | AI-assisted development branches |

## Conventions

- Keep commits small and focused with clear messages.
- Write tests for new functionality.
- Run `python manage.py test templates_app` before committing.
- Update this file as the project structure evolves.

## Notes for AI Assistants

- Before making changes, read relevant files to understand existing code.
- Always run tests before committing.
- The `{{variable}}` syntax in templates uses **double curly braces** — do not confuse with Django's own template syntax.
- Variables are auto-synced from template content via `MasterTemplate.sync_variables()`.
