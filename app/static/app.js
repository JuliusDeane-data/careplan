// Bestätigungsdialoge für destruktive Aktionen + Lade-Hinweis für den Solver.
document.addEventListener("submit", function (event) {
  const form = event.target;
  const message = form.getAttribute("data-confirm");
  if (message && !window.confirm(message)) {
    event.preventDefault();
    return;
  }
  const button = form.querySelector("button[data-loading]");
  if (button) {
    button.textContent = button.getAttribute("data-loading");
    // Deaktivieren erst nach dem Absenden, damit der Klick noch zählt.
    setTimeout(() => { button.disabled = true; }, 0);
  }
});
