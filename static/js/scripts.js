
document.addEventListener("DOMContentLoaded", function () {
  const toggles = document.querySelectorAll('[data-bs-toggle="collapse"]');
  toggles.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = document.querySelector(btn.dataset.bsTarget);
      if (target) {
        target.classList.toggle("show");
      }
    });
  });
});
