(() => {
  const carousel = document.querySelector('.hero-carousel.splide');

  if (!carousel || !window.Splide) {
    return;
  }

  new window.Splide(carousel, {
    type: 'fade',
    rewind: true,
    autoplay: true,
    interval: 6500,
    speed: 700,
    rewindSpeed: 700,
    arrows: false,
    pagination: false,
    keyboard: false,
    drag: false,
    live: false,
  }).mount();
})();
