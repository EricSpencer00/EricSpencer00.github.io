---
title: "Yeat Large Language Model"
date: 2026-01-14
description: "Fine tuning GPT-2 to talk like Yeat"
tags: ["AI", "LLM"]
categories: ["Projects"]
draft: false
image: "/previews/yeat-llm.png"
---

Yeat LLM lets you generate new song lyrics that are derived from all of Yeat's public lyrics from Genius. 

```
twizzy)
It's up
I got so high (Yeah, yeah)
I been going on snappin', yeah
Yeah (Yeah, yeah)
Up on the sky
Goin' down (Goin' out)
Up on the ceiling (Goin' up, goin')
Up off the coast (Goin' up, goin')
Goin' down, goin' down (Goin')
Goin' down (Goin')
Goin' down (Goin')
Goin' down, goin', goin', goin', goin', goin', goin', goin', goin' down (Goin', goin', goin', goin', goin', goin', goin')
Goin', goin', goin', goin', goin', goin', goin', goin', goin', goin', goin', goin
```

Setup your Python environment as described [here](https://github.com/EricSpencer00/yeat-llm/blob/main/README.md).

Get a Genius API key to allow easy scraping from the site. Then, make requests via [/scrape_lyrics.py](https://github.com/EricSpencer00/yeat-llm/blob/main/scrape_lyrics.py). Afterwards, all of your lyrics will be inside the /songs directory. Then, [train your model](https://github.com/EricSpencer00/yeat-llm/blob/main/train_model.py). Your model can then be interacted with via [yeat_bot.py](https://github.com/EricSpencer00/yeat-llm/blob/main/yeat_bot.py). 

None of the original lyrics or models I have were made public for copyright reasons. Create similar models for different artists by changing which artist you use. 