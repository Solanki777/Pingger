# 🏓 Pingger

> **Real-time website uptime monitoring** — built with Django, Celery, Redis, and PostgreSQL.

Pingger lets you track the health of any URL on a configurable schedule. It records response times, calculates uptime percentages, and instantly alerts you (in-app **and** via email) whenever a site goes down or comes back online.

---

## 🚀 Deployment Status

> ⚠️ **Currently not publicly deployed**
>
> Pingger has been fully developed and tested locally, including Google authentication, website monitoring, scheduled health checks, alerts, notifications, and email functionality.
>
> The application is **currently not deployed to a public production server because the selected free cloud hosting provider requires credit-card/payment verification**. Since a suitable payment method is not currently available, deployment has been temporarily paused.
>
> The project is fully functional in the local development environment, and screenshots of the working application are provided below.

---

## 🖥️ Working Application Screenshots

The following screenshots demonstrate the working Pingger application.

### 🔐 Google Login
![Pingger Login](screenshots/Login.png)
![Pingger welcome](screenshots/welcome.png)

### 📊 Monitoring Dashboard

![Pingger Dashboard](screenshots/dashboard.png)

### 🌐 Add or Save Website Monitor

![Add Monitor](screenshots/add-monitor.png)

### 🟢 Website Up

![Website Up](screenshots/website-up.png)

### 🔴 Website Down

![Website Down](screenshots/website-down.png)

### 📈 Monitoring Graph

![Monitoring Graph](screenshots/monitor-graph.png)

### 🔔 Alerts & Notifications

![Alerts](screenshots/alerts.png)

### 📧 Email Notification

![Email Notification](screenshots/email-alert.png)

> These screenshots demonstrate the application's functionality running in the local development environment.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔍 **Health Checks** | HTTP GET checks with 10 s timeout; records status code & response time |
| ⏱ **Scheduled Monitoring** | Per-monitor intervals (minutes) powered by Celery Beat + `django-celery-beat` |
| 📊 **Uptime Calculation** | Accurate 24 h / 7 d / 30 d uptime % accounting for pause/resume state |
| 🔔 **Smart Alerts** | Fires only on state transitions (UP → DOWN and DOWN → UP) |
| 📧 **Email Notifications** | Gmail SMTP — "Website Down 🔴" and "Back Online 🟢" emails |
| 👤 **Auth** | Django-allauth with Google OAuth & GitHub OAuth support |
| 🗃 **Per-user isolation** | Every monitor, check, and alert is scoped to the owner |
| 🕹 **Manual checks** | Trigger an instant check from the dashboard at any time |
| ✏️ **Full CRUD** | Add, edit, pause/resume, and delete monitors |

---

## 🏗 Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Django 6 |
| Task queue | Celery 5 |
| Message broker / cache | Redis 8 |
| Task scheduler | Celery Beat + `django-celery-beat` |
| Database | PostgreSQL (via `psycopg` 3) |
| Authentication | `django-allauth` (Google & GitHub OAuth) |
| HTTP checks | `requests` |
| Email | Gmail SMTP |

---

## 📁 Project Structure

```text
Pingger/

├── config/                 # Django project settings
│   ├── settings.py        # Main settings (DB, Celery, email, allauth)
│   ├── celery.py          # Celery application instance
│   └── urls.py            # Root URL conf
│
├── monitor/               # Core monitoring app
│   ├── models.py          # Monitor, HealthCheck, MonitorState, Alert
│   ├── views.py           # All views (list, add, edit, delete, APIs)
│   ├── tasks.py           # Celery tasks
│   ├── services.py        # Health checks and uptime calculations
│   ├── signals.py         # Django signals
│   └── urls.py            # Monitor URL patterns
│
├── templates/             # HTML templates
├── screenshots/           # Working application screenshots
├── requirements.txt       # Python dependencies
├── manage.py
└── .env                   # Environment variables (not committed)