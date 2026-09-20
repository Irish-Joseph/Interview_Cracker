"""Generate a searchable static site in docs/ from the Markdown sources.

Usage:
    pip install markdown pymdown-extensions pygments jinja2
    python scripts/build_site.py

The Markdown in interview-prep/, coding-challenges/ and daily-challenges/ is
the single source of truth. This script renders it to docs/, which GitHub
Pages serves. Edit the Markdown, never the generated HTML.

Why a site: the question banks are only findable through GitHub search today.
As indexed HTML pages they become findable through a search engine, which is
the difference between a repository people stumble on and one they arrive at.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import markdown
    from jinja2 import Environment
except ImportError:  # pragma: no cover
    print("Install deps:  pip install markdown pymdown-extensions pygments jinja2",
          file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"

SITE_NAME = "Interview Cracker"
SITE_TAGLINE = "Interview prep that explains why an answer is right"
BASE_URL = "https://irish-joseph.github.io/Interview_Cracker"
REPO_URL = "https://github.com/Irish-Joseph/Interview_Cracker"
REPO_BLOB = REPO_URL + "/blob/main"

# Sections rendered into the site, in nav order.
SECTIONS = [
    ("interview-prep", "Interview Prep"),
    ("coding-challenges", "Coding Challenges"),
    ("daily-challenges", "Daily Challenges"),
]

SUBJECT_TITLES = {
    "data-structures": "Data Structures",
    "algorithms": "Algorithms",
    "databases": "Databases",
    "core-cs": "Core Computer Science",
    "system-design": "System Design",
    "languages": "Language Specific",
    "behavioral": "Behavioural",
}

DIFFICULTY = {"\U0001f7e2": "easy", "\U0001f7e1": "medium", "\U0001f534": "hard"}


@dataclass
class Page:
    src: Path                 # source markdown, relative to ROOT
    url: str                  # site-relative url, e.g. interview-prep/x/y.html
    title: str
    section: str
    group: str
    body: str = ""
    description: str = ""
    headings: list[str] = field(default_factory=list)
    text: str = ""


def make_markdown() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=[
            "extra",              # tables, fenced code, footnotes, attr_list
            "toc",
            "sane_lists",
            "md_in_html",
            "pymdownx.superfences",
            "pymdownx.highlight",
            "pymdownx.betterem",
        ],
        extension_configs={
            "pymdownx.highlight": {
                "css_class": "highlight",
                "guess_lang": False,
            },
            "toc": {"permalink": False},
        },
        output_format="html5",
    )


def first_paragraph(md_text: str) -> str:
    """A one-line description for <meta> and the search index."""
    for block in md_text.split("\n\n"):
        block = block.strip()
        if not block or block.startswith(("#", "|", "```", ">", "-", "*", "<")):
            continue
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", block)
        clean = re.sub(r"[*`_]", "", clean).replace("\n", " ")
        clean = re.sub(r"\s+", " ", clean).strip()
        if len(clean) > 40:
            return (clean[:180] + "...") if len(clean) > 180 else clean
    return SITE_TAGLINE


def page_title(md_text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    if match:
        return re.sub(r"[*`]", "", match.group(1)).strip()
    return fallback


def collect_pages() -> list[Page]:
    pages: list[Page] = []

    for section, section_title in SECTIONS:
        base = ROOT / section
        if not base.is_dir():
            continue
        for md_path in sorted(base.rglob("*.md")):
            rel = md_path.relative_to(ROOT)
            parts = rel.parts

            # Group = the subfolder, or the section itself for a top-level file.
            if len(parts) >= 3:
                group = SUBJECT_TITLES.get(parts[1], parts[1].replace("-", " ").title())
            else:
                group = section_title

            slug = rel.with_suffix(".html").as_posix()
            text = md_path.read_text(encoding="utf-8")
            fallback = md_path.stem.replace("-", " ").replace("_", " ").title()

            pages.append(Page(
                src=rel,
                url=slug,
                title=page_title(text, fallback),
                section=section_title,
                group=group,
            ))

    return pages


def rewrite_links(body_html: str, page_url: str, known: set[str]) -> str:
    """Point .md links at the generated pages, everything else at GitHub."""
    depth = page_url.count("/")
    prefix = "../" * depth

    def fix(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)

        anchor = ""
        if "#" in href:
            href, anchor = href.split("#", 1)
            anchor = "#" + anchor
        if not href:
            return match.group(0)

        # Resolve relative to the page's own directory.
        target = (Path(page_url).parent / href).as_posix()
        target = re.sub(r"[^/]+/\.\./", "", target)
        while "/./" in target:
            target = target.replace("/./", "/")
        target = target.lstrip("./")

        if target.endswith(".md"):
            as_html = target[:-3] + ".html"
            if as_html in known:
                return 'href="{}{}{}"'.format(prefix, as_html, anchor)
            # A markdown file outside the site (README, CONTRIBUTING, ...)
            return 'href="{}/{}{}"'.format(REPO_BLOB, target, anchor)

        # Source files, folders and PDFs live on GitHub.
        return 'href="{}/{}{}"'.format(REPO_BLOB, target.rstrip("/"), anchor)

    return re.sub(r'href="([^"]+)"', fix, body_html)


def plain_text(body_html: str) -> str:
    text = re.sub(r"<(script|style).*?</\1>", " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% if page.title == site_name %}{{ site_name }} &mdash; {{ tagline }}{% else %}{{ page.title }} &middot; {{ site_name }}{% endif %}</title>
<meta name="description" content="{{ page.description }}">
<link rel="canonical" href="{{ base_url }}/{{ page.url }}">
<meta property="og:type" content="article">
<meta property="og:title" content="{% if page.title == site_name %}{{ site_name }}{% else %}{{ page.title }} &middot; {{ site_name }}{% endif %}">
<meta property="og:description" content="{{ page.description }}">
<meta property="og:url" content="{{ base_url }}/{{ page.url }}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{{ prefix }}assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#127891;</text></svg>">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <a class="brand" href="{{ prefix }}index.html">{{ site_name }}</a>
  <input id="q" type="search" placeholder="Search {{ page_count }} pages&hellip;" autocomplete="off" aria-label="Search">
  <a class="ghlink" href="{{ repo_url }}" rel="noopener">GitHub</a>
</header>
<div id="results" hidden></div>
<div class="layout">
  <nav class="sidebar" aria-label="Sections">
    {% for section, groups in nav %}
    <div class="navsection"><span class="navtitle">{{ section }}</span>
      {% for group, items in groups %}
      <div class="navgroup">
        {% if group != section %}<span class="navgroup-title">{{ group }}</span>{% endif %}
        <ul>
        {% for item in items %}
          <li><a href="{{ prefix }}{{ item.url }}"{% if item.url == page.url %} class="current" aria-current="page"{% endif %}>{{ item.title }}</a></li>
        {% endfor %}
        </ul>
      </div>
      {% endfor %}
    </div>
    {% endfor %}
  </nav>
  <main id="main" class="content">
    {{ page.body }}
    <hr>
    <p class="editlink">Found a mistake? <a href="{{ repo_blob }}/{{ page.src }}" rel="noopener">Edit this page on GitHub</a>.</p>
  </main>
</div>
<script>window.SEARCH_PREFIX={{ prefix | tojson }};</script>
<script src="{{ prefix }}assets/search.js" defer></script>
</body>
</html>
"""

