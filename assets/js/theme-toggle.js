/* Theme toggle, same key ("at-theme") on hub and game pages.
   The before-first-paint script in <head> sets the initial theme;
   this script only handles the button. It must stay a shared file,
   not an inline copy in each template, or the two copies will drift. */
(function () {
  var button = document.getElementById("theme-toggle");
  if (!button) return;
  /* The icon shows the mode a tap would switch to, matching the
     icon-only sidebar toggle and note buttons: moon in light
     mode, sun in dark mode. */
  function label() {
    var dark = document.documentElement.getAttribute("data-bs-theme") === "dark";
    var icon = button.querySelector("i");
    if (icon) icon.className = dark ? "bi bi-sun-fill" : "bi bi-moon-fill";
    button.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
  }
  button.addEventListener("click", function () {
    var next = document.documentElement.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-bs-theme", next);
    try { localStorage.setItem("at-theme", next); } catch (e) {}
    label();
  });
  label();
})();
