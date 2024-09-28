var themeToggleDarkIcon = document.getElementById("theme-toggle-dark-icon");
var themeToggleLightIcon = document.getElementById("theme-toggle-light-icon");
var themeToggleBtns = document.querySelectorAll("#theme-toggle");

// Change the icons inside the button based on previous settings
if (
  localStorage.getItem("color-theme") === "dark" ||
  (!("color-theme" in localStorage) &&
    window.matchMedia("(prefers-color-scheme: dark)").matches)
) {
  themeToggleLightIcon.classList.add("opacity-40");
  themeToggleDarkIcon.classList.remove("opacity-40");
  themeToggleBtns.forEach((themeToggleBtn) => (themeToggleBtn.checked = false));
} else {
  themeToggleDarkIcon.classList.add("opacity-40");
  themeToggleLightIcon.classList.remove("opacity-40");
  themeToggleBtns.forEach((themeToggleBtn) => (themeToggleBtn.checked = true));
}

themeToggleBtns.forEach((themeToggleBtn) =>
  themeToggleBtn.addEventListener("click", function () {
    themeToggleDarkIcon.classList.toggle("opacity-40");
    themeToggleLightIcon.classList.toggle("opacity-40");

    // if set via local storage previously
    if (localStorage.getItem("color-theme")) {
      if (localStorage.getItem("color-theme") === "light") {
        document.documentElement.classList.add("dark");
        localStorage.setItem("color-theme", "dark");
      } else {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("color-theme", "light");
      }

      // if NOT set via local storage previously
    } else {
      if (document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("color-theme", "light");
      } else {
        document.documentElement.classList.add("dark");
        localStorage.setItem("color-theme", "dark");
      }
    }
  })
);
