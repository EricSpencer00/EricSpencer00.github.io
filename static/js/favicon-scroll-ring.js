(function () {
  const SIZE = 64;
  const canvas = document.createElement('canvas');
  canvas.width = SIZE;
  canvas.height = SIZE;
  const ctx = canvas.getContext('2d');

  // Remove every static <link rel="icon"> so the browser can't prefer a
  // different size over the one we draw. Keep a single dynamic link.
  document.querySelectorAll("link[rel~='icon'], link[rel='shortcut icon'], link[rel='apple-touch-icon']").forEach(el => el.remove());
  const link = document.createElement('link');
  link.rel = 'icon';
  link.type = 'image/png';
  document.head.appendChild(link);

  const getAccent = () => {
    const styles = getComputedStyle(document.documentElement);
    const primary = styles.getPropertyValue('--primary').trim();
    return primary || (matchMedia('(prefers-color-scheme: dark)').matches ? '#dadadb' : '#1d1e20');
  };
  const getBg = () => {
    const styles = getComputedStyle(document.documentElement);
    const theme = styles.getPropertyValue('--theme').trim();
    return theme || (matchMedia('(prefers-color-scheme: dark)').matches ? '#1d1e20' : '#ffffff');
  };

  let lastProgress = -1;

  function getScrollProgress() {
    const doc = document.documentElement;
    const scrollable = (doc.scrollHeight - doc.clientHeight) || 0;
    if (scrollable <= 0) return 0;
    const y = window.scrollY || doc.scrollTop || 0;
    return Math.min(1, Math.max(0, y / scrollable));
  }

  function draw(progress) {
    const cx = SIZE / 2;
    const cy = SIZE / 2;
    const r = SIZE / 2 - 6;
    const accent = getAccent();
    const bg = getBg();

    ctx.clearRect(0, 0, SIZE, SIZE);

    ctx.beginPath();
    ctx.arc(cx, cy, r + 3, 0, Math.PI * 2);
    ctx.fillStyle = bg;
    ctx.fill();

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.lineWidth = 6;
    ctx.strokeStyle = accent;
    ctx.globalAlpha = 0.18;
    ctx.stroke();

    ctx.globalAlpha = 1;
    ctx.beginPath();
    const start = -Math.PI / 2;
    ctx.arc(cx, cy, r, start, start + Math.PI * 2 * progress);
    ctx.lineWidth = 6;
    ctx.strokeStyle = accent;
    ctx.lineCap = 'round';
    ctx.stroke();

    ctx.fillStyle = accent;
    ctx.font = 'bold 22px -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('E', cx, cy + 1);

    link.href = canvas.toDataURL('image/png');
  }

  function tick() {
    const p = getScrollProgress();
    const quantized = Math.round(p * 60) / 60;
    if (quantized !== lastProgress) {
      lastProgress = quantized;
      draw(quantized);
    }
  }

  let rafScheduled = false;
  function onScroll() {
    if (rafScheduled) return;
    rafScheduled = true;
    requestAnimationFrame(() => {
      rafScheduled = false;
      tick();
    });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  window.addEventListener('load', tick);
  if (window.matchMedia) {
    matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', () => {
      lastProgress = -1;
      tick();
    });
  }
  document.addEventListener('themeChanged', () => {
    lastProgress = -1;
    tick();
  });

  tick();
})();
