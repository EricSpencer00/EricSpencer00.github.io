function secretFunction() {
    confetti.start();
    // Stop
    setTimeout(function() {
        confetti.stop();
    }, 7000); // 7 seconds
}

function typeText(text, id, speed) {
    const container = document.getElementById(id);
    let index = 0;

    function type() {
        const char = text[index++];
        container.textContent += char;
        if (index < text.length) {
            setTimeout(type, speed);
        }
    }

    type();
}



