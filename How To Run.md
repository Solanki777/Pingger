# Pingger

Pingger is a Django-based website monitoring application. It checks
configured websites, stores health-check results, and can send alerts
when a website goes down or comes back online.

This guide explains how to run Pingger locally on Windows.

## 1. Prerequisites

Install:

-   Python 3.13
-   Git
-   PostgreSQL
-   Redis
-   VS Code or another code editor

Celery runs background tasks, and Celery Beat schedules periodic
monitoring checks.

## 2. Clone the repository

Open PowerShell:

``` powershell
git clone <YOUR_REPOSITORY_URL>
cd Pingger
```

If you already have the project, open PowerShell in the folder
containing `manage.py`.

## 3. Create and activate a virtual environment

``` powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this in the same terminal and try
again:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Create the local database

Start PostgreSQL and create a database named `pingger`. Use the username
and password configured for your local PostgreSQL installation.

## 6. Configure environment variables

Create a `.env` file in the project root (the folder containing
`manage.py`). Do not commit this file.

Example:

``` dotenv
SECRET_KEY=replace-with-a-local-secret
DEBUG=True

DB_NAME=pingger
DB_USER=postgres
DB_PASSWORD=your-local-postgres-password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

Update the database values to match your local setup. The project
settings disable PostgreSQL SSL for `localhost`.

For Google sign-in locally, configure the Google Social Application in
Django Admin and add this callback URL to your OAuth client:

`http://localhost:8000/accounts/google/login/callback/`

Use your own OAuth credentials. Never put client secrets in source
control.

## 7. Start Redis

If you use Docker, start Redis with:

``` powershell
docker run --name pingger-redis -p 6379:6379 -d redis
```

If the container already exists, use:

``` powershell
docker start pingger-redis
```

Verify Redis:

``` powershell
docker exec -it pingger-redis redis-cli ping
```

Expected output:

``` text
PONG
```

Alternatively, start your local Redis installation using its own
instructions.

## 8. Apply migrations

With the virtual environment activated, run:

``` powershell
python manage.py migrate
```

## 9. Create an admin user

``` powershell
python manage.py createsuperuser
```

Follow the prompts.

## 10. Start Django

In the project root, run:

``` powershell
python manage.py runserver
```

Open:

-   Website: http://127.0.0.1:8000/
-   Admin: http://127.0.0.1:8000/admin/

Keep this terminal open.

## 11. Start the Celery worker

Open a second PowerShell terminal in the project folder. Activate the
virtual environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Then start the worker:

``` powershell
celery -A config worker --loglevel=info --pool=solo
```

The `solo` pool is suitable for local development on Windows. Keep this
terminal open.

## 12. Start Celery Beat

Open a third PowerShell terminal in the project folder and activate the
virtual environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Start Beat:

``` powershell
celery -A config beat --loglevel=info
```

Keep this terminal open. Beat uses the database scheduler configured in
Django settings.

## 13. Configure scheduled checks

In Django Admin:

1.  Open **Periodic Tasks**.
2.  Add or edit the task that checks all active monitors.
3.  Set **Task** to `monitor.tasks.check_all_monitors`.
4.  Select an interval, such as every 5 minutes.
5.  Enable the task and save.

`monitor.tasks.check_monitor_task` is for one specific monitor and
requires its monitor ID in **Positional Arguments**, such as `[2]`. Do
not schedule it without the correct ID.

Scheduled checks require Django, Redis, the Celery worker, and Celery
Beat to be running.

## Troubleshooting

### Scheduled checks do not run

-   Confirm Redis responds with `PONG`.
-   Confirm the worker terminal reports that it is ready and has no
    broker connection errors.
-   Confirm Beat is running and logs that it sends due tasks.
-   Confirm the periodic task is enabled and has the intended interval.
-   Ensure all processes use the same `.env` file and database.

### Celery reports a connection error

Redis may not be running, or `REDIS_URL` may be incorrect. Start Redis
and check the host and port.

### Website checks time out

A slow target may exceed the timeout configured in
`monitor/services.py`. Verify the target URL and timeout. A timeout is
recorded as a failed health check.

### Migrations fail

Ensure PostgreSQL is running, the `pingger` database exists, and the
`.env` credentials are correct.

## Stop the local services

Press `Ctrl+C` in each terminal running Django, Celery Worker, and
Celery Beat.

If Redis runs in Docker, stop it with:

``` powershell
docker stop pingger-redis
```

## Security notes

-   Do not commit `.env`, database passwords, OAuth secrets, or
    production Django secret keys.
-   Use separate credentials for local development and production.
-   Run commands from the directory containing `manage.py`.
