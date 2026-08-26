# 🏓 Pingger

> **Real-time website uptime monitoring** — built with Django, Celery, Redis, and PostgreSQL.

Pingger lets you track the health of any URL on a configurable schedule. It records response times, calculates uptime percentages, and instantly alerts you (in-app **and** via email) whenever a site goes down or comes back online.

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

```
Pingger/
├── config/               # Django project settings
│   ├── settings.py       # Main settings (DB, Celery, email, allauth)
│   ├── celery.py         # Celery application instance
│   └── urls.py           # Root URL conf
│
├── monitor/              # Core monitoring app
│   ├── models.py         # Monitor, HealthCheck, MonitorState, Alert
│   ├── views.py          # All views (list, add, edit, delete, APIs)
│   ├── tasks.py          # Celery tasks: check_monitor_task, check_all_monitors
│   ├── services.py       # perform_health_check(), calculate_uptime()
│   ├── signals.py        # Django signals
│   └── urls.py           # Monitor URL patterns
│
├── templates/            # HTML templates (base, login, dashboard, etc.)
├── requirements.txt      # Python dependencies
├── manage.py
└── .env                  # Environment variables (not committed)
```

---

## ⚙️ Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| PostgreSQL | 14+ |
| Redis | 7+ (via Docker recommended) |
| Docker (optional) | For running Redis |

---

## 🚀 Getting Started

### 1 — Start Redis

If you have Docker installed, the easiest way to run Redis is:

```bash
# First time — create the container
docker run --name pingger-redis -p 6379:6379 -d redis

# Subsequent starts
docker start pingger-redis
```

> If `docker start pingger-redis` says the container already exists and is running, you're good to go.

---

### 2 — Set up the Python environment

```bash
# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

---

### 3 — Configure environment variables

Create a `.env` file in the project root (copy the example below):

```env
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

> **Tip:** Use a [Gmail App Password](https://support.google.com/accounts/answer/185833) — not your regular Gmail password.

---

### 4 — Set up the database

Make sure PostgreSQL is running and a database named `pingger` exists, then:

```bash
python manage.py migrate
python manage.py createsuperuser   # optional — for /admin access
```

---

### 5 — Run the Django development server

```bash
python manage.py runserver
```

The app will be available at **http://127.0.0.1:8000**

---

### 6 — Start the Celery worker

Open a **new terminal**, activate the venv, then run:

```bash
celery -A config worker --loglevel=INFO --pool=solo
```

Wait until you see output similar to:

```
connected to redis://localhost:6379/0
celery@<hostname> ready.
```

---

### 7 — Start the Celery Beat scheduler

Open **another terminal**, activate the venv, then run:

```bash
celery -A config beat --loglevel=INFO
```

This is what fires the periodic health-check tasks on schedule.

---

## 🖥 Running the Full Stack (summary)

| Terminal | Command |
|---|---|
| 1 | `docker start pingger-redis` |
| 2 | `venv\Scripts\activate` → `python manage.py runserver` |
| 3 | `venv\Scripts\activate` → `celery -A config worker --loglevel=INFO --pool=solo` |
| 4 | `venv\Scripts\activate` → `celery -A config beat --loglevel=INFO` |

---

## 🔌 API Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/monitors/` | Dashboard — list all monitors |
| `GET/POST` | `/monitors/add/` | Add a new monitor |
| `GET/POST` | `/monitors/<id>/edit/` | Edit monitor name, URL, interval |
| `POST` | `/monitors/<id>/delete/` | Delete a monitor |
| `POST` | `/monitors/<id>/toggle/` | Pause / resume a monitor |
| `GET` | `/monitors/<id>/check/` | Manual health check |
| `GET` | `/monitors/<id>/details/` | Monitor detail page |
| `GET` | `/monitors/<id>/logs/` | JSON — last 20 health check logs |
| `GET` | `/monitors/<id>/graph/` | JSON — last 100 data points for chart |
| `GET` | `/api/alerts/` | JSON — last 20 alerts + unread count |
| `POST` | `/api/alerts/<id>/read/` | Dismiss / delete an alert |

---

## 🗄 Data Models

### `Monitor`
Represents a tracked URL.

| Field | Type | Description |
|---|---|---|
| `name` | CharField | Human-readable label |
| `url` | URLField | Target URL |
| `is_active` | BooleanField | Whether monitoring is running |
| `check_interval` | PositiveIntegerField | Minutes between checks |
| `user` | ForeignKey → User | Owner |

### `HealthCheck`
One recorded HTTP check result.

| Field | Type | Description |
|---|---|---|
| `monitor` | ForeignKey | Parent monitor |
| `status_code` | IntegerField | HTTP response code |
| `response_time` | FloatField | Round-trip time in ms |
| `success` | BooleanField | `True` if 2xx response |
| `error` | TextField | Error message if failed |
| `check_type` | CharField | `"user"` or `"celery"` |

### `MonitorState`
Tracks pause/resume history for accurate uptime calculations.

### `Alert`
An in-app + email notification fired on UP ↔ DOWN transitions.

---

## 📧 Email Alerts

Pingger uses Gmail SMTP to send two types of email:

- **🔴 Website Down** — sent when a monitor transitions from UP to DOWN
- **🟢 Back Online** — sent when a monitor transitions from DOWN to UP

Alerts are only sent on **state transitions**, so you won't be spammed with repeated emails.

---

## 🔐 Authentication

Pingger uses `django-allauth` and supports:

- **Username / Password** — standard Django auth
- **Google OAuth** — one-click sign-in with Google
- **GitHub OAuth** — one-click sign-in with GitHub

To configure OAuth providers, add your client ID and secret to the Django Admin under **Sites → Social Applications**.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute it.

---

<p align="center">Made with ❤️ using Django + Celery + Redis</p>