INDEX_BODY = """
<h1>{site_name}</h1>
<p class="lede">{tagline}. Every question has a written answer, every challenge
has a commented solution with its complexity, and every concept links to a small
runnable program.</p>

<div class="cards">
  <a class="card" href="interview-prep/README.html">
    <h3>Interview Prep</h3>
    <p>{prep_count} subject question banks with full written answers &mdash; data
    structures, algorithms, databases, OS, networking, concurrency, system design,
    language-specific and behavioural.</p>
  </a>
  <a class="card" href="coding-challenges/README.html">
    <h3>Coding Challenges</h3>
    <p>Problems grouped by the <strong>pattern</strong> that solves them, each with
    a hint, a tested solution and its complexity.</p>
  </a>
  <a class="card" href="daily-challenges/README.html">
    <h3>Daily Challenges</h3>
    <p>One focused problem per day, with the answer collapsed so you can attempt
    it first.</p>
  </a>
  <a class="card" href="{repo_url}/tree/main/examples">
    <h3>150 Runnable Examples</h3>
    <p>One concept per file across 13 languages. Most print their own expected
    output, so you can change a line and see what happens.</p>
  </a>
</div>

<h2>Start here</h2>
<p>If your interview is soon, read
<a href="interview-prep/README.html">the study plans</a> &mdash; there is a
one-week and a four-week version. Then drill the challenges <em>by pattern</em>,
because recognising the pattern is the part that transfers.</p>

<h2>What makes this different</h2>
<ul>
<li><strong>Every code snippet has been executed</strong>, and cross-checked
against a brute-force reference on randomised inputs where practical.</li>
<li><strong>Complexity is stated and justified</strong>, including the space cost
of recursion.</li>
<li><strong>Trade-offs over rules.</strong> Where there is no single right answer,
the answer explains the choice.</li>
<li><strong>No invented company attributions.</strong> Nothing here claims to be
"asked at" any employer &mdash; those claims are not verifiable.</li>
</ul>
"""


