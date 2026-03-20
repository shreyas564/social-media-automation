# 💻 Local Development Setup — Walstar Social Media Automation

> **Stack:** Django 6.0 · PostgreSQL · Python 3.12 · n8n · Windows / macOS / Linux

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone the Repository](#2-clone-the-repository)
3. [Python Virtual Environment](#3-python-virtual-environment)
4. [PostgreSQL Local Setup](#4-postgresql-local-setup)
5. [Environment Variables (.env)](#5-environment-variables-env)
6. [Database Migrations](#6-database-migrations)
7. [Run the Development Server](#7-run-the-development-server)
8. [n8n Local Setup](#8-n8n-local-setup)
9. [Media & Static Files](#9-media--static-files)
10. [Testing Social API Integrations Locally](#10-testing-social-api-integrations-locally)
11. [Useful Django Management Commands](#11-useful-django-management-commands)
12. [Common Local Issues](#12-common-local-issues)

---

## 1. Prerequisites

Install the following before starting:

| Tool | Version | Download |
|---|---|---|
| Python | 3.11 or 3.12 | [python.org](https://python.org) |
| Git | Latest | [git-scm.com](https://git-scm.com) |
| PostgreSQL | 14+ | [postgresql.org](https://www.postgresql.org/download/) |
| Node.js | 20+ *(for n8n)* | [nodejs.org](https://nodejs.org) |
| VS Code *(optional)* | Latest | [code.visualstudio.com](https://code.visualstudio.com) |

### Windows-specific: Install Make tools (optional)

```powershell
# Chocolatey (run as Administrator)
choco install make
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/<your-org>/social-media-automation.git
cd social-media-automation
```

---

## 3. Python Virtual Environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

# If Activate.ps1 is blocked by execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install python-dotenv        # ensure it's installed
```

---

## 4. PostgreSQL Local Setup

### Windows — Using pgAdmin or psql

Open **pgAdmin** or the **SQL Shell (psql)** and run:

```sql
CREATE DATABASE walstar_local;
CREATE USER walstar_user WITH PASSWORD 'localpassword';
GRANT ALL PRIVILEGES ON DATABASE walstar_local TO walstar_user;
\q
```

### macOS (Homebrew)

```bash
brew install postgresql@16
brew services start postgresql@16
psql postgres
```

Then run the same SQL above inside `psql`.

### Linux

```bash
sudo -u postgres psql
```

Then run the same SQL above.

---

## 5. Environment Variables (.env)

The project uses `python-dotenv`. Copy the example file and fill in your local values:

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` with your local configuration:

```env
# ── Django Core ───────────────────────────────────────────────────────────────
SECRET_KEY='any-random-string-for-local-dev-only'
DEBUG='True'
ALLOWED_HOSTS='localhost,127.0.0.1'

# ── PostgreSQL (local) ────────────────────────────────────────────────────────
DB_NAME='walstar_local'
DB_USER='walstar_user'
DB_PASSWORD='localpassword'
DB_HOST='localhost'
DB_PORT='5432'

# ── Cloudinary ────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME='your-cloudinary-cloud-name'
CLOUDINARY_API_KEY='your-cloudinary-api-key'
CLOUDINARY_API_SECRET='your-cloudinary-api-secret'

# ── Social Media API Tokens ───────────────────────────────────────────────────
FACEBOOK_TOKEN='your-facebook-token'
INSTAGRAM_TOKEN='your-instagram-token'
LINKEDIN_TOKEN='your-linkedin-token'

# ── Facebook Page Tokens ──────────────────────────────────────────────────────
FB_PAGE_TOKEN='your-fb-page-token'
FB_ACCESS_TOKEN_BASE='your-fb-base-access-token'
FB_ACCESS_TOKEN_COMMENTERS='your-fb-commenters-access-token'

# ── Apify ─────────────────────────────────────────────────────────────────────
APIFY_TOKEN='your-apify-token'
INSTAGRAM_SESSION_COOKIE=''   # Optional

# ── Razorpay ──────────────────────────────────────────────────────────────────
RAZORPAY_KEY_ID='your-test-razorpay-key-id'
RAZORPAY_KEY_SECRET='your-test-razorpay-secret'
RAZORPAYX_ACCOUNT_NUMBER='your-razorpayx-account'
```

> 💡 **Tip:** For Razorpay locally, use the **test mode** keys from your [Razorpay Dashboard](https://dashboard.razorpay.com) — test keys start with `rzp_test_`.

---

## 6. Database Migrations

```bash
# Apply all migrations
python manage.py migrate

# Create your local superuser (for admin access)
python manage.py createsuperuser
```

---

## 7. Run the Development Server

```bash
python manage.py runserver
```

Open your browser at: **[http://127.0.0.1:8000/social/](http://127.0.0.1:8000/social/)**

Django Admin: **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)**

> 💡 Run on a different port: `python manage.py runserver 8080`

### Run on Local Network (accessible from phone/other device)

```bash
python manage.py runserver 0.0.0.0:8000
```

Then visit `http://<your-local-IP>:8000/social/` from any device on the same Wi-Fi.

---

## 8. n8n Local Setup

### 8.1 Install n8n

```bash
npm install -g n8n
```

### 8.2 Run n8n Locally (SQLite mode — no setup needed)

```bash
n8n start
```

n8n will be available at: **[http://localhost:5678](http://localhost:5678)**

On first launch, you'll be prompted to create an owner account.

### 8.3 Expose Local n8n to the Internet (for Webhooks)

Facebook/Instagram webhooks require a public HTTPS URL. Use **ngrok** to tunnel your local n8n:

```bash
# Install ngrok
npm install -g ngrok   # or download from https://ngrok.com

# Expose n8n
ngrok http 5678
```

Copy the generated `https://xxxxx.ngrok-free.app` URL and use it as your `WEBHOOK_URL` in n8n settings or in Facebook App webhook configuration.

### 8.4 Expose Django Locally (for Social API Callbacks)

```bash
# In a separate terminal
ngrok http 8000
```

Use the ngrok HTTPS URL as your Django callback URL in the Facebook Developer App settings.

### 8.5 Connect n8n to Local Django

In any n8n **HTTP Request** node, set the URL to:

```
http://localhost:8000/social/api/<your-endpoint>/
```

Or use your ngrok URL if testing webhooks from external services.

---

## 9. Media & Static Files

In development (`DEBUG=True`), Django automatically serves media and static files — no Nginx needed.

Media uploads are stored in the `media/` folder in the project root.

```bash
# Collect static files (only needed if testing production-like static serving)
python manage.py collectstatic
```

---

## 10. Testing Social API Integrations Locally

### Facebook / Instagram

Facebook Graph API requires a **public HTTPS callback URL** for webhooks. Use ngrok (§8.3).

1. Go to [Facebook Developer Console](https://developers.facebook.com)
2. Under your App → Webhooks, set the callback URL to your ngrok Django URL:
   `https://xxxxx.ngrok-free.app/social/webhook/facebook/`
3. Use a **test page** for posting to avoid affecting real pages.

### LinkedIn

LinkedIn OAuth requires a registered callback URL. For local dev, add `http://localhost:8000/social/linkedin/callback/` to your LinkedIn App's Authorized Redirect URLs.

### Razorpay / RazorpayX

Use **test mode keys** from the Razorpay dashboard. Payouts will be simulated and won't transfer real money.

---

## 11. Useful Django Management Commands

```bash
# Check for any configuration issues
python manage.py check

# List all registered URL patterns
python manage.py show_urls        # requires django-extensions

# Open the Django ORM shell
python manage.py shell

# Create a new database migration after model changes
python manage.py makemigrations

# Apply pending migrations
python manage.py migrate

# Roll back last migration
python manage.py migrate social <previous_migration_name>

# Show migration history for 'social' app
python manage.py showmigrations social

# Dump data to a fixture (for seeding local DB)
python manage.py dumpdata social --indent 2 > fixtures/social_data.json

# Load a fixture into local DB
python manage.py loaddata fixtures/social_data.json

# Clear all sessions
python manage.py clearsessions
```

---

## 12. Common Local Issues

### ❌ `django.db.utils.OperationalError: could not connect to server`

PostgreSQL is not running.

```bash
# Windows — Start from Services or:
pg_ctl start -D "C:\Program Files\PostgreSQL\16\data"

# macOS (Homebrew)
brew services start postgresql@16

# Linux
sudo systemctl start postgresql
```

### ❌ `ModuleNotFoundError: No module named 'dotenv'`

```bash
pip install python-dotenv
```

### ❌ `.venv\Scripts\Activate.ps1 cannot be loaded — execution policy`

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ `ImproperlyConfigured: settings.DATABASES is improperly configured` 

Your `.env` is missing or `DB_*` variables are not set. Make sure `.env` exists in the project root and variables are correctly filled.

### ❌ `cloudinary.exceptions.AuthorizationRequired`

Your Cloudinary credentials in `.env` are wrong or empty. Double-check `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.

### ❌ `Port 8000 is already in use`

```bash
# Windows PowerShell
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS / Linux
lsof -ti:8000 | xargs kill -9
```

### ❌ `n8n: command not found`

Node.js global bin is not in your PATH. Fix:

```bash
# Find npm global bin path
npm config get prefix

# Add to PATH (macOS/Linux — add to ~/.bashrc or ~/.zshrc)
export PATH="$(npm config get prefix)/bin:$PATH"

# Windows: Add the npm global bin folder to System Environment Variables > Path
```

---

## Quick Start (TL;DR)

```bash
# 1. Clone
git clone https://github.com/<your-org>/social-media-automation.git
cd social-media-automation

# 2. Setup virtualenv & install dependencies
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt

# 3. Setup .env
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux
# (edit .env with your local DB and API keys)

# 4. Migrate & create admin
python manage.py migrate
python manage.py createsuperuser

# 5. Run
python manage.py runserver

# 6. (Optional) Run n8n in a separate terminal
n8n start
```

---

*Last updated: March 2026 — Walstar Social Media Automation Platform*
