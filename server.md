# 🚀 Server Deployment Guide — Walstar Social Media Automation

> **Stack:** Django 6.0 · PostgreSQL · Gunicorn · Nginx · Cloudinary · n8n · Ubuntu 22.04 LTS

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Server Initial Setup](#2-server-initial-setup)
3. [PostgreSQL Database Setup](#3-postgresql-database-setup)
4. [Application Deployment](#4-application-deployment)
5. [Environment Variables](#5-environment-variables)
6. [Gunicorn (WSGI Server) Setup](#6-gunicorn-wsgi-server-setup)
7. [Nginx (Reverse Proxy) Setup](#7-nginx-reverse-proxy-setup)
8. [SSL / HTTPS with Certbot](#8-ssl--https-with-certbot)
9. [Static & Media Files](#9-static--media-files)
10. [Cloudinary Configuration](#10-cloudinary-configuration)
11. [Social API Tokens](#11-social-api-tokens)
12. [Systemd Service Management](#12-systemd-service-management)
13. [Firewall Configuration](#13-firewall-configuration)
14. [Production Security Checklist](#14-production-security-checklist)
15. [Updating the Application](#15-updating-the-application)
16. [Monitoring & Logs](#16-monitoring--logs)
17. [Rollback Procedure](#17-rollback-procedure)
18. [Troubleshooting](#18-troubleshooting)
19. [n8n Workflow Automation](#19-n8n-workflow-automation)

---

## 1. System Requirements

| Component    | Minimum                | Recommended            |
|-------------|------------------------|------------------------|
| OS           | Ubuntu 20.04 LTS       | Ubuntu 22.04 LTS       |
| CPU          | 1 vCPU                 | 2+ vCPUs               |
| RAM          | 1 GB                   | 2 GB+                  |
| Disk         | 20 GB SSD              | 40 GB+ SSD             |
| Python       | 3.11+                  | 3.12                   |
| PostgreSQL   | 14+                    | 16                     |
| Nginx        | 1.18+                  | Latest stable          |

---

## 2. Server Initial Setup

### 2.1 Update & Install Core Dependencies

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  python3 python3-pip python3-venv \
  postgresql postgresql-contrib \
  nginx \
  git \
  curl \
  libpq-dev \
  python3-dev \
  build-essential \
  certbot python3-certbot-nginx
```

### 2.2 Create a Dedicated System User

```bash
sudo adduser --system --group --no-create-home walstar
```

> Running the app as a non-root, non-login user is a critical security practice.

---

## 3. PostgreSQL Database Setup

```bash
sudo -u postgres psql
```

Inside the PostgreSQL shell:

```sql
-- Create the database
CREATE DATABASE walstar_db;

-- Create a dedicated user
CREATE USER walstar_user WITH PASSWORD 'your-strong-password';

-- Grant privileges
ALTER ROLE walstar_user SET client_encoding TO 'utf8';
ALTER ROLE walstar_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE walstar_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE walstar_db TO walstar_user;

\q
```

> ⚠️ **Important:** Use a strong, randomly generated password. Store it in `.env`, never hardcode it.

---

## 4. Application Deployment

### 4.1 Clone the Repository

```bash
cd /opt
sudo git clone https://github.com/<your-org>/social-media-automation.git walstar
sudo chown -R walstar:walstar /opt/walstar
```

### 4.2 Create Python Virtual Environment

```bash
cd /opt/walstar
sudo -u walstar python3 -m venv .venv
sudo -u walstar .venv/bin/pip install --upgrade pip
sudo -u walstar .venv/bin/pip install -r requirements.txt
```

### 4.3 Install Additional Production Dependencies

```bash
sudo -u walstar .venv/bin/pip install gunicorn python-dotenv
```

> `python-dotenv` is already used in `settings.py` via `load_dotenv()`. Ensure it's in `requirements.txt`.

### 4.4 Run Database Migrations

```bash
sudo -u walstar /opt/walstar/.venv/bin/python manage.py migrate
```

### 4.5 Create a Superuser

```bash
sudo -u walstar /opt/walstar/.venv/bin/python manage.py createsuperuser
```

### 4.6 Collect Static Files

```bash
sudo -u walstar /opt/walstar/.venv/bin/python manage.py collectstatic --noinput
```

---

## 5. Environment Variables

Create the `.env` file in the project root:

```bash
sudo nano /opt/walstar/.env
```

Paste and fill in the following. **All values are required in production:**

```env
# ── Django Core ──────────────────────────────────────────────────────────────
SECRET_KEY='<generate-a-50+-char-random-key>'
DEBUG='False'
ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com,<server-IP>'

# ── PostgreSQL ────────────────────────────────────────────────────────────────
DB_NAME='walstar_db'
DB_USER='walstar_user'
DB_PASSWORD='your-strong-password'
DB_HOST='localhost'
DB_PORT='5432'

# ── Cloudinary (Media Storage) ───────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME='your-cloudinary-cloud-name'
CLOUDINARY_API_KEY='your-cloudinary-api-key'
CLOUDINARY_API_SECRET='your-cloudinary-api-secret'

# ── Social Media API Tokens ───────────────────────────────────────────────────
FACEBOOK_TOKEN='your-facebook-token'
INSTAGRAM_TOKEN='your-instagram-token'
LINKEDIN_TOKEN='your-linkedin-token'

# ── Facebook Page Tokens ───────────────────────────────────────────────────────
FB_PAGE_TOKEN='your-fb-page-token'
FB_ACCESS_TOKEN_BASE='your-fb-base-access-token'
FB_ACCESS_TOKEN_COMMENTERS='your-fb-commenters-access-token'

# ── Apify (Scraping) ──────────────────────────────────────────────────────────
APIFY_TOKEN='your-apify-token'
INSTAGRAM_SESSION_COOKIE='your-instagram-session-cookie'  # Optional

# ── Razorpay (Affiliate Payouts) ──────────────────────────────────────────────
RAZORPAY_KEY_ID='your-razorpay-key-id'
RAZORPAY_KEY_SECRET='your-razorpay-key-secret'
RAZORPAYX_ACCOUNT_NUMBER='your-razorpayx-account-number'
```

Secure the file:

```bash
sudo chown walstar:walstar /opt/walstar/.env
sudo chmod 600 /opt/walstar/.env
```

### Generate a Django SECRET_KEY

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 6. Gunicorn (WSGI Server) Setup

### 6.1 Test Gunicorn Manually

```bash
cd /opt/walstar
sudo -u walstar .venv/bin/gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  walstar.wsgi:application
```

Visit `http://<server-IP>:8000` to verify. Press `Ctrl+C` to stop.

> **Worker formula:** `(2 × CPU cores) + 1`. For a 1-core server → 3 workers.

### 6.2 Create Gunicorn Systemd Socket

```bash
sudo nano /etc/systemd/system/walstar.socket
```

```ini
[Unit]
Description=Walstar Gunicorn Socket

[Socket]
ListenStream=/run/walstar.sock

[Install]
WantedBy=sockets.target
```

### 6.3 Create Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/walstar.service
```

```ini
[Unit]
Description=Walstar Gunicorn Daemon
Requires=walstar.socket
After=network.target

[Service]
User=walstar
Group=walstar
WorkingDirectory=/opt/walstar
EnvironmentFile=/opt/walstar/.env
ExecStart=/opt/walstar/.venv/bin/gunicorn \
          --access-logfile /var/log/walstar/access.log \
          --error-logfile /var/log/walstar/error.log \
          --workers 3 \
          --bind unix:/run/walstar.sock \
          walstar.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 6.4 Create Log Directory

```bash
sudo mkdir -p /var/log/walstar
sudo chown walstar:walstar /var/log/walstar
```

### 6.5 Enable & Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable walstar.socket
sudo systemctl start walstar.socket
sudo systemctl enable walstar.service
sudo systemctl start walstar.service

# Verify
sudo systemctl status walstar.service
```

---

## 7. Nginx (Reverse Proxy) Setup

### 7.1 Create Nginx Server Block

```bash
sudo nano /etc/nginx/sites-available/walstar
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Max upload size (for media/images)
    client_max_body_size 20M;

    # Static files
    location /static/ {
        alias /opt/walstar/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (local fallback — Cloudinary is the primary storage)
    location /media/ {
        alias /opt/walstar/media/;
        expires 7d;
    }

    # Proxy all other requests to Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/walstar.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }
}
```

### 7.2 Enable the Site

```bash
sudo ln -s /etc/nginx/sites-available/walstar /etc/nginx/sites-enabled/
sudo nginx -t     # Test configuration
sudo systemctl reload nginx
```

---

## 8. SSL / HTTPS with Certbot

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will:
- Obtain a Let's Encrypt certificate
- Automatically update your Nginx config with SSL settings
- Set up auto-renewal (via `systemd` timer)

### Verify Auto-Renewal

```bash
sudo certbot renew --dry-run
```

> The app's `settings.py` already enables `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` when `DEBUG=False`.

---

## 9. Static & Media Files

### 9.1 Add `STATIC_ROOT` to `settings.py`

Ensure `settings.py` has:

```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

Then run:

```bash
sudo -u walstar /opt/walstar/.venv/bin/python manage.py collectstatic --noinput
```

### 9.2 Media Files

Local media files are stored in `/opt/walstar/media/`. Since Cloudinary is configured as the primary media backend, most uploaded media is served from Cloudinary CDN — the local `/media/` directory is a fallback.

---

## 10. Cloudinary Configuration

Cloudinary is configured in `settings.py` and serves as the CDN for all user-uploaded images and post thumbnails. Ensure the following environment variables are set (see §5):

```
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
```

Verify the integration after deployment:

```bash
sudo -u walstar /opt/walstar/.venv/bin/python manage.py shell -c \
  "import cloudinary; print(cloudinary.config().cloud_name)"
```

---

## 11. Social API Tokens

The application integrates with three social platforms. Tokens must be set in `.env`:

| Platform   | Env Variable                  | Notes                                    |
|-----------|-------------------------------|------------------------------------------|
| Facebook  | `FACEBOOK_TOKEN`              | Graph API user token                     |
| Facebook  | `FB_PAGE_TOKEN`               | Page-specific access token               |
| Facebook  | `FB_ACCESS_TOKEN_BASE`        | Base token for commenters flow           |
| Facebook  | `FB_ACCESS_TOKEN_COMMENTERS`  | Commenter targeting token                |
| Instagram | `INSTAGRAM_TOKEN`             | Instagram Graph API token                |
| Instagram | `INSTAGRAM_SESSION_COOKIE`    | Optional — for Apify scraping sessions   |
| LinkedIn  | `LINKEDIN_TOKEN`              | LinkedIn OAuth token                     |

> ⚠️ **Token Expiry:** Facebook/Instagram long-lived tokens expire after ~60 days. Implement a token refresh cron job or webhook to avoid posting failures.

---

## 12. Systemd Service Management

| Action                | Command                                         |
|-----------------------|-------------------------------------------------|
| Start service         | `sudo systemctl start walstar`                  |
| Stop service          | `sudo systemctl stop walstar`                   |
| Restart service       | `sudo systemctl restart walstar`                |
| Reload (no downtime)  | `sudo systemctl reload walstar`                 |
| Check status          | `sudo systemctl status walstar`                 |
| View logs             | `sudo journalctl -u walstar -f`                 |
| Enable on boot        | `sudo systemctl enable walstar`                 |
| Nginx restart         | `sudo systemctl restart nginx`                  |

---

## 13. Firewall Configuration

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'   # Opens ports 80 and 443
sudo ufw enable
sudo ufw status
```

> **Do NOT expose port 8000** (Gunicorn) directly — traffic must flow through Nginx only.

---

## 14. Production Security Checklist

- [ ] `DEBUG=False` in `.env`
- [ ] `SECRET_KEY` is 50+ random characters, not the Django default
- [ ] `ALLOWED_HOSTS` contains only your domain(s)
- [ ] `.env` file has `chmod 600` permissions
- [ ] SSL certificate installed (Certbot / Let's Encrypt)
- [ ] `SECURE_SSL_REDIRECT = True` *(auto-enabled when DEBUG=False)*
- [ ] `SESSION_COOKIE_SECURE = True` *(auto-enabled)*
- [ ] `CSRF_COOKIE_SECURE = True` *(auto-enabled)*
- [ ] PostgreSQL not exposed publicly (only `localhost`)
- [ ] Gunicorn socket (Unix socket), not TCP port
- [ ] Firewall enabled (UFW) — only ports 22, 80, 443 open
- [ ] Django Admin URL changed from `/admin/` to something custom
- [ ] Regular database backups configured
- [ ] Social API tokens rotated periodically
- [ ] n8n protected behind Nginx auth or subdomain SSL
- [ ] n8n `N8N_BASIC_AUTH_ACTIVE=true` with strong credentials set
- [ ] n8n data directory backed up regularly (`~/.n8n/`)

---

## 15. Updating the Application

```bash
cd /opt/walstar

# 1. Pull latest code
sudo -u walstar git pull origin main

# 2. Install any new dependencies
sudo -u walstar .venv/bin/pip install -r requirements.txt

# 3. Run new migrations
sudo -u walstar .venv/bin/python manage.py migrate

# 4. Collect static files
sudo -u walstar .venv/bin/python manage.py collectstatic --noinput

# 5. Restart Gunicorn
sudo systemctl restart walstar

# 6. Reload Nginx (if config changed)
sudo nginx -t && sudo systemctl reload nginx
```

---

## 16. Monitoring & Logs

### Application Logs

```bash
# Live Gunicorn access log
tail -f /var/log/walstar/access.log

# Live Gunicorn error log
tail -f /var/log/walstar/error.log

# Systemd journal
sudo journalctl -u walstar -f --since "1 hour ago"
```

### Nginx Logs

```bash
# Access log
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log
```

### Database Monitoring

```bash
sudo -u postgres psql -d walstar_db -c "SELECT count(*) FROM django_session;"
```

### Setting Up Log Rotation

```bash
sudo nano /etc/logrotate.d/walstar
```

```
/var/log/walstar/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 walstar walstar
    sharedscripts
    postrotate
        systemctl reload walstar > /dev/null 2>&1 || true
    endscript
}
```

---

## 17. Rollback Procedure

### Code Rollback

```bash
cd /opt/walstar

# Find the last working commit
sudo -u walstar git log --oneline -10

# Roll back to a specific commit
sudo -u walstar git checkout <commit-hash>

# Restart services
sudo systemctl restart walstar
```

### Database Rollback (Migration)

```bash
# List migrations for the social app
sudo -u walstar .venv/bin/python manage.py showmigrations social

# Roll back to a specific migration
sudo -u walstar .venv/bin/python manage.py migrate social <migration_name>
```

### Database Backup & Restore

```bash
# Create a backup before any major update
sudo -u postgres pg_dump walstar_db > /opt/backups/walstar_$(date +%Y%m%d_%H%M%S).sql

# Restore from a backup
sudo -u postgres psql walstar_db < /opt/backups/walstar_YYYYMMDD_HHMMSS.sql
```

---

## 18. Troubleshooting

### ❌ 502 Bad Gateway

Gunicorn is not running or the Unix socket path is wrong.

```bash
sudo systemctl status walstar
sudo ls -la /run/walstar.sock     # Socket must exist
sudo journalctl -u walstar -n 50
```

### ❌ 500 Internal Server Error

Check Django app logs:

```bash
tail -100 /var/log/walstar/error.log
```

Common causes:
- Missing environment variable (e.g., `SECRET_KEY` not set)
- Database not running or wrong credentials
- Missing `python-dotenv` in `.venv`
- `STATIC_ROOT` not set / `collectstatic` not run

### ❌ Static Files Not Loading (404)

```bash
# Verify collectstatic ran
ls /opt/walstar/staticfiles/

# Verify Nginx alias points to correct path
sudo nginx -t
```

### ❌ Database Connection Refused

```bash
sudo systemctl status postgresql
sudo -u postgres psql -d walstar_db   # Test connection
```

### ❌ Permission Denied on `.sock` File

```bash
sudo chown walstar:www-data /run/walstar.sock
sudo chmod 660 /run/walstar.sock
```

Add `www-data` user to the `walstar` group:

```bash
sudo usermod -aG walstar www-data
sudo systemctl restart nginx walstar
```

### ❌ Cloudinary Images Not Displaying

- Verify `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` are correct in `.env`
- Check that the `walstar` system user can read `/opt/walstar/.env`
- Run: `sudo -u walstar /opt/walstar/.venv/bin/python manage.py shell -c "import cloudinary; print(cloudinary.config().cloud_name)"`

---

## 19. n8n Workflow Automation

n8n is a self-hostable workflow automation tool used to orchestrate social media posting schedules, webhook triggers, and multi-step API automations alongside the Django app.

### 19.1 Install Node.js (Required)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version   # Should be v20+
npm --version
```

### 19.2 Install n8n Globally

```bash
sudo npm install -g n8n
```

### 19.3 Create a Dedicated n8n User

```bash
sudo adduser --system --group --home /opt/n8n n8n
```

### 19.4 Create n8n Environment File

```bash
sudo nano /opt/n8n/.env
```

Paste the following (fill in all values):

```env
# ── n8n Core ──────────────────────────────────────────────────────────────────
N8N_HOST=n8n.yourdomain.com
N8N_PORT=5678
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n.yourdomain.com/

# ── Basic Auth (simple protection) ───────────────────────────────────────────
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-strong-n8n-password

# ── Data Storage ──────────────────────────────────────────────────────────────
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n_db
DB_POSTGRESDB_USER=n8n_user
DB_POSTGRESDB_PASSWORD=your-n8n-db-password
DB_POSTGRESDB_SCHEMA=public

# ── Security ──────────────────────────────────────────────────────────────────
N8N_ENCRYPTION_KEY=your-32-char-random-encryption-key

# ── Timezone ──────────────────────────────────────────────────────────────────
GENERIC_TIMEZONE=Asia/Kolkata
TZ=Asia/Kolkata

# ── Logging ───────────────────────────────────────────────────────────────────
N8N_LOG_LEVEL=info
N8N_LOG_OUTPUT=file
N8N_LOG_FILE_LOCATION=/var/log/n8n/n8n.log
```

Secure it:

```bash
sudo chown n8n:n8n /opt/n8n/.env
sudo chmod 600 /opt/n8n/.env
```

> Generate `N8N_ENCRYPTION_KEY` with: `openssl rand -hex 16`

### 19.5 Create the n8n PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE n8n_db;
CREATE USER n8n_user WITH PASSWORD 'your-n8n-db-password';
GRANT ALL PRIVILEGES ON DATABASE n8n_db TO n8n_user;
\q
```

### 19.6 Create Log Directory

```bash
sudo mkdir -p /var/log/n8n
sudo chown n8n:n8n /var/log/n8n
```

### 19.7 Create n8n Systemd Service

```bash
sudo nano /etc/systemd/system/n8n.service
```

```ini
[Unit]
Description=n8n Workflow Automation
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=n8n
Group=n8n
WorkingDirectory=/opt/n8n
EnvironmentFile=/opt/n8n/.env
ExecStart=/usr/bin/n8n start
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/log/n8n/n8n.log
StandardError=append:/var/log/n8n/n8n-error.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable n8n
sudo systemctl start n8n
sudo systemctl status n8n
```

### 19.8 Nginx Configuration for n8n

n8n runs on port `5678`. Expose it via a **subdomain** (recommended) or a subpath.

#### Option A — Subdomain (Recommended): `n8n.yourdomain.com`

```bash
sudo nano /etc/nginx/sites-available/n8n
```

```nginx
server {
    listen 80;
    server_name n8n.yourdomain.com;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_send_timeout 300;
        chunked_transfer_encoding on;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Issue SSL certificate for n8n subdomain
sudo certbot --nginx -d n8n.yourdomain.com
```

#### Option B — Subpath: `yourdomain.com/n8n/`

Add this block inside the existing `walstar` Nginx server block:

```nginx
location /n8n/ {
    proxy_pass http://localhost:5678/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300;
    rewrite ^/n8n/(.*) /$1 break;
}
```

> ⚠️ **Note:** If using the subpath approach, also set `N8N_PATH=/n8n/` in `/opt/n8n/.env` and restart n8n.

### 19.9 Allow n8n Port in Firewall (Internal Only)

```bash
# n8n should NOT be exposed publicly — Nginx proxies it
# Only allow Nginx Full (80/443) through UFW
# If you need direct testing access temporarily:
sudo ufw allow from <your-IP> to any port 5678
```

### 19.10 Integrating n8n with the Django App

n8n communicates with your Django app via HTTP webhooks and API calls.

#### Django → n8n (Triggering Workflows)

From your Django views, trigger an n8n webhook to start automation:

```python
import requests

def trigger_n8n_post_workflow(post_data):
    n8n_webhook_url = "https://n8n.yourdomain.com/webhook/social-post-trigger"
    response = requests.post(n8n_webhook_url, json=post_data, timeout=10)
    return response.status_code == 200
```

#### n8n → Django (Calling Django APIs)

In n8n workflows, use the **HTTP Request** node to call your Django REST API endpoints:

```
Method: POST
URL: https://yourdomain.com/social/api/post/schedule/
Headers:
  Content-Type: application/json
  Authorization: Token <django-api-token>
Body: { "post_id": "{{ $json.post_id }}", "platform": "{{ $json.platform }}" }
```

#### Recommended n8n Workflows for This Project

| Workflow | Trigger | Actions |
|---|---|---|
| **Scheduled Post Publisher** | Cron (every 15min) | Call Django API → Post to FB/Instagram/LinkedIn |
| **Affiliate Payout Notifier** | Django webhook → payout approved | Send email via Brevo → Notify via WhatsApp/Telegram |
| **Token Refresh Reminder** | Cron (every 55 days) | Send alert email when social tokens near expiry |
| **New Post Alert** | Django webhook → post published | Notify admin → Log to Google Sheets |

### 19.11 Backing Up n8n

n8n stores all workflows and credentials in the `n8n_db` PostgreSQL database (since we configured `DB_TYPE=postgresdb`).

```bash
# Backup n8n PostgreSQL DB
sudo -u postgres pg_dump n8n_db > /opt/backups/n8n_$(date +%Y%m%d_%H%M%S).sql

# Also export workflows from n8n UI:
# Settings → Import/Export → Export all workflows as JSON
```

### 19.12 Updating n8n

```bash
# Stop n8n
sudo systemctl stop n8n

# Update globally
sudo npm update -g n8n

# Start n8n
sudo systemctl start n8n
sudo systemctl status n8n
```

### Systemd Management for n8n

| Action           | Command                                  |
|-----------------|------------------------------------------|
| Start n8n        | `sudo systemctl start n8n`              |
| Stop n8n         | `sudo systemctl stop n8n`               |
| Restart n8n      | `sudo systemctl restart n8n`            |
| Check status     | `sudo systemctl status n8n`             |
| View live logs   | `sudo journalctl -u n8n -f`             |
| View log file    | `tail -f /var/log/n8n/n8n.log`          |

---

## Quick Reference Commands

```bash
# Full restart of all services (Django + n8n + Nginx + DB)
sudo systemctl restart postgresql walstar n8n nginx

# Check all service statuses at once
sudo systemctl status postgresql walstar n8n nginx

# Run Django management commands
sudo -u walstar /opt/walstar/.venv/bin/python /opt/walstar/manage.py <command>

# Open Django shell
sudo -u walstar /opt/walstar/.venv/bin/python /opt/walstar/manage.py shell

# n8n — view current version
n8n --version

# n8n — run interactively for testing (not for production)
n8n start
```

---

*Last updated: March 2026 — Walstar Social Media Automation Platform*
