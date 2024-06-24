function secretFunction() {
    confetti.start();
    setTimeout(function() {
        confetti.stop();
    }, 7000); // 7 seconds
}

function typeText(text, id, speed) {
    const container = document.getElementById(id);
    container.innerHTML = ''; // Clear the container

    // Pre-allocate lines
    const lines = text.split('');
    lines.forEach(() => {
        const line = document.createElement('div');
        container.appendChild(line);
    });

    const cursor = document.createElement('span');
    cursor.textContent = '|';
    cursor.style.animation = 'blink 1s step-end infinite';
    container.appendChild(cursor);

    let index = 0;
    const startTime = performance.now();

    function type() {
        const currentTime = performance.now();
        const elapsedTime = currentTime - startTime;
        const expectedTime = index * speed;
        const remainingTime = Math.max(0, expectedTime - elapsedTime);

        const char = text[index++];
        if (char === '\n') {
            cursor.parentElement.appendChild(cursor);
        } else {
            const span = document.createElement('span');
            span.textContent = char;
            cursor.parentElement.insertBefore(span, cursor);
        }

        if (index < text.length) {
            setTimeout(type, remainingTime);
        } else {
            cursor.style.animation = 'blink 1s step-end infinite';
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
    pre {
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
