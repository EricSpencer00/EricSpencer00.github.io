---
title: "Home"
---

{{< rawhtml >}}
<div id="ascii-art"></div>
<script src="/js/script.js"></script>
<script>
  // Example usage: display a random ASCII art from asciiNameArray
  document.addEventListener("DOMContentLoaded", function() {
    const art = getRandomAsciiArt();
    typeText2dArray([art], "ascii-art", 10); // Adjust speed as desired
  });
</script>
{{< /rawhtml >}}