function secretFunction() {
    confetti.start();
    // Stop
    setTimeout(function() {
        confetti.stop();
    }, 7000); // 7 seconds
}

document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('start-button');
    const reactionTest = document.getElementById('reaction-test');
    let startTime, endTime;

    startButton.addEventListener('click', function() {
        // Change button color to signal user to react
        startButton.style.backgroundColor = 'red';
        startButton.textContent = 'Click!';

        // Record start time when color changes
        startTime = new Date().getTime();

        // Change color again after random time interval
        setTimeout(function() {
            startButton.style.backgroundColor = 'green';
            startButton.textContent = 'Start';

            // Record end time when color changes again
            endTime = new Date().getTime();

            // Calculate reaction time
            const reactionTime = endTime - startTime;

            // Display reaction time to user
            reactionTest.innerHTML = `<p>Your reaction time: <strong>${reactionTime} milliseconds</strong></p>`;
        }, Math.floor(Math.random() * 3000) + 1000); // Random time between 1 to 4 seconds
    });
});
