---
title: ChatGPT Research
date: 2023-06-01
description: "Research with v3.5 and how it could possibly teach those new to Java Data Structures"
draft: true
tags: ["LLM", "Java"]
categories: ["Projects"]
draft: false
image: "previews/chatgpt_research.png"
---

During the summer of 2023 (article written August 2025), I contributed to research at Loyola regarding how ChatGPT understood CS2 data structures (defined from Pearson, the publisher, as the second Computer Science course in common curriculum--CS1 is akin to AP Computer Science A). 

I was given the task of evaluating responses from ChatGPT and compiling them on [https://curricula.cs.luc.edu/15-cs2/content.html](https://curricula.cs.luc.edu/15-cs2/content.html). I contributed to the sections on Maze search algorithms. I found it fun to take my theoretical knowledge from my Data Structures class and pair it with ChatGPT to further enhance my learning. 

Bi-weekly (obviously meaning once every [fortnight](https://en.wikipedia.org/wiki/Fortnight)) meetings helped guide the project and what direction to take when researching. 

![breadth first search maze gif](/images/projects/chatgpt_research/bfs.webp)
![depth first search maze gif](/images/projects/chatgpt_research/dfs.webp)

Credit to [seanperfecto](https://github.com/seanperfecto) on GitHub for the above gifs.

I've compiled my chats with v3.5 into convenient markdown format:

- [Iterative Maze Solver Example](../iterative-maze-solver)
  - BFS, DFS, and A* algorithms among others
- [Recursive Maze Solver Example](../recursive-maze-solver)
  - Memoization, multi-threaded approaches
- [Meta Researching ChatGPT](../meta_research)
  - A meta-level analysis where I ask the AI how it would research itself
- [Family Ancestry Tree in Java](../ancestry_tree)
  - Asking v3.5 how it would design an ancestry tree to find relatives


I believe they were listed on the Google Search index at one time in July 2025 due to them being shared with my reserach cohort as a public link, but OpenAI has since fixed that issue. Regardless, nothing sensitive was ever shared.

You can see how v3.5 was hallucinating (or just incompetant) back in 2023:

```
User:
Is the maze in your example able to be solved?

ChatGPT:
Apologies for the confusion, but upon reviewing the example maze, I noticed that it is not solvable. 
The maze has an isolated wall in the middle, blocking any path to the exit.

Here's the maze for reference:

*******
*     *
* *** *
* *   *
* ***** 
*     *
*******

```
This maze has no exits nor entrances.