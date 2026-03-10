# 🌟 Walstar — Social Media Automation Platform

> A full-stack Django platform that lets a **Super Admin** publish posts across Facebook, Instagram, and LinkedIn, and pays **Affiliates** for engaging with those posts through a verified rewards system.

---

## ✨ Features

### 👑 Super Admin
- **Multi-platform Publishing** — Create and publish image/video posts to Facebook, Instagram, and LinkedIn simultaneously
- **Post Analytics** — Real-time stats (likes, comments, shares) synced per platform from the APIs
- **Affiliate Management** — View, manage, and verify all registered affiliate users
- **Payment Settings** — Configure per-action payouts (like / comment / share) per platform
- **Withdrawal Management** — Approve or reject affiliate withdrawal requests with RazorpayX auto-payout
- **Verification Dashboard** — Trigger Apify scraping to verify affiliate engagement activity
- **Admin Notifications** — Real-time bell notifications for new withdrawal requests

### 🤝 Affiliate Portal
- **Feed Dashboard** — Browse all posts and engage (like, comment, share) across linked social platforms
- **Reward Tracking** — See earnings per action, per platform in real time
- **Wallet & Withdrawal** — Request payouts above the configured minimum withdrawal threshold
- **Payment History** — Full ledger of all past payouts with payment IDs
- **Profile Management** — Update social usernames, UPI/bank details, and change password

### 🔍 Engagement Verification
- **Apify Integration** — Automatically scrapes Instagram, Facebook, and LinkedIn to verify claimed engagements
- **Audit Trail** — Every verified action stores the Apify run ID, method, and timestamp
- **Screenshot / Manual fallback** — Manual verification method for edge cases

### ⚙️ Automation
- **n8n Integration** — Webhook endpoint (`/social/upload-image/`) for n8n-triggered post workflows
- **LinkedIn OAuth** — Full OAuth 2.0 flow for LinkedIn token management
- **Cloudinary CDN** — All uploaded media stored and served via Cloudinary

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6.0, Django REST Framework |
| **Database** | PostgreSQL 14+ |
| **Media Storage** | Cloudinary |
| **Payments** | Razorpay / RazorpayX |
| **Email** | Brevo (Transactional Email API) |
| **Automation** | n8n (self-hosted) |
| **Social APIs** | Facebook Graph API, Instagram Graph API, LinkedIn API |
| **Scraping** | Apify |
| **Server** | Gunicorn + Nginx (production) |
| **Auth** | Django sessions + custom OTP flow |

---

## 📁 Project Structure

```
social-media-automation/
├── walstar/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── social/                    # Main application
│   ├── models.py              # All database models
│   ├── views.py               # All view logic (~3,000+ lines)
│   ├── urls.py                # URL routing (super admin + affiliate)
│   ├── templates/             # HTML templates (Jinja-style Django)
│   ├── context_processors.py  # Global template context (notifications, settings)
│   └── migrations/            # Database migrations
├── utils/                     # Shared utilities
├── media/                     # Local media uploads (fallback)
├── requirements.txt
├── .env.example               # Environment variable example file 
---

## 🗃️ Data Models

| Model | Description |
|---|---|
| `SuperAdmin` | Extends Django `User`; stores platform tokens, currency, min withdrawal |
| `Post` | Multi-platform post with media, captions, and per-platform post IDs & stats |
| `AffiliateProfile` | Affiliate user with per-platform usernames and hashed secret |
| `Comment` / `Like` / `Share` | Engagement records with verification status and Apify audit trail |
| `ScrapedPost` / `ScrapedLike` / `ScrapedComment` | Raw Apify scrape results for verification |
| `PaymentSetting` | Per-platform, per-action payout amount configured by Super Admin |
| `WithdrawalRequest` | Affiliate payout requests with approve/reject/paid status |
| `PaymentHistory` | Immutable payment ledger with unique `PAY-XXXXXXXXXX` IDs |
| `AffiliatePaymentDetail` | Affiliate UPI / bank account details for RazorpayX payouts |
| `AdminNotification` | In-app notifications for withdrawal requests |

---

## 🚀 Quick Start

See **[local_deployment.md](./local_deployment.md)** for the full local setup guide.

```bash
# 1. Clone
git clone https://github.com/<your-org>/social-media-automation.git
cd social-media-automation

# 2. Create virtualenv & install
python -m venv .venv
# Windows:  .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your DB credentials and API keys

