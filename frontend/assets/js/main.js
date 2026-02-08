// Mobile menu
const btn = document.getElementById("btnMobileMenu");
const drawer = document.getElementById("mobileDrawer");

if (btn && drawer) {
  btn.addEventListener("click", () => {
    drawer.classList.toggle("open");
  });
}

// HERO carousel
(function heroCarousel(){
  const carousel = document.getElementById("heroCarousel");
  const slideA = document.getElementById("heroSlideA");
  const slideB = document.getElementById("heroSlideB");

  if (!carousel || !slideA || !slideB) return;

  const slides = [
    "./assets/img/hero.jpg",
    "./assets/img/hero2.jpg",
  ];

  slides.forEach(src => { const img = new Image(); img.src = src; });

  let idx = 0;
  let activeEl = slideA;
  let nextEl = slideB;
  let isAnimating = false;

  function setBg(el, url) {
    el.style.backgroundImage = `url('${url}')`;
  }

  setBg(activeEl, slides[idx]);
  setBg(nextEl, slides[(idx + 1) % slides.length]);

  const intervalMs = 5000;
  const animMs = 900;

  function slideOnce() {
    if (isAnimating || slides.length < 2) return;
    isAnimating = true;

    const nextIdx = (idx + 1) % slides.length;
    setBg(nextEl, slides[nextIdx]);

    carousel.classList.add("is-sliding");

    setTimeout(() => {
      carousel.classList.remove("is-sliding");

      const tmp = activeEl;
      activeEl = nextEl;
      nextEl = tmp;

      activeEl.classList.remove("hero-slide--next");
      activeEl.classList.add("hero-slide--active");

      nextEl.classList.remove("hero-slide--active");
      nextEl.classList.add("hero-slide--next");

      idx = nextIdx;

      isAnimating = false;
    }, animMs + 20);
  }

  setInterval(slideOnce, intervalMs);
})();
