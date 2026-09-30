# Pingger --- Project Problems, Solutions, Challenges, and Current Status

## 1. Project Overview

Pingger is a website monitoring application. It allows users to register
websites, run health checks, view monitoring results, and receive alerts
when a monitored website changes between available and unavailable
states.

The project is built with Django and uses PostgreSQL for data storage.
Celery and Redis are intended to handle scheduled and background
monitoring tasks.

## 2. Problems Pingger Is Designed to Solve

### Website availability is not always visible

A website owner may not know when their website becomes unavailable,
especially if they are not checking it manually. Pingger is intended to
check configured websites regularly and record whether they respond
successfully.

### Manual checking takes time

Checking every website manually is repetitive. Pingger is designed to
automate recurring health checks so users do not have to visit each
website themselves.

### Failures need a record and a response

A single failed request is useful, but a history of checks helps users
understand what happened. Pingger stores health-check results, including
status codes, response times, and errors when available.

### Users need to know when a website changes state

Pingger includes alert logic intended to notify users when a monitored
website goes down or comes back up. Email delivery depends on the email
configuration being correct.

## 3. Main Work Completed So Far

-   Built the Django application and its monitoring-related pages.
-   Added website monitoring records and health-check history.
-   Implemented a health-check service that sends an HTTP request to a
    monitored URL and records the result.
-   Added a manual **Check Now** flow. A manual check has been tested
    and returned HTTP 200 for a reachable website.
-   Added Celery tasks for checking an individual monitor and for
    scheduling checks across active monitors.
-   Configured PostgreSQL for the deployed application.
-   Configured Redis for Celery to use as its broker.
-   Added Django Admin support for managing scheduled tasks with
    `django-celery-beat`.
-   Created and configured periodic-task entries in the admin interface.
-   Created a local-run README with setup instructions for the
    development environment.

## 4. Problems Encountered and How They Were Addressed

### A. Django Site configuration

**Problem:** The application encountered a `Site.DoesNotExist` issue
because the expected Django Site record was not available or did not
match the configured `SITE_ID`.

**Work completed:** A migration was added to create/update the Site
record. The deployed database was checked, and the Site record was
present with ID `2`. The project setting was updated to `SITE_ID = 2`.

**Result:** This resolved the missing Site record issue.

### B. Google sign-in configuration

**Problem:** Google authentication did not immediately lead to the
expected direct login experience. A signup form appeared, and the email
being used was already associated with an existing admin account.

**Work completed:** The Google SocialApp was configured in Django Admin
and associated with the site. The allauth configuration was reviewed,
including options related to verified email authentication and
connecting a Google login to an existing account.

**Current note:** The Google authentication flow progressed to the
signup form. The final desired sign-in behavior still needs to be
verified after the account-linking configuration is confirmed.

### C. Manual health checks can block a web request

**Problem:** The manual check view runs the HTTP request inside the
Django web request. The health-check service uses a request timeout of
30 seconds. When a monitored website responds too slowly, the request
can take longer than the Gunicorn worker allows.

**Evidence observed:** Deployment logs showed a Gunicorn
`WORKER TIMEOUT` while handling `GET /monitors/1/check/`. The traceback
led to `perform_health_check()` and its `requests.get(..., timeout=30)`
call. The application also returned a 502 during deployment
troubleshooting.

**Work completed:** The manual check was tested against a reachable
website and returned HTTP 200. A longer Gunicorn timeout was considered
as a temporary workaround, but it does not address the underlying design
issue.

**Recommended technical direction:** Run potentially slow checks in the
background using Celery, then show the saved result to the user. This
avoids keeping a web request open while waiting for the monitored
website.

### D. Scheduled checks are not running

**Problem:** Periodic tasks were created in Django Admin, including
tasks configured with a one-minute interval. However, automatic checks
have not been observed running. The task's last-run time remained blank.

**Likely cause based on the available logs and configuration:** The
deployed web service starts Django with Gunicorn, but the current start
command does not start a Celery worker or Celery Beat. Creating a
periodic task in the admin interface stores its schedule; it does not
itself run the task. Beat must publish due tasks, and a worker must
execute them.

**Work completed:** Redis was started and tested locally, and
`redis-cli PING` returned `PONG`. Celery was installed and worker
commands were tested locally. Periodic tasks were also created in the
deployed Django Admin.

**Current status:** Automatic execution is still unverified in the
deployed environment because the required background processes have not
been successfully kept running there.

### E. Deployment command and platform behavior

**Problem:** The deployed service currently starts with:

``` bash
sh -c "python manage.py migrate --noinput && gunicorn config.wsgi:application"
```

An attempt was made to start Celery worker and Beat as detached
processes in the same command before starting Gunicorn:

``` bash
sh -c "python manage.py migrate --noinput && celery -A config worker --loglevel=info --detach && celery -A config beat --loglevel=info --detach && exec gunicorn config.wsgi:application"
```

**Observed result:** The combined command was followed by a Cloudflare
502. The service was then returned to the original Django-only start
command, which restored the web service.

**Current understanding:** The deployment platform's process/service
behavior is preventing the current all-in-one detached-process approach
from working reliably. The available evidence does not establish whether
the issue is specifically caused by process management, resource limits,
or another platform configuration detail.

**Next step:** Configure the web app, Celery worker, and Celery Beat as
separate platform services/processes if the platform supports that
arrangement. If the platform does not support persistent background
processes for this app, choose a supported worker/scheduler deployment
method. Then verify worker startup, Beat scheduling, task execution, and
database health-check records.

## 5. Current Deployment Status

**Status: Partially deployed; automatic monitoring is blocked by the
current deployment setup.**

The Django web application is deployed and can serve pages. The manual
**Check Now** feature has been tested and returned HTTP 200 for a
reachable target. PostgreSQL and the Django Site configuration have also
been set up.

However, scheduled monitoring is not yet working in the deployed
environment. The periodic tasks exist in Django Admin, but there is no
confirmed evidence that Celery Beat is publishing them or that a Celery
worker is executing them. An attempt to launch both background processes
alongside Gunicorn caused a 502, so the application was reverted to its
previous web-only start command.

Therefore, Pingger should not yet be described as fully deployed with
working automatic monitoring. The current blocker is the
deployment/runtime setup for background processes, rather than proof
that the monitoring task code itself is failing.

## 6. Main Difficulties Faced

1.  **Deployment process management:** The platform's
    service/start-command setup has made it difficult to run Django,
    Celery worker, and Celery Beat reliably together.
2.  **Debugging across multiple services:** The application depends on
    Django, PostgreSQL, Redis, Celery worker, and Celery Beat. A problem
    in any one of these can prevent scheduled checks from completing.
3.  **Long-running HTTP requests:** A monitored website can be slow or
    unresponsive, and a synchronous manual check can exceed the web
    server's worker timeout.
4.  **Authentication integration:** Google sign-in requires correct
    SocialApp, Site, and allauth settings, especially when the Google
    email already belongs to an existing user.
5.  **Separating application issues from platform issues:** The web app
    and manual check can work while scheduled tasks remain inactive. The
    deployment must be checked for running worker and scheduler
    processes before concluding that the task code is defective.

## 7. What Still Needs to Be Done

-   Establish a supported way to run a persistent Celery worker on the
    deployment platform.
-   Establish a supported way to run Celery Beat, or use another
    supported scheduler.
-   Confirm the worker connects to the same Redis broker and database as
    the web application.
-   Confirm that Beat publishes a due task and the worker receives and
    completes it.
-   Verify that a scheduled check creates a new `HealthCheck` record in
    the database.
-   Verify that state changes create the expected alert and that email
    delivery works.
-   Move manual checks to a background-task flow if appropriate, so slow
    websites do not block Gunicorn requests.
-   Keep `DEBUG=False` in production and rotate credentials that may
    have been exposed in logs or error pages.
-   Resolve the allauth settings warning and verify the intended Google
    login flow.

## 8. Summary

Pingger has a working Django foundation, database configuration,
health-check logic, manual checking, and Celery task definitions. The
project has also addressed a missing Django Site record and progressed
through Google authentication configuration.

The main unfinished part is reliable automatic monitoring in production.
Scheduled tasks have been configured, but they are not confirmed to
execute because the deployment currently runs the web application
without a successfully running Celery worker and scheduler. The attempt
to launch all processes together caused a 502, so the deployment was
rolled back to the web-only command.

**Current conclusion:** Pingger is partially deployed. Automatic
monitoring remains blocked until the background-process setup is made
compatible with the deployment platform and verified end to end.
