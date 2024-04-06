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




