---
title: "GraceNook"
date: 2025-12-14
description: "A FaceBook Clone"
tags: ["NextJS", "Dexcom", "iOS"]
categories: ["Projects"]
draft: true
---

This semester, I got really into utilizing CloudFlare for my projects. They offer completely free hosting for fullstack sites, without a credit card. I had taken a systems design class in the Quinlan Business School at Loyola. The semester long assignment was to create an entire architecture for any product we desired. However, I wanted to build our system out for fun. Creating a live demo of the site was as easy as giving Claude Haiku 3% of my monthly Copilot usage. You can compare the semester long project design specification as one large prompt engineering exercise. 

The idea was to rebuild Facebook's specifications in a realistic way. We would use their ideas of liking posts, commenting on other's photos, and DM'ing friends as well. In order to make the project economically feasible, we allowed ads on the platform. This required an ad portal. To manage both the ad portal and the platform, Admins with elevated access were necessary. 

The app had a small CloudFlare worker with React Server Components, a light R1 database, and a beautiful frontend in NextJS.

