
// Client-side search over a prebuilt index. No dependencies, no network calls
// beyond the one JSON fetch, so the site stays a static bundle.
(function () {
  var input = document.getElementById('q');
  var panel = document.getElementById('results');
  if (!input || !panel) return;

  var prefix = window.SEARCH_PREFIX || '';
  var docs = null;
  var selected = -1;

  function load() {
    if (docs) return Promise.resolve(docs);
    return fetch(prefix + 'search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (data) { docs = data; return docs; })
      .catch(function () { docs = []; return docs; });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // Score: title hits beat heading hits beat body hits. Every term must
  // appear somewhere, so multi-word queries narrow rather than widen.
  function score(doc, terms) {
    var title = doc.t.toLowerCase();
    var heads = doc.h.toLowerCase();
    var body = doc.b.toLowerCase();
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var term = terms[i];
      var hit = 0;
      if (title.indexOf(term) !== -1) hit += 12;
      if (heads.indexOf(term) !== -1) hit += 5;
      if (body.indexOf(term) !== -1) hit += 1;
      if (!hit) return 0;
      total += hit;
    }
    return total;
  }

  function highlight(text, term) {
    // indexOf rather than a RegExp: no need to escape the user's query,
    // which is where dynamic-regex search boxes usually break.
    var lower = text.toLowerCase();
    var out = '';
    var at = 0;
    for (;;) {
      var found = lower.indexOf(term, at);
      if (found === -1) { out += escapeHtml(text.slice(at)); break; }
      out += escapeHtml(text.slice(at, found));
      out += '<mark>' + escapeHtml(text.slice(found, found + term.length)) + '</mark>';
      at = found + term.length;
    }
    return out;
  }

  function snippet(doc, term) {
    var body = doc.b;
    var at = body.toLowerCase().indexOf(term);
    if (at === -1) return escapeHtml(body.slice(0, 120)) + '...';
    var start = Math.max(0, at - 55);
    var chunk = body.slice(start, start + 150);
    return (start ? '...' : '') + highlight(chunk, term) + '...';
  }

  function render(matches, terms) {
    if (!matches.length) {
      panel.innerHTML = '<p class="empty">No matches.</p>';
      panel.hidden = false;
      return;
    }
    panel.innerHTML = matches.slice(0, 12).map(function (m) {
      return '<a href="' + prefix + m.doc.u + '">' +
        '<span class="r-title">' + escapeHtml(m.doc.t) + '</span> ' +
        '<span class="r-sec">' + escapeHtml(m.doc.s || '') + '</span>' +
        '<div class="r-snip">' + snippet(m.doc, terms[0]) + '</div></a>';
    }).join('');
    panel.hidden = false;
    selected = -1;
  }

  function run() {
    var query = input.value.trim().toLowerCase();
    if (query.length < 2) { panel.hidden = true; return; }
    load().then(function (all) {
      var terms = query.split(/\s+/).filter(Boolean);
      var matches = [];
      for (var i = 0; i < all.length; i++) {
        var s = score(all[i], terms);
        if (s > 0) matches.push({ doc: all[i], s: s });
      }
      matches.sort(function (a, b) { return b.s - a.s; });
      render(matches, terms);
    });
  }

  input.addEventListener('input', run);
  input.addEventListener('focus', function () { if (input.value.trim().length > 1) run(); });

  document.addEventListener('click', function (event) {
    if (!panel.contains(event.target) && event.target !== input) panel.hidden = true;
  });

  // Keyboard: / focuses search, arrows move, Enter opens, Escape closes.
  document.addEventListener('keydown', function (event) {
    if (event.key === '/' && document.activeElement !== input) {
      event.preventDefault();
      input.focus();
      return;
    }
    if (panel.hidden) return;
    var links = panel.querySelectorAll('a');
    if (event.key === 'Escape') { panel.hidden = true; input.blur(); }
    else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (!links.length) return;
      if (selected >= 0) links[selected].classList.remove('sel');
      selected = event.key === 'ArrowDown'
        ? (selected + 1) % links.length
        : (selected - 1 + links.length) % links.length;
      links[selected].classList.add('sel');
      links[selected].scrollIntoView({ block: 'nearest' });
    } else if (event.key === 'Enter' && selected >= 0 && links[selected]) {
      window.location.href = links[selected].getAttribute('href');
    }
  });
})();
