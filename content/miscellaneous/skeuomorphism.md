---
title: "Skeuomorphic Project Desk"
date: 2025-12-31
draft: true
showToc: false
---

{{< rawhtml >}}
<div class="skeuomorphic-wrapper">
    <div class="skeuomorphic-container">
        <img src="/skeuomorphism/desk.jpg" alt="Skeuomorphic Project Desk" class="skeuomorphic-image">
        <svg viewBox="0 0 1024 559" class="skeuomorphic-overlay">
            <!-- AI & LLM Tools -->
            <a href="/projects/2025/terminalgpt/" title="Terminal GPT">
                <rect x="20" y="45" width="160" height="260" class="clickable-area" />
            </a>
            <a href="/projects/2025/llmjammer/" title="llmjammer">
                <rect x="320" y="375" width="70" height="110" class="clickable-area" />
            </a>
            <a href="/projects/2025/flatten-repo/" title="flatten-repo">
                <rect x="265" y="195" width="100" height="160" class="clickable-area" />
            </a>
            <a href="/miscellaneous/tell-ai/" title="How to Tell if AI">
                <rect x="435" y="450" width="100" height="60" class="clickable-area" />
            </a>
            <a href="/projects/2025/sign-language/" title="Sign Language Interpreter">
                <rect x="480" y="480" width="200" height="60" class="clickable-area" />
            </a>

            <!-- Networking & Security -->
            <a href="/projects/2025/udp-server-binary/" title="UDP Server (Binary)">
                <rect x="265" y="450" width="160" height="80" class="clickable-area" />
            </a>
            <a href="/projects/2025/gitkey/" title="Git Key Guardian">
                <rect x="10" y="315" width="190" height="110" class="clickable-area" />
            </a>
            <a href="/projects/2023/bbomb/" title="Binary Bomb Puzzle">
                <rect x="135" y="485" width="130" height="70" class="clickable-area" />
            </a>

            <!-- Health & Bio-Tech -->
            <a href="/projects/2025/glucopilot/" title="GluCoPilot (Dexcom)">
                <rect x="200" y="365" width="120" height="160" class="clickable-area" />
            </a>
            <a href="/projects/2024/dailytask/" title="Daily Task Tracker">
                <rect x="385" y="435" width="50" height="90" class="clickable-area" />
            </a>
            <a href="/projects/2024/one-rep-max/" title="One Rep Max Calc">
                <rect x="10" y="480" width="190" height="70" class="clickable-area" />
            </a>

            <!-- Games & Sim -->
            <a href="/miscellaneous/gameoflife/" title="Conway's Game of Life">
                <rect x="535" y="450" width="110" height="60" class="clickable-area" />
            </a>
            <a href="/projects/2025/connect-4/" title="Connect 4 Engine">
                <rect x="645" y="345" width="140" height="210" class="clickable-area" />
            </a>
            <a href="/miscellaneous/chess/" title="Chess & Blackjack">
                <rect x="635" y="450" width="130" height="60" class="clickable-area" />
            </a>

            <!-- Web & Software -->
            <a href="/projects/2025/interactive-microwave-tla/" title="TLA+ Microwave">
                <rect x="745" y="25" width="210" height="160" class="clickable-area" />
            </a>
            <a href="/miscellaneous/windows/" title="Windows Design Site">
                <rect x="795" y="345" width="110" height="60" class="clickable-area" />
            </a>
            <a href="/projects/2025/youtube-dl/" title="YouTube Downloader">
                <rect x="905" y="325" width="90" height="90" class="clickable-area" />
            </a>
            <a href="/miscellaneous/search-engine/" title="Search Engine">
                <rect x="775" y="415" width="210" height="160" class="clickable-area" />
            </a>

            <!-- Personal / Retro -->
            <a href="/resume/" title="CV / Resume">
                <rect x="675" y="450" width="190" height="80" class="clickable-area" />
            </a>
            <a href="/miscellaneous/my-zshrc/" title="~/.zshrc file">
                <rect x="575" y="125" width="80" height="110" class="clickable-area" />
            </a>
            <a href="/projects/2023/anagram/" title="Anagram Solver">
                <rect x="655" y="520" width="140" height="30" class="clickable-area" />
            </a>
            <a href="/miscellaneous/pixel-profile/" title="GitHub pfp Gen">
                <rect x="835" y="450" width="160" height="100" class="clickable-area" />
            </a>
        </svg>
        <div id="project-label" class="project-label">Hover over an item...</div>
    </div>
</div>

<style>
    .skeuomorphic-wrapper {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        font-family: 'Courier New', Courier, monospace;
    }
    .skeuomorphic-container {
        position: relative;
        width: 100%;
        max-width: 1024px;
        margin: 0 auto;
        overflow: hidden;
        border: 4px solid #333;
        border-radius: 4px;
    }
    .skeuomorphic-image {
        width: 100%;
        height: auto;
        display: block;
        filter: contrast(1.1) brightness(0.9);
    }
    .skeuomorphic-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    .clickable-area {
        fill: rgba(0, 255, 0, 0.05);
        stroke: rgba(0, 255, 0, 0.3);
        stroke-width: 2;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    .clickable-area:hover {
        fill: rgba(0, 255, 0, 0.15);
        stroke: rgba(0, 255, 0, 0.8);
        stroke-width: 3;
        filter: drop-shadow(0 0 10px rgba(0, 255, 0, 0.8));
    }
    .project-label {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: #0f0;
        padding: 5px 15px;
        border: 1px solid #0f0;
        border-radius: 4px;
        pointer-events: none;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        z-index: 10;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
</style>

<script>
    document.querySelectorAll('.clickable-area').forEach(area => {
        area.addEventListener('mouseenter', (e) => {
            const title = e.target.parentElement.getAttribute('title');
            document.getElementById('project-label').textContent = title;
        });
        area.addEventListener('mouseleave', () => {
            document.getElementById('project-label').textContent = 'Hover over an item...';
        });
    });
</script>
{{< /rawhtml >}}
