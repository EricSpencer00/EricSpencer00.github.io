document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('about-toggle');
  var full = document.getElementById('about-full');
  if (!btn || !full) return;

  // If the toggle is an anchor link, don't intercept its click (let it navigate).
  if (btn.tagName.toLowerCase() === 'a') return;

  // Otherwise keep the expand/collapse behavior for buttons.
  btn.addEventListener('click', function (e) {
    var expanded = btn.getAttribute('aria-expanded') === 'true';
    if (expanded) {
      full.setAttribute('aria-hidden', 'true');
      btn.setAttribute('aria-expanded', 'false');
      btn.textContent = 'Show more \u2193';
      full.classList.remove('expanded');
    } else {
      full.setAttribute('aria-hidden', 'false');
      btn.setAttribute('aria-expanded', 'true');
      btn.textContent = 'Show less \u2191';
      full.classList.add('expanded');
      // smooth scroll to newly revealed section
      full.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });
});
