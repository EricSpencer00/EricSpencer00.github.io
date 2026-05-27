document.addEventListener("DOMContentLoaded", function() {
    const maxForm = document.getElementById('maxForm');
    if (maxForm) {
        maxForm.addEventListener('submit', function(event) {
            event.preventDefault();
            calculateMax();
        });
    }

    function calculateMax() {
        const reps = parseFloat(document.getElementById('reps').value);
        const weight = parseFloat(document.getElementById('weight').value);
        const unit = document.getElementById('unit').value;

        if (isNaN(reps) || isNaN(weight)) {
            document.getElementById('result').innerHTML =
              "<p style='color:red;'>Please enter valid numbers for weight and reps.</p>";
            return;
        }

        // Epley formula: One Rep Max = weight * (1 + reps/30)
        const oneRepMax = weight * (1 + reps / 30);
        const repMaxEstimates = generateRepMaxEstimates(oneRepMax, unit);
        document.getElementById('result').innerHTML = repMaxEstimates;
    }

    function generateRepMaxEstimates(oneRepMax, unit) {
        const estimates = [];
        estimates.push(`<li>Your One Rep Max is ${oneRepMax.toFixed(2)} ${unit}</li>`);
        estimates.push('<hr>');
        for (let i = 2; i <= 100; i++) {
            estimates.push(`<li>You can lift ${(oneRepMax / (1 + i/30)).toFixed(2)} ${unit} for ${i} reps</li>`);
        }
        return `<ul>${estimates.join("\n")}</ul>`;
    }
});
