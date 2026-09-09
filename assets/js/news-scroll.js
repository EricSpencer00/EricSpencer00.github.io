(() => {
  // A fresh conversation opens at the latest message. Preserve explicit anchors
  // and browser back/forward restoration, and never fight someone scrolling up.
  const navigation = performance.getEntriesByType('navigation')[0];
  if (location.hash || navigation?.type === 'back_forward') return;
  let interacted = false;
  for (const event of ['wheel', 'touchstart', 'pointerdown', 'keydown']) {
    window.addEventListener(event, () => { interacted = true; }, { once: true, passive: true });
  }
  const showLatest = () => {
    if (!interacted) window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' });
  };
  showLatest();
  requestAnimationFrame(showLatest);
  window.addEventListener('load', showLatest, { once: true });
  document.fonts?.ready.then(showLatest);
})();
