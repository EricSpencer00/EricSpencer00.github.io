---
title: "BlackJack Game"
date: 2025-06-13
description: "Play BlackJack with fake money"
tags: ["web development", "javascript", "canvas"]
categories: ["Miscellaneous"]
draft: false
image: "/previews/blackjack.png"
---

Play BlackJack with fake money in this interactive JavaScript game! Maybe if this does well enough I'll hook up the Coinbase API.

{{< rawhtml >}}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blackjack Canvas Game</title>
    <link rel="stylesheet" href="/css/blackjack.css">
</head>
<body>
    <div class="game-wrapper">
        <h1>Blackjack</h1>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div class="controls">
            <div class="game-controls">
                <button id="deal-btn">Deal New Hand</button>
                <button id="hit-btn" disabled>Hit</button>
                <button id="stand-btn" disabled>Stand</button>
                <button id="double-down-btn" disabled>Double Down</button>
                <button id="split-btn" disabled>Split</button>
            </div>
        </div>
    </div>
    <script src="/js/blackjack.js"></script>
</body>
</html>
{{< /rawhtml >}} 