document.querySelectorAll("[data-password-toggle]").forEach((toggle) => {
  toggle.addEventListener("click", () => {
    const field = toggle.closest(".password-field")?.querySelector("input");
    if (!field) return;

    const showPassword = field.type === "password";
    field.type = showPassword ? "text" : "password";
    toggle.textContent = showPassword ? "Hide" : "Show";
    toggle.setAttribute("aria-label", showPassword ? "Hide password" : "Show password");
    toggle.setAttribute("aria-pressed", String(showPassword));
  });
});