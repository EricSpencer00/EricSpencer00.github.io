---
title: "GluCoPilot"
date: 2025-09-11
description: "AI Glucose Insights App"
tags: ["Swift", "Dexcom", "iOS"]
categories: ["Projects"]
draft: false
---

During the September 2025 OpenAI Hackathon for GPT-OSS:120b, they opened up inference to the model on HuggingFace for free. The hackathon had the intention of producing fine-tuned use cases for the oss model. I, along with many other contestants, just treated the hackathon as an opportunity to make an AI wrapper project. The only fine tuning I did with 120b was some prompt engineering.

GluCoPilot is an app that taps into multiple health sources to provide insights on your glucose numbers throughout the day. Users with a Dexcom-based continuous glucose monitor (CGMs such as Stelo or g7) can access their live data through the company's APIs. The app uses this data source along with others, such as Apple Health and MyFitnessPal, to aggregate all of a user's health data. Then, this data is time series'd into a 24 hour window that 120b can analyze and provide suggestions for improvement. For example, if a user's glucose is too high at 4pm, and your Apple Watch shows little activity during that time, the AI insights will suggest more activity during that time. If you drank a Sprite at 7pm and managed to not spike your glucose due to the amount of activity you did, the AI will recognize it and applaude you. 

Now, in practice the app would have flaws due to the entire architecture not being provided enough data. The problem with data logging and tracking for things like food is that the act of logging is a hurdle. CGMs and Apple Watches are perfect UX, while MyFitnessPal suffers from missing and inaccurate data. If you're trying to eat healthier and cleaner, the things you buy likely don't have labels or barcodes to identify their nutritional makeup. 

To get further into the architecture. The App started off as a React Native project with a Python backend (utilizing my favorite Dexcom library, pydexcom). However, I wanted Apple Health integration among other things, so I switched to Swift and lighter Python backend. 
In a nutshell, the frontend Swift would authenticate using Dexcom OAuth and the backend would use rate limited API calls to the HuggingFace inference servers. All Apple Health, Dexcom, and MyFitnessPal data would aggregate itself on the frontend after adding those services. Then, a single JSON prompt with about 100k tokens of context would be sent to the AI for analysis. I would rate the accuracy of the AI at about 65%. It was too general in some cases. Since I forced it to always return 5 results, it gave 1 or 2 good insights and then the same boilerplate suggestions afterwards.

