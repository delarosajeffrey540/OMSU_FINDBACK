document.querySelectorAll(".auth-brand img[data-fallback]").forEach((logo) => {
  const useOnlineFallback = () => {
    logo.src = logo.dataset.fallback;
  };

  if (logo.complete && !logo.naturalWidth) {
    useOnlineFallback();
  } else {
    logo.addEventListener("error", useOnlineFallback, { once: true });
  }
});