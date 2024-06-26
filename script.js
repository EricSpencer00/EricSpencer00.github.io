function secretFunction() {
    confetti.start();
    setTimeout(function() {
        confetti.stop();
    }, 7000); // 7 seconds
}

function generateHexGrid(width, height) {
    let grid = '';
    for (let h = 0; h < height; h++) {
        let line = '';
        for (let w = 0; w < width; w++) {
            line += (w % 19 === 0 && w !== 0) ? "    " : Math.floor(Math.random() * 256).toString(16).padStart(2, '0').toUpperCase() + " ";
        }
        grid += line.trim() + '\n';
    }
    return grid;
}

function updateBackgroundHex() {
    const hexElement = document.getElementById('hexBackground');
    hexElement.textContent = generateHexGrid(200, 20);
}

// setInterval(updateBackgroundHex, 1000)

function typeText2dArray(asciiArtArray, id, speed) {
    const container = document.getElementById(id);
    container.innerHTML = '';

    // Determine the size of the canvas
    let canvasWidth = 0;
    let canvasHeight = 0;
    asciiArtArray.forEach(letter => {
        canvasWidth += letter[0].length;
        canvasHeight = Math.max(canvasHeight, letter.length);
    });

    // Initialize the canvas with empty spaces
    const canvas = Array(canvasHeight).fill('').map(() => Array(canvasWidth).fill(' '));

    function mergeLetter(letter, startCol) {
        for (let row = 0; row < letter.length; row++) {
            for (let col = 0; col < letter[row].length; col++) {
                const char = letter[row][col];
                if (char !== ' ') {
                    canvas[row][startCol + col] = char;
                }
            }
        }
    }

    function printCanvas() {
        container.innerHTML = canvas.map(row => row.join('')).join('\n');
    }

    let letterIndex = 0;
    let currentCol = 0;
    const totalLetters = asciiArtArray.length;

    function type() {
        if (letterIndex < totalLetters) {
            const letter = asciiArtArray[letterIndex];
            mergeLetter(letter, currentCol);
            currentCol += letter[0].length;

            letterIndex++;
            setTimeout(type, speed);
            printCanvas();
        }
    }

    type();
}

function typeHTML(text, id, speed) {
    const element = document.getElementById(id);
    let index = 0;

    function type() {
        if (index < text.length) {
            // Use innerHTML to correctly interpret HTML tags
            element.innerHTML += text[index];
            index++;
            setTimeout(type, speed);
        }
    }

    type();
}

function typeText(text, id, speed, includeCursor) {
    const container = document.getElementById(id);
    container.innerHTML = '';

    // Pre-allocate lines
    const lines = text.split('\n');
    const numberOfLines = lines.length;

    const measurementSpan = document.createElement('span');
    measurementSpan.style.visibility = 'hidden';
    measurementSpan.style.whiteSpace = 'pre';
    measurementSpan.textContent = 'A';
    container.appendChild(measurementSpan);
    const lineHeight = measurementSpan.offsetHeight;
    container.removeChild(measurementSpan);

    container.style.height = `${numberOfLines * lineHeight}px`;

    let index = 0;
    const startTime = performance.now();

    let cursor;
    if (includeCursor) {
        cursor = document.createElement('span');
        cursor.textContent = '▌';
        cursor.style.animation = 'blink 1s step-end infinite';
        container.appendChild(cursor);
    }

    function type() {
        const currentTime = performance.now();
        const elapsedTime = currentTime - startTime;
        const expectedTime = index * speed;
        const remainingTime = Math.max(0, expectedTime - elapsedTime);

        if (index < text.length) {
            const char = text[index++];
            if (char === '\n') {
                container.appendChild(document.createElement('br'));
            } else {
                const span = document.createElement('span');
                span.textContent = char;
                if (includeCursor) {
                    container.insertBefore(span, cursor);
                } else {
                    container.appendChild(span);
                }
            }

            setTimeout(type, remainingTime);
        } else if (includeCursor) {
            container.appendChild(cursor); // Make sure the cursor is at the end
        }
    }

    type();
}

// CSS for cursor blinking
const style = document.createElement('style');
style.textContent = `
    @keyframes blink {
        50% { opacity: 0; }
    }
    .cursor {
        display: inline-block;
        white-space: pre;
    }
    span {
        white-space: pre;
    }
`;
document.head.appendChild(style);


function chessStats() { 
    document.addEventListener('DOMContentLoaded', function() {
        const username = 'EricSpencer00';
        const statsDiv = document.getElementById('stats');

        fetch(`https://api.chess.com/pub/player/${username}/stats`)
            .then(response => response.json())
            .then(data => {
                if (data && data.chess_blitz && data.chess_bullet && data.chess_rapid) {
                    const { chess_blitz, chess_bullet, chess_rapid } = data;
                    const statsHTML = `
                        <h2>Chess.com Stats for ${username}</h2>
                        <p><strong>Blitz:</strong> ${chess_blitz.last.rating}</p>
                        <p><strong>Bullet:</strong> ${chess_bullet.last.rating}</p>
                        <p><strong>Rapid:</strong> ${chess_rapid.last.rating}</p>
                    `;
                    statsDiv.innerHTML = statsHTML;
                } else {
                    statsDiv.innerHTML = '<p>Stats not available for the user.</p>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                statsDiv.innerHTML = '<p>There was an error fetching the data. Please try again later.</p>';
            });
    });
}
