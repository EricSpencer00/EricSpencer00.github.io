---
title: "CTA Transit Tracker"
date: 2025-02-16
description: "A real-time bus and train tracking system built during Loyola's Hackathon."
tags: ["hackathon", "Flask", "Celery", "Firebase", "transit"]
categories: ["Projects"]
image: "../Images/cta_tracker_logo.png"
draft: false
---

<hr>

{{< youtube u8ivcj2fhrk >}}

<hr>

During Loyola’s Spring Hackathon, I built **CTA Transit Tracker**, a horribly buggy full-stack web app that provides **real-time bus and train predictions** across Chicago. It integrates **CTA’s APIs**, **GTFS data**, and a **custom notification system** that texts users when their favorite lines are arriving near their home.

This was a major engineering challenge that included:
- 🔧 Parsing and visualizing **GTFS transit data** with `folium` and `Leaflet.js`
- 🧠 Creating a **notification system** with **Celery workers** that checks for real-time arrivals
- 📨 Sending alerts via **SMS-over-email gateways**
- 🔐 Implementing **OTP-based phone authentication**
- 🌐 Building a dynamic dashboard with **Flask** and **Bootstrap**

### 🧠 Technical Highlights:
- **Flask** backend handles user auth, prediction APIs, and dynamic routing.
- **Celery** with a separate beat scheduler to push notifications based on custom thresholds.
- **GTFS data** parsed live from CSVs to render routes and stops.
- Uses **SQLite** for fast local data storage, with **Flask-Migrate** + Alembic for schema changes.
- **Leaflet.js** provides an interactive map of buses and trains using emoji and icon markers.
- Users can **set their home location**, **favorite lines**, and **receive SMS alerts** based on proximity and time-to-arrival.

### 🧪 Notable Features:
- 📍 Draggable home marker to set geolocation preferences
- 🔁 Real-time updates from both CTA bus and train trackers
- 🗺️ Route and stop visualization using `stops.txt` and `shapes.txt`
- 💬 OTP verification for login without storing passwords
- 🔔 Background job sends SMS when a favorite line is about to arrive near home

### 🧑‍💻 Team:
- Solo project built in under 48 hours
- Deployed using **Gunicorn**, **Celery**, and a `Procfile` for Heroku-style hosting

---

### 🔗 Useful Links:
- 💻 [GitHub Repository](https://github.com/EricSpencer00/LoyolaHACK)  
- 📹 [Demo Video](https://youtu.be/u8ivcj2fhrk)

---