def build_nav(pages: list[Page]) -> list:
    """[(section, [(group, [pages])])] preserving SECTIONS order."""
    nav = []
    for _, section_title in SECTIONS:
        in_section = [p for p in pages if p.section == section_title]
        if not in_section:
            continue
        groups: dict[str, list[Page]] = {}
        for page in in_section:
            groups.setdefault(page.group, []).append(page)
        # Put the section's own README first within its group.
        ordered = []
        for group, items in groups.items():
            items.sort(key=lambda p: (not p.src.name.lower().startswith("readme"),
                                      p.title.lower()))
            ordered.append((group, items))
        ordered.sort(key=lambda pair: (pair[0] != section_title, pair[0]))
        nav.append((section_title, ordered))
    return nav


def main() -> int:
    pages = collect_pages()
    if not pages:
        print("No Markdown sources found.", file=sys.stderr)
        return 1

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)

    known = {p.url for p in pages}
    converter = make_markdown()

    # Render each page's body once.
    for page in pages:
        md_text = (ROOT / page.src).read_text(encoding="utf-8")

        # GitHub renders Markdown inside <details> natively; Python-Markdown
        # needs markdown="1" to do the same. Injecting it here keeps the
        # source files plain, so they stay correct on GitHub either way.
        md_text = re.sub(r"<details(?![^>]*markdown=)([^>]*)>",
                         r'<details markdown="1">', md_text)
        md_text = re.sub(r"<summary(?![^>]*markdown=)([^>]*)>",
                         r'<summary markdown="1">', md_text)

        page.description = first_paragraph(md_text)
        converter.reset()
        body = converter.convert(md_text)
        body = rewrite_links(body, page.url, known)
        page.body = body
        page.headings = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", body, re.S)
        page.headings = [re.sub(r"<[^>]+>", "", h).strip() for h in page.headings]
        page.text = plain_text(body)

    nav = build_nav(pages)
    env = Environment(autoescape=False)
    template = env.from_string(PAGE_TEMPLATE)

    def render(page: Page) -> str:
        depth = page.url.count("/")
        return template.render(
            page=page, nav=nav, site_name=SITE_NAME, base_url=BASE_URL,
            repo_url=REPO_URL, repo_blob=REPO_BLOB, prefix="../" * depth,
            tagline=SITE_TAGLINE,
            page_count=len(pages) + 1,
        )

    for page in pages:
        target = OUT / page.url
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(page), encoding="utf-8")

    # Home page, rendered through the same template.
    prep_count = sum(1 for p in pages
                     if p.section == "Interview Prep"
                     and not p.src.name.lower().startswith("readme"))
    home = Page(src=Path("README.md"), url="index.html", title=SITE_NAME,
                section="", group="")
    home.description = (SITE_TAGLINE + ": question banks with written answers, "
                        "pattern-grouped coding challenges, and 150 runnable examples.")
    home.body = INDEX_BODY.format(site_name=SITE_NAME, tagline=SITE_TAGLINE,
                                  prep_count=prep_count, repo_url=REPO_URL)
    home.text = plain_text(home.body)
    (OUT / "index.html").write_text(render(home), encoding="utf-8")

    # Search index: title, headings and a truncated body per page.
    index = [
        {"u": p.url, "t": p.title, "s": p.section,
         "h": " ".join(p.headings)[:1500], "b": p.text[:4000]}
        for p in [home] + pages
    ]
    (OUT / "search-index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")

    # SEO plumbing.
    urls = "\n".join(
        "  <url><loc>{}/{}</loc></url>".format(BASE_URL, p.url)
        for p in [home] + pages)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(BASE_URL),
        encoding="utf-8")
    # .nojekyll stops GitHub Pages running Jekyll over already-built HTML.
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    (OUT / "assets" / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (OUT / "assets" / "search.js").write_text(SEARCH_JS, encoding="utf-8")

    print("wrote {} pages to {}/".format(len(pages) + 1, OUT.relative_to(ROOT)))
    print("  search index: {} entries".format(len(index)))
    print("  sitemap:      {} urls".format(len(index)))
    return 0


STYLE_CSS = """
:root {
  --bg: #ffffff; --fg: #1c1f24; --muted: #5b6672; --line: #e3e7ec;
  --accent: #14213d; --link: #0b5fa5; --code-bg: #f5f7fa; --card: #fbfcfd;
  --mark: #fff3bf;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f1216; --fg: #e6e9ee; --muted: #97a3b2; --line: #232a33;
    --accent: #cbd7ea; --link: #7fb2e5; --code-bg: #161b22; --card: #151a21;
    --mark: #554a1f;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        "Helvetica Neue", Arial, sans-serif;
  -webkit-text-size-adjust: 100%;
}
.skip { position: absolute; left: -9999px; }
.skip:focus { left: 8px; top: 8px; background: var(--bg); padding: 8px; z-index: 30; }

.topbar {
  position: sticky; top: 0; z-index: 20; display: flex; gap: 12px;
  align-items: center; padding: 10px 16px; background: var(--bg);
  border-bottom: 1px solid var(--line);
}
.brand { font-weight: 700; color: var(--fg); text-decoration: none; white-space: nowrap; }
.ghlink { color: var(--muted); text-decoration: none; font-size: 14px; white-space: nowrap; }
.ghlink:hover { color: var(--link); }
#q {
  flex: 1; min-width: 0; padding: 7px 11px; border: 1px solid var(--line);
  border-radius: 7px; background: var(--code-bg); color: var(--fg); font-size: 14px;
}
#q:focus { outline: 2px solid var(--link); outline-offset: 1px; }

#results {
  position: absolute; left: 0; right: 0; top: 52px; z-index: 19;
  max-height: 70vh; overflow-y: auto; background: var(--bg);
  border-bottom: 1px solid var(--line);
}
#results a { display: block; padding: 10px 16px; border-bottom: 1px solid var(--line);
  text-decoration: none; color: var(--fg); }
#results a:hover, #results a.sel { background: var(--code-bg); }
#results .r-title { font-weight: 600; color: var(--link); }
#results .r-sec { font-size: 12px; color: var(--muted); }
#results .r-snip { font-size: 13px; color: var(--muted); }
#results mark { background: var(--mark); color: inherit; }
#results .empty { padding: 14px 16px; color: var(--muted); }

.layout { display: flex; gap: 28px; max-width: 1180px; margin: 0 auto; padding: 0 16px; }
.sidebar {
  width: 250px; flex: 0 0 250px; padding: 22px 0 60px;
  position: sticky; top: 52px; align-self: flex-start;
  max-height: calc(100vh - 52px); overflow-y: auto;
}
.navtitle { display: block; font-size: 12px; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); margin: 16px 0 6px; }
.navgroup-title { display: block; font-size: 13px; font-weight: 600;
  color: var(--fg); margin: 10px 0 3px; }
.sidebar ul { list-style: none; margin: 0 0 6px; padding: 0 0 0 2px; }
.sidebar li { margin: 1px 0; }
.sidebar a { display: block; padding: 3px 8px; border-radius: 5px;
  color: var(--muted); text-decoration: none; font-size: 14px; }
.sidebar a:hover { background: var(--code-bg); color: var(--fg); }
.sidebar a.current { background: var(--code-bg); color: var(--link); font-weight: 600; }

.content { flex: 1; min-width: 0; padding: 22px 0 80px; }
.content h1 { font-size: 30px; line-height: 1.25; margin: 6px 0 14px; }
.content h2 { font-size: 22px; margin: 34px 0 10px; padding-bottom: 5px;
  border-bottom: 1px solid var(--line); }
.content h3 { font-size: 17px; margin: 26px 0 8px; color: var(--accent); }
.content p, .content li { overflow-wrap: break-word; }
.content a { color: var(--link); }
.lede { font-size: 18px; color: var(--muted); }

table { border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 14px;
  display: block; overflow-x: auto; }
th, td { border: 1px solid var(--line); padding: 7px 10px; text-align: left;
  vertical-align: top; }
th { background: var(--code-bg); }

code { background: var(--code-bg); padding: 1px 5px; border-radius: 4px;
  font-size: 90%; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
pre { background: var(--code-bg); border: 1px solid var(--line); border-radius: 8px;
  padding: 12px 14px; overflow-x: auto; font-size: 13.5px; line-height: 1.5; }
pre code { background: none; padding: 0; font-size: inherit; }
blockquote { margin: 14px 0; padding: 2px 16px; border-left: 3px solid var(--line);
  color: var(--muted); }
hr { border: 0; border-top: 1px solid var(--line); margin: 30px 0 14px; }
details { margin: 12px 0; border: 1px solid var(--line); border-radius: 8px;
  padding: 10px 14px; background: var(--card); }
summary { cursor: pointer; font-weight: 600; }
.editlink { font-size: 13px; color: var(--muted); }

.cards { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  margin: 22px 0; }
.card { display: block; padding: 16px 18px; border: 1px solid var(--line);
  border-radius: 10px; background: var(--card); text-decoration: none; color: inherit; }
.card:hover { border-color: var(--link); }
.card h3 { margin: 0 0 6px; color: var(--link); }
.card p { margin: 0; font-size: 14px; color: var(--muted); }

@media (max-width: 860px) {
  .layout { flex-direction: column; gap: 0; }
  .sidebar { width: 100%; flex: none; position: static; max-height: none;
    border-bottom: 1px solid var(--line); padding-bottom: 14px; }
  .content h1 { font-size: 25px; }
  #results { top: 50px; }
}
"""


SEARCH_JS = r"""
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
"""


if __name__ == "__main__":
    raise SystemExit(main())
