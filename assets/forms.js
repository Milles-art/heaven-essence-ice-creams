/* Submit site forms to the Django API through the same-origin /api proxy. */
(function () {
  // On cPanel the API usually lives on a subdomain. The meta tag is patched
  // at deploy time; when empty, requests stay same-origin (local / tunnel).
  var baseMeta = document.querySelector('meta[name="heaven-api-base"]');
  var API_BASE = ((baseMeta && baseMeta.getAttribute('content')) || '').replace(/\/$/, '');

  document.querySelectorAll('form[data-endpoint]').forEach(function (form) {
    var button = form.querySelector('[type="submit"]');
    var msg = form.querySelector('.form-msg');

    function say(text, kind) {
      if (!msg) return;
      msg.textContent = text;
      msg.className = 'form-msg show ' + (kind || 'ok');
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var payload = {};
      new FormData(form).forEach(function (value, key) { payload[key] = value; });
      // Only numeric/date fields need null for "empty"; text fields accept "".
      form.querySelectorAll('input[type="date"], input[type="number"]').forEach(function (input) {
        if (payload[input.name] === '') payload[input.name] = null;
      });

      var original = button ? button.textContent : '';
      if (button) { button.disabled = true; button.textContent = 'Sending…'; }
      say('');

      fetch(API_BASE + form.getAttribute('data-endpoint'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function (res) {
          return res.json().catch(function () { return {}; }).then(function (data) {
            return { ok: res.ok, data: data };
          });
        })
        .then(function (result) {
          if (result.ok) {
            say(form.getAttribute('data-success') || 'Thank you! We’ll be in touch soon.', 'ok');
            form.reset();
          } else {
            var data = result.data;
            var problems = [];
            Object.keys(data).forEach(function (key) {
              var v = data[key];
              if (Array.isArray(v)) problems.push(key + ': ' + v.join(' '));
              else if (typeof v === 'string' && key !== 'detail') problems.push(v);
            });
            say(problems.length ? problems.join(' · ') : (data.detail || 'Something went wrong. Please try again.'), 'err');
          }
        })
        .catch(function () { say('Could not reach us right now. Please try WhatsApp instead.', 'err'); })
        .finally(function () {
          if (button) { button.disabled = false; button.textContent = original; }
        });
    });
  });
})();
