function secretFunction() {
    confetti.start();
    setTimeout(function() {
        confetti.stop();
    }, 7000); // 7 seconds
}

function typeText(text, id, speed, includeCursor = false) {
    const container = document.getElementById(id);
    container.innerHTML = ''; // Clear the container

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
        cursor.textContent = '|';
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
