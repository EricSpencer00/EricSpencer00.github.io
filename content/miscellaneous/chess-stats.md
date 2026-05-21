---
title: "Chess.com Stats Display"
date: 2025-08-01
description: "A small Flask app that pulls Chess.com's public API and graphs your rating history."
tags: ["Python", "Chess", "AI-written"]
categories: ["Miscellaneous"]
draft: false
---

I play a fair amount of Chess.com and wanted a stats page that wasn't buried three clicks deep in their site. Chess.com has a free public API, so I threw together a small Flask app that takes a username, hits `/pub/player/{user}`, `/pub/player/{user}/stats`, and `/pub/player/{user}/games/archives`, and dumps everything onto one page.

The whole thing is one `app.py` file. Flask renders the templates inline as strings (so there's no `templates/` folder — just a couple of giant triple-quoted HTML blobs at the top of the file). Styling is Bootstrap 4 from a CDN. The rating graph is Chart.js, also from a CDN. The "build" step is `pip install -r requirements.txt && python app.py`.

The graph part was the only piece that took any real work. Chess.com doesn't give you a rating history endpoint directly — you have to walk the monthly archives, pull every game in the time window, find the games where the requested user is white or black, and pluck out their rating at game-end. So if you ask for "all time" on a heavy player you're firing off a lot of requests in a loop. I left it synchronous because this is a local tool and I'm the only one running it.

I never deployed it. It just runs on `localhost:5000` when I want to look at someone's stats — usually after I've lost a game and want to feel better by checking that my opponent is, in fact, much higher rated than me. The four categories it tracks are daily, rapid, blitz, and bullet.

Source: [github.com/EricSpencer00/ChessStats](https://github.com/EricSpencer00/ChessStats). It's tiny — if you want to fork it and actually host it somewhere, you'd want to add some caching so you're not hammering the archives endpoint on every request.

---

*Written with AI.*
