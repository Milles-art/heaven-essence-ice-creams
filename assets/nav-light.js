/* Lightweight replacement for the React runtime on the copied pages.
   Header, mobile menu, active nav, scroll progress, full navigation and
   flavour filters — no framework required. */
(function () {
  var ROUTES = /^\/(flavours|our-story|events|gallery|visit|faq)(\/|\?|$)/;
  document.addEventListener('click', function (e) {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (ROUTES.test(href)) {
      e.preventDefault();
      e.stopImmediatePropagation();
      window.location.href = href;
    }
  }, true);

  var header = document.querySelector('header > div');
  var bar = document.querySelector('.h-1.origin-left');
  function onScroll() {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? window.scrollY / h : 0) + ')';
    if (header) header.classList.toggle('bg-card/85', window.scrollY > 24);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var path = location.pathname.replace(/\/$/, '') || '/';
  document.querySelectorAll('header nav a').forEach(function (a) {
    if (a.getAttribute('href') === path || a.getAttribute('href') === path + '/') {
      a.setAttribute('data-status', 'active');
      a.setAttribute('aria-current', 'page');
    }
  });

  var btn = document.querySelector('button[aria-label="Open menu"]');
  if (btn) {
    var menu = document.createElement('div');
    menu.className = 'hidden fixed inset-x-3 top-[76px] z-50 rounded-[1.5rem] bg-card p-4 shadow-2xl ring-1 ring-border lg:hidden';
    menu.innerHTML = '<nav class="flex flex-col gap-1">' +
      Array.prototype.map.call(document.querySelectorAll('header nav a'), function (a) {
        return '<a href="' + a.getAttribute('href') + '" class="rounded-xl px-4 py-3 text-sm font-medium hover:bg-accent hover:text-accent-foreground">' + a.textContent + '</a>';
      }).join('') +
      '<a href="https://wa.me/255768641810?text=Hello%20Heaven%20Essence!" target="_blank" rel="noreferrer" class="mt-2 rounded-xl bg-primary px-4 py-3 text-center text-sm font-medium text-primary-foreground">Order on WhatsApp</a></nav>';
    document.body.appendChild(menu);
    btn.addEventListener('click', function () {
      var open = menu.classList.toggle('hidden') === false;
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      btn.setAttribute('aria-expanded', String(open));
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) { menu.classList.add('hidden'); btn.setAttribute('aria-label', 'Open menu'); btn.setAttribute('aria-expanded', 'false'); }
    });
  }

  // Flavour menu filters
  var tabs = document.querySelectorAll('[data-filter]');
  if (tabs.length) {
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        var f = tab.getAttribute('data-filter');
        tabs.forEach(function (t) {
          var on = t === tab;
          t.closest('button').setAttribute('aria-selected', String(on));
          t.closest('button').classList.toggle('bg-primary', on);
          t.closest('button').classList.toggle('text-primary-foreground', on);
        });
        document.querySelectorAll('article[data-cat]').forEach(function (art) {
          art.style.display = (f === 'all' || art.getAttribute('data-cat') === f) ? '' : 'none';
        });
      });
    });
  }
})();