# 4. Database
python manage.py migrate
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

**App:** http://127.0.0.1:8000/social/super-admin/  
**Admin:** http://127.0.0.1:8000/admin/

---

## 🌐 URL Structure

### Super Admin
| Path | Description |
|---|---|
| `/social/super-admin/` | Super admin dashboard |
| `/social/create-post/` | Create & publish a post |
| `/social/posts-list/` | All posts list |
| `/social/post-stats/` | Post analytics across platforms |
| `/social/users/` | Manage affiliate users |
| `/social/verification/` | Engagement verification dashboard |
| `/social/payment-settings/` | Configure payout rates |
| `/social/withdrawal-requests/` | Approve / reject payouts |
| `/social/payment-history/` | Full payment ledger |
| `/social/settings/` | Platform token settings |

### Affiliate Portal
| Path | Description |
|---|---|
| `/social/affiliate-register/` | Affiliate registration |
| `/social/affiliate-login/` | Affiliate login |
| `/social/affiliate-dashboard/` | Post feed — like, comment, share |
| `/social/affiliate/post-details/` | Detailed post analytics |
| `/social/affiliate/withdrawal/` | Request a payout |
| `/social/affiliate/payment-history/` | Past payouts |
| `/social/affiliate/rewards-settings/` | Earnings overview |
| `/social/edit-profile/` | Update profile & payment details |

### Integrations
| Path | Description |
|---|---|
| `/social/upload-image/` | n8n webhook endpoint for automated posting |
| `/social/linkedin/callback` | LinkedIn OAuth callback |
| `/social/collect-data/` | Collect engagement data endpoint |

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in all values:

```env
SECRET_KEY=''
DEBUG='False'
ALLOWED_HOSTS='yourdomain.com'

DB_NAME=''
DB_USER=''
DB_PASSWORD=''
DB_HOST='localhost'
DB_PORT='5432'

CLOUDINARY_CLOUD_NAME=''
CLOUDINARY_API_KEY=''
CLOUDINARY_API_SECRET=''

FACEBOOK_TOKEN=''
INSTAGRAM_TOKEN=''
LINKEDIN_TOKEN=''
FB_PAGE_TOKEN=''
FB_ACCESS_TOKEN_BASE=''
FB_ACCESS_TOKEN_COMMENTERS=''

APIFY_TOKEN=''
INSTAGRAM_SESSION_COOKIE=''

RAZORPAY_KEY_ID=''
RAZORPAY_KEY_SECRET=''
RAZORPAYX_ACCOUNT_NUMBER=''
```

See [deployment.md §5](./deployment.md#5-environment-variables) for a full annotated reference.

---

## 🚢 Production Deployment

See **[deployment.md](./deployment.md)** for the complete step-by-step guide covering:

- Ubuntu 22.04 server setup
- PostgreSQL configuration
- Gunicorn (systemd socket + service)
- Nginx reverse proxy
- SSL with Let's Encrypt / Certbot
- Cloudinary & Social API configuration
- **n8n self-hosted deployment** (Section 19)
- Security hardening checklist
- Log rotation, rollback, and troubleshooting

---

## 🔗 External Service Setup

### Cloudinary
1. Create a free account at [cloudinary.com](https://cloudinary.com)
2. Copy **Cloud name**, **API Key**, **API Secret** from the dashboard
3. Add to `.env`

### Facebook & Instagram (Graph API)
1. Create a Facebook Developer App at [developers.facebook.com](https://developers.facebook.com)
2. Add **Instagram Graph API** and **Pages API** products
3. Generate a long-lived page access token
4. Add to `.env` as `FB_PAGE_TOKEN` and `FACEBOOK_TOKEN`

### LinkedIn
1. Create an app at [linkedin.com/developers](https://www.linkedin.com/developers/)
2. Add OAuth 2.0 redirect URI: `https://yourdomain.com/social/linkedin/callback`
3. Complete the OAuth flow to obtain a token → stored in `SuperAdmin.lntoken`

### Razorpay / RazorpayX
1. Create a Razorpay account at [dashboard.razorpay.com](https://dashboard.razorpay.com)
2. Enable **RazorpayX** for automated payouts
3. Add API keys and account number to `.env`

### Apify
1. Create an account at [apify.com](https://apify.com)
2. Copy your API token from Account → Integrations
3. Add to `.env` as `APIFY_TOKEN`

---

## 🧪 Running Tests

```bash
python manage.py test
```

---
