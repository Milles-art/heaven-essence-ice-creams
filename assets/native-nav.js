/* React Router intercepts same-origin links and renders its own route
   components. Force a real page load so the designed static pages are used. */
(function () {
  var ROUTES = /^\/(flavours|our-story|events|gallery|visit|faq)(\/|\?|$)/;
  document.addEventListener('click', function (event) {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var anchor = event.target && event.target.closest ? event.target.closest('a') : null;
    if (!anchor) return;
    var href = anchor.getAttribute('href') || '';
    if (!ROUTES.test(href)) return;
    event.preventDefault();
    event.stopImmediatePropagation(); // runs in capture phase, before React's handler
    window.location.href = href;
  }, true);
})();
