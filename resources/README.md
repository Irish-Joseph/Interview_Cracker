# Resources

## PDF question banks

Printable versions of the [`interview-prep/`](../interview-prep/) question banks,
for offline reading, printing, or revising on a tablet.

| PDF | Pages | Covers |
|---|---|---|
| [Complete question bank](pdf/interview-questions-complete.pdf) | ~62 | Everything below, in one book |
| [Data structures](pdf/interview-questions-data-structures.pdf) | ~16 | Arrays, linked lists, stacks/queues/heaps, hash tables, trees and graphs |
| [Algorithms](pdf/interview-questions-algorithms.pdf) | ~13 | Complexity, sorting and searching, recursion, dynamic programming |
| [Core computer science](pdf/interview-questions-core-cs.pdf) | ~10 | Operating systems, networking, concurrency |
| [Language specific](pdf/interview-questions-languages.pdf) | ~10 | Python, JavaScript, Java |
| [System design](pdf/interview-questions-system-design.pdf) | ~8 | Fundamentals and a full worked walkthrough |
| [Databases](pdf/interview-questions-databases.pdf) | ~7 | SQL queries, indexing, transactions |
| [Behavioural](pdf/interview-questions-behavioral.pdf) | ~4 | STAR method and the recurring questions |

## Regenerating them

The PDFs are generated from the Markdown sources — **edit the Markdown, never
the PDF**, then rebuild:

```bash
pip install reportlab
python scripts/build_pdfs.py
```

The builder ([`scripts/build_pdfs.py`](../scripts/build_pdfs.py)) understands the
Markdown subset the question banks use: headings, paragraphs, fenced code blocks,
tables, lists, rules, and inline bold/italic/code/links.

Two things worth knowing if you modify it:

- **Fonts.** It prefers a Unicode TTF (DejaVu on Linux, Arial on Windows) and
  falls back to the built-in Helvetica. Characters the standard PDF fonts cannot
  render are transliterated — the difficulty emoji become `[Easy]`, `[Medium]`
  and `[Hard]`, arrows become `->`, and so on.
- **Flowables are single-use.** reportlab flowables carry layout state, so each
  output PDF re-renders from source rather than reusing objects. Sharing them
  between documents raises a `LayoutError`.
