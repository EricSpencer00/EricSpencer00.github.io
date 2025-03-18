---
title: "One Rep Max Calculator"
date: 2024-04-15
description: "Calculate your One Rep Max"
tags: ["calculator", "web development", "wellness"]
categories: ["Projects"]
image: "../Images/logo.png"
draft: false
---

This tool uses **Epley's Formula** to estimate your one rep max. Enter the weight you lifted, the number of reps you performed, and select your unit (lbs or kgs). Then click **Calculate 1RM**.

<div style="margin: 1em 0;">
  <label for="weight">Weight:</label>
  <input type="number" id="weight" name="weight" placeholder="Enter weight" step="any" style="margin:0 1em 0 0;">
  
  <label for="unit">Unit:</label>
  <select id="unit" name="unit" style="margin:0 1em 0 0;">
    <option value="lbs">lbs</option>
    <option value="kgs">kgs</option>
  </select>
  
  <label for="reps">Reps:</label>
  <input type="number" id="reps" name="reps" placeholder="Enter reps" style="margin:0 1em 0 0;">
  
  <button id="calculateBtn">Calculate 1RM</button>
</div>

<div id="result" style="margin-top: 1em; font-weight: bold;"></div>

<script>
// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById('calculateBtn').addEventListener('click', function(){
    // Get input values
    var weight = parseFloat(document.getElementById('weight').value);
    var reps = parseFloat(document.getElementById('reps').value);
    var unit = document.getElementById('unit').value;

    // Validate inputs
    if (isNaN(weight) || isNaN(reps) || weight <= 0 || reps <= 0) {
      document.getElementById('result').innerHTML = "<p>Please enter valid numbers for weight and reps.</p>";
      return;
    }

    // Epley's formula: 1RM = weight * (1 + reps/30)
    var oneRepMax = weight * (1 + reps / 30);

    // Display the result
    document.getElementById('result').innerHTML = "<p>Your estimated 1RM is " + oneRepMax.toFixed(2) + " " + unit + ".</p>";
  });
});
</script>

---

This was converted from html/js to md, view the original here:
[1RM Calculator](https://EricSpencer00.github.io/old-site/Projects/OneRepMax.html)
