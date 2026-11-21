/* =========================================================
   Smart IT Help Desk Management System
   static/js/main.js - small reusable front-end helpers
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  /* ---------- 1. Bootstrap-style client-side form validation ---------- */
  document.querySelectorAll("form.needs-validation").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    });
  });

  /* ---------- 2. Confirmation before destructive actions ---------- */
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var message = form.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });

  /* ---------- 3. Auto-hide flash messages after 6 seconds ---------- */
  document.querySelectorAll(".flash-stack .alert").forEach(function (alert) {
    window.setTimeout(function () {
      alert.classList.remove("show");
      window.setTimeout(function () { alert.remove(); }, 300);
    }, 6000);
  });

  /* ---------- 4. Show / hide password on the login page ---------- */
  var toggle = document.getElementById("togglePassword");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var input = document.getElementById("password");
      if (!input) return;
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      toggle.innerHTML = show
        ? '<i class="bi bi-eye-slash"></i>'
        : '<i class="bi bi-eye"></i>';
    });
  }

  /* ---------- 5. Mobile sidebar ---------- */
  var sidebar = document.getElementById("sidebar");
  var backdrop = document.getElementById("sidebarBackdrop");
  var toggleBtn = document.getElementById("sidebarToggle");

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove("open");
    if (backdrop) backdrop.classList.remove("show");
  }

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", function () {
      sidebar.classList.toggle("open");
      if (backdrop) backdrop.classList.toggle("show");
    });
  }
  if (backdrop) backdrop.addEventListener("click", closeSidebar);
  if (sidebar) {
    sidebar.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeSidebar);
    });
  }
});
