/* Persist the sidebar's collapsed/open state across pages.
   A restore script at the top of <body> re-applies the saved class
   before AdminLTE's own init runs, so the drawer does not flash
   open on every navigation. This observer then saves each change
   AdminLTE makes (toggle clicks, and its mobile collapse on load).
   AdminLTE's own persistence is off; this is the project's own key,
   "at-sidebar", deliberately separate from the theme key. */
(function () {
  function save() {
    try {
      if (document.body.classList.contains("sidebar-collapse")) {
        localStorage.setItem("at-sidebar", "collapsed");
      } else if (document.body.classList.contains("sidebar-open")) {
        localStorage.setItem("at-sidebar", "open");
      } else {
        localStorage.removeItem("at-sidebar");
      }
    } catch (e) {}
  }
  var observer = new MutationObserver(function (mutations) {
    for (var i = 0; i < mutations.length; i++) {
      if (mutations[i].attributeName === "class") { save(); return; }
    }
  });
  observer.observe(document.body, {attributes: true});
})();
