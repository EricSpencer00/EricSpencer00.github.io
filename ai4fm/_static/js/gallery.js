document.addEventListener('DOMContentLoaded', function () {
  const galleries = document.querySelectorAll('.ai4fm-gallery');
  galleries.forEach(gallery => {
    const imgs = Array.from(gallery.querySelectorAll('.thumbs img'));
    const main = gallery.querySelector('.main-img');
    const prev = gallery.querySelector('.g-prev');
    const next = gallery.querySelector('.g-next');
    let idx = 0;
    function show(i) {
      if (i < 0) i = imgs.length - 1;
      if (i >= imgs.length) i = 0;
      idx = i;
      const src = imgs[i].getAttribute('data-full');
      main.setAttribute('src', src);
      imgs.forEach(im => im.classList.remove('active'));
      imgs[i].classList.add('active');
    }
    imgs.forEach((im, i) => {
      im.addEventListener('click', () => show(i));
    });
    prev && prev.addEventListener('click', () => show(idx - 1));
    next && next.addEventListener('click', () => show(idx + 1));
    // init
    if (imgs.length) {
      imgs.forEach(im => {
        const full = im.getAttribute('data-full');
        if (!full) im.setAttribute('data-full', im.getAttribute('src'));
      });
      show(0);
    }
  });
});
