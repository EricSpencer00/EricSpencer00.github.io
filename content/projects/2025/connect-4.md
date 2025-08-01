---
title: "Connect 4 Game Engine"
date: 2025-06-29
description: "A Chess engine-esque Connect 4 analyzer"
tags: ["localhost", "python", "game"]
categories: ["Projects"]
image: "/previews/connect-4.png"
draft: false
---
[GitHub Repo](https://github.com/EricSpencer00/connect-4)

![Photo of the Connect 4 game engine](/previews/connect-4.png)

Inspired by Chess Engines that mathematically predict how long it will take for a player to win a game (or the liklihood of a player winning a game), I created the same thing for Connect 4. 

## Solved Mode

The AI was trained on 67,557 unique and legal positions by move 4 (both players have just played 4 moves each) of the game. Each position is labeled with the game-theoretic outcome of win/loss/tie. Also, these positions require no player to have won nor have a forcing move on the next play (3 in a row and similar positions). The dataset was acquired from work by John Tromp [tromp.github.io](https://tromp.github.io).

*Sidenote, I absolutely love simple html pages like the one above. 
They're extremely optimized for browsers that expect thousands of lines of JavaScript.*

Connect 4 is a solved game, meaning that if you play first and play optimally, you will win 100% of the time (Most people do not).

