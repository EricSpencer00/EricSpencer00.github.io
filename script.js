function secretFunction() {
    confetti.start();
    setTimeout(function() {
        confetti.stop();
    }, 7000); // 7 seconds
}

function typeText(text, id, speed) {
    const container = document.getElementById(id);
    let index = 0;
    const startTime = performance.now();

    function type() {
        const currentTime = performance.now();
        const elapsedTime = currentTime - startTime;
        const expectedTime = index * speed;
        const remainingTime = Math.max(0, expectedTime - elapsedTime);

        const char = text[index++];
        const span = document.createElement('span');
        span.textContent = char;
        container.appendChild(span);

        if (index < text.length) {
            setTimeout(type, remainingTime);
        }
    }

    type();
}

function chessStats() { 
    document.addEventListener('DOMContentLoaded', function() {
        const username = 'EricSpencer00'
        const statsDiv = document.getElementById('stats');

        fetch(`https://api.chess.com/pub/player/${username}/stats`)
            .then(response => response.json())
            .then(data => {
                const { chess_blitz, chess_bullet, chess_rapid, chess_daily } = data;
                const statsHTML = `
                <h2>Chess.com Stats for ${username}</h2>
                <p><strong>Blitz:</strong> ${chess_blitz.last.rating}</p>
                <p><strong>Bullet:</strong> ${chess_bullet.last.rating}</p>
                <p><strong>Rapid:</strong> ${chess_rapid.last.rating}</p>
            `;
                statsDiv.textContent = `Rating: ${stats.last.rating}, Wins: ${stats.record.win}, Losses: ${stats.record.loss}, Draws: ${stats.record.draw}`;
            });
}




