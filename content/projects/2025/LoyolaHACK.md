---
title: "CTA Transit Tracker"
date: 2025-02-16
description: "A real-time bus and train tracking system built during Loyola's Hackathon."
tags: ["Hackathon", "Flask"]
categories: ["Projects"]
image: "/previews/ctatracker.png"
draft: false
---

<hr>

{{< youtube u8ivcj2fhrk >}}

<hr>

During Loyola's Spring Hackathon, I built CTA Transit Tracker, a horribly buggy full-stack web app that predicts when Chicago buses and trains are about to show up near your home and then texts you about it. I built it solo in under 48 hours, which is the right amount of time to write the code and roughly half the amount of time you actually need to make it not break.

The premise was simple enough. I wanted something that would notice when a bus I cared about was a few minutes from my stop and send me a text so I didn't have to keep refreshing the CTA app. The CTA exposes their own real-time prediction APIs for both buses and trains, and they publish GTFS feeds — the standard transit data format, distributed as a bag of CSVs (`stops.txt`, `shapes.txt`, etc.) describing every route and stop in the system. So the data was there. What I had to build was everything around it.

The backend is Flask with SQLite for storage and Flask-Migrate/Alembic for schema changes, which I needed more times than I expected for a weekend project. The map is Leaflet — you drop a draggable marker on your home location, pick the lines you care about, and that gets saved to your account. Authentication is OTP over SMS, so there are no passwords stored anywhere. The notification side runs on Celery with a beat scheduler that wakes up on an interval, polls the CTA prediction APIs for your favorite lines, and decides whether anything's close enough to your home to be worth bugging you about.

The texting part is the dumb-but-fun trick of the project. Instead of paying for Twilio for a hackathon demo, I send texts through SMS-over-email gateways — every US carrier has an email-to-SMS bridge (`number@txt.att.net`, `@vtext.com`, etc.), so I just send an email and the carrier turns it into a text on the other end. It is exactly as reliable as that sounds, which is to say "mostly." It worked for the demo.

To actually run all of this in one place I had a Procfile with the Flask app under Gunicorn, the Celery worker, and the Celery beat scheduler — Heroku-style, though I was running it locally on a laptop in a Loyola classroom and praying nothing crashed during the judging round. Nothing crashed during the judging round.

It's still buggy. I'd love for it to not be. If you want to poke at the code or fix any of it, the [GitHub repo](https://github.com/EricSpencer00/LoyolaHACK) is up, and there's a [demo video](https://youtu.be/u8ivcj2fhrk) if you'd rather just watch the thing limp through a working flow.
