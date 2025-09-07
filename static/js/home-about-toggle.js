document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('about-toggle');
  var full = document.getElementById('about-full');
  if (!btn || !full) return;

  btn.addEventListener('click', function () {
    var expanded = btn.getAttribute('aria-expanded') === 'true';
    if (expanded) {
      full.setAttribute('aria-hidden', 'true');
      btn.setAttribute('aria-expanded', 'false');
      btn.textContent = 'Show more ↓';
      full.classList.remove('expanded');
    } else {
      full.setAttribute('aria-hidden', 'false');
      btn.setAttribute('aria-expanded', 'true');
      btn.textContent = 'Show less ↑';
      full.classList.add('expanded');
      // smooth scroll to newly revealed section
      full.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });
});
