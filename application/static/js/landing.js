(() => {
  const nav = document.querySelector(".nav-links");
  const navToggle = document.querySelector(".nav-toggle");

  if (nav && navToggle) {
    navToggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
      navToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
    });

    nav.addEventListener("click", (event) => {
      if (event.target instanceof Element && event.target.closest("a")) {
        nav.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        navToggle.setAttribute("aria-label", "Open navigation");
      }
    });
  }

  const password = document.querySelector("#password");
  const passwordToggle = document.querySelector(".password-toggle");
  if (password instanceof HTMLInputElement && passwordToggle instanceof HTMLButtonElement) {
    passwordToggle.addEventListener("click", () => {
      const showPassword = password.type === "password";
      password.type = showPassword ? "text" : "password";
      passwordToggle.textContent = showPassword ? "Hide" : "Show";
      passwordToggle.setAttribute("aria-label", showPassword ? "Hide password" : "Show password");
      passwordToggle.setAttribute("aria-pressed", String(showPassword));
    });
  }

  const loginError = document.querySelector("#login-error");
  if (loginError) {
    loginError.scrollIntoView({ block: "center" });
    document.querySelector("#email")?.focus({ preventScroll: true });
  }
})();
