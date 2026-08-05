# Pingger

Pingger is a website monitoring platform that helps developers track the availability and performance of their web applications.

Users can create an account, add one or more website URLs, and Pingger automatically performs periodic health checks by sending HTTP requests at configurable intervals. Each check records important metrics such as uptime status, response time, HTTP status code, and the time of the last successful check.

The dashboard provides a real-time overview of every monitored website, allowing users to quickly identify downtime, investigate historical performance, and receive notifications when a website becomes unavailable.

## Features

* 🔐 User authentication (Register & Login)
* 🌐 Monitor multiple websites
* ⏱️ Automatic health checks at regular intervals
* 📊 Response time tracking
* ✅ HTTP status monitoring
* 📈 Uptime statistics
* 📝 Historical check logs
* 🔔 Downtime notifications (coming soon)
* 📱 Responsive dashboard

## Tech Stack

* **Frontend:** React / Next.js
* **Backend:** Node.js + Express
* **Database:** PostgreSQL / MongoDB
* **Scheduler:** Cron Jobs / BullMQ
* **Authentication:** JWT / Clerk / NextAuth
* **Deployment:** Render / Railway / Vercel

## Future Improvements

* Email, Discord, and Telegram alerts
* SSL certificate monitoring
* Domain expiry monitoring
* API endpoint monitoring
* Public status pages
* Team collaboration
* Custom check intervals
* Performance analytics
* Incident reports
