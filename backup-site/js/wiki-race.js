// Wiki Race Game Logic
const startBtn = document.getElementById('start-btn');
const analyzeBtn = document.getElementById('analyze-btn');
const timerEl = document.getElementById('timer');
const wikiFrame = document.getElementById('wiki-frame');
const startInput = document.getElementById('start-page');
const endInput = document.getElementById('end-page');
const currentPathEl = document.getElementById('current-path');
const networkResult = document.getElementById('network-result');

let timer = 0, interval = null, started = false;
let path = [], visited = new Set();
let endPage = '';

function formatTime(sec) {
    const m = String(Math.floor(sec/60)).padStart(2,'0');
    const s = String(sec%60).padStart(2,'0');
    return `${m}:${s}`;
}

function startRace() {
    timer = 0;
    timerEl.textContent = '00:00';
    started = true;
    path = [];
    visited = new Set();
    endPage = endInput.value.trim();
    currentPathEl.textContent = '';
    networkResult.textContent = '';
    if(interval) clearInterval(interval);
    interval = setInterval(() => {
        timer++;
        timerEl.textContent = formatTime(timer);
    }, 1000);
    loadWikiPage(startInput.value.trim());
}

function loadWikiPage(title) {
    const url = `https://en.wikipedia.org/wiki/${encodeURIComponent(title)}`;
    wikiFrame.src = url;
    path.push(title);
    visited.add(title);
    updatePath();
}

function updatePath() {
    currentPathEl.textContent = 'Path: ' + path.join(' → ');
}

// Prevent back navigation
function canNavigateTo(title) {
    return !visited.has(title);
}

// Listen for iframe load and filter links
wikiFrame.addEventListener('load', () => {
    let doc;
    try {
        doc = wikiFrame.contentDocument || wikiFrame.contentWindow.document;
    } catch (e) {
        // Cross-origin, can't access
        return;
    }
    if (!doc) return;
    // Only allow links to Wikipedia articles
    const anchors = doc.querySelectorAll('a[href]');
    anchors.forEach(a => {
        const href = a.getAttribute('href');
        if (!href.startsWith('/wiki/') || href.includes(':') || href.startsWith('/wiki/Main_Page')) {
            a.removeAttribute('href');
            a.style.pointerEvents = 'none';
            a.style.opacity = '0.5';
        } else {
            // Only allow forward navigation
            a.addEventListener('click', e => {
                e.preventDefault();
                const nextTitle = decodeURIComponent(href.split('/wiki/')[1]);
                if (canNavigateTo(nextTitle)) {
                    loadWikiPage(nextTitle);
                    if (nextTitle === endPage) {
                        clearInterval(interval);
                        timerEl.textContent += ' (Finished!)';
                        started = false;
                    }
                }
            });
        }
    });
});

startBtn.onclick = startRace;

analyzeBtn.onclick = () => {
    if (path.length < 2) {
        networkResult.textContent = 'Not enough data to analyze.';
        return;
    }
    // Simple network: show path and number of hops
    networkResult.innerHTML = `Visited <b>${path.length}</b> pages:<br>` + path.map((p,i) => `${i+1}. ${p}`).join('<br>');
};
