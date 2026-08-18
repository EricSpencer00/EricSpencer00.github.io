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
                <rect x="15" y="25" width="160" height="175" class="clickable-area" />
            </a>
            <a href="/projects/2025/llmjammer/" title="llmjammer">
                <rect x="325" y="215" width="80" height="125" class="clickable-area" />
            </a>
            <a href="/projects/2025/flatten-repo/" title="flatten-repo">
                <rect x="275" y="110" width="110" height="155" class="clickable-area" />
            </a>
            <a href="/miscellaneous/tell-ai/" title="How to Tell if AI">
                <rect x="205" y="5" width="125" height="125" class="clickable-area" />
            </a>
            <a href="/projects/2025/sign-language/" title="Sign Language Interpreter">
                <rect x="435" y="375" width="155" height="135" class="clickable-area" />
            </a>

            <!-- Networking & Security -->
            <a href="/projects/2025/udp-server-binary/" title="UDP Server (Binary)">
                <rect x="190" y="300" width="240" height="140" class="clickable-area" />
            </a>
            <a href="/projects/2025/gitkey/" title="Git Key Guardian">
                <rect x="20" y="170" width="170" height="140" class="clickable-area" />
            </a>
            <a href="/projects/2023/bbomb/" title="Binary Bomb Puzzle">
                <rect x="170" y="290" width="90" height="65" class="clickable-area" />
            </a>

            <!-- Health & Bio-Tech -->
            <a href="/projects/2025/glucopilot/" title="GluCoPilot (Dexcom)">
                <rect x="175" y="180" width="90" height="115" class="clickable-area" />
            </a>
            <a href="/projects/2024/dailytask/" title="Daily Task Tracker">
                <rect x="400" y="215" width="45" height="95" class="clickable-area" />
            </a>
            <a href="/projects/2024/one-rep-max/" title="One Rep Max Calc">
                <rect x="15" y="380" width="155" height="165" class="clickable-area" />
            </a>

            <!-- Web & Software (drawn before Games so Chess overlays Search Engine) -->
            <a href="/projects/2025/interactive-microwave-tla/" title="TLA+ Microwave">
                <rect x="825" y="15" width="185" height="170" class="clickable-area" />
            </a>
            <a href="/miscellaneous/windows/" title="Windows Design Site">
                <rect x="415" y="15" width="240" height="295" class="clickable-area" />
            </a>
            <a href="/projects/2025/youtube-dl/" title="YouTube Downloader">
                <rect x="965" y="105" width="50" height="85" class="clickable-area" />
            </a>
            <a href="/miscellaneous/search-engine/" title="Search Engine">
                <rect x="775" y="195" width="230" height="230" class="clickable-area" />
            </a>

            <!-- Games & Sim (after Web/Software so foreground items win on hover) -->
            <a href="/projects/2025/connect-4/" title="Connect 4 Engine">
                <rect x="605" y="175" width="170" height="215" class="clickable-area" />
            </a>
            <a href="/miscellaneous/gameoflife/" title="Conway's Game of Life">
                <rect x="545" y="305" width="115" height="60" class="clickable-area" />
            </a>
            <a href="/miscellaneous/chess/" title="Chess & Blackjack">
                <rect x="775" y="305" width="60" height="110" class="clickable-area" />
            </a>

            <!-- Personal / Retro (drawn last - foreground desk items) -->
            <a href="/resume/" title="CV / Resume">
                <rect x="585" y="380" width="135" height="110" class="clickable-area" />
            </a>
            <a href="/miscellaneous/my-zshrc/" title="~/.zshrc file">
                <rect x="625" y="80" width="115" height="75" class="clickable-area" />
            </a>
            <a href="/projects/2023/anagram/" title="Anagram Solver">
                <rect x="735" y="440" width="140" height="50" class="clickable-area" />
            </a>
            <a href="/miscellaneous/pixel-profile/" title="GitHub pfp Gen">
                <rect x="855" y="395" width="150" height="150" class="clickable-area" />
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
