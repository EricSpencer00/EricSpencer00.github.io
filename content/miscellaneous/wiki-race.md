---
title: "Wiki Race Game"
date: 2025-06-30
description: "Race from one Wikipedia article to another as fast as possible!"
tags: ["web development", "javascript", "wikipedia", "canvas"]
categories: ["Miscellaneous"]
draft: true
---

{{< rawhtml >}}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wiki Race Game</title>
    <link rel="stylesheet" href="/css/wiki-race.css">
</head>
<body>
    <div class="wiki-race-wrapper">
        <h1>Wiki Race</h1>
        <div class="game-controls">
            <label>Start Page: <input type="text" id="start-page" value="Python_(programming_language)"></label>
            <label>End Page: <input type="text" id="end-page" value="Philosophy"></label>
            <button id="start-btn">Start Race</button>
            <span id="timer">00:00</span>
        </div>
        <div id="current-path"></div>
        <iframe id="wiki-frame" width="800" height="600" sandbox="allow-scripts allow-same-origin"></iframe>
        <div class="network-analysis">
            <button id="analyze-btn">Analyze Path Network</button>
            <div id="network-result"></div>
        </div>
    </div>
    <script src="/js/wiki-race.js"></script>
</body>
</html>
{{< /rawhtml >}}
