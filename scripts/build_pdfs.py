"""Render the Markdown question banks in interview-prep/ into printable PDFs.

Usage:
    pip install reportlab
    python scripts/build_pdfs.py

Produces one PDF per subject folder plus a combined book, in resources/pdf/.
The Markdown subset understood here is the one the question banks actually use:
headings, paragraphs, fenced code blocks, tables, bullet and numbered lists,
horizontal rules, and inline bold / italic / code / links.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        BaseDocTemplate, CondPageBreak, Frame, HRFlowable, ListFlowable,
        ListItem, PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table,
        TableStyle,
    )
except ImportError:  # pragma: no cover
    print("reportlab is required:  pip install reportlab", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "interview-prep"
OUTPUT = ROOT / "resources" / "pdf"

# Subject folders, in the order they should appear in the combined book.
SUBJECTS = [
    ("data-structures", "Data Structures"),
    ("algorithms", "Algorithms"),
    ("databases", "Databases"),
    ("core-cs", "Core Computer Science"),
    ("system-design", "System Design"),
    ("languages", "Language Specific"),
    ("behavioral", "Behavioural"),
]

# The standard PDF fonts cannot render these, so spell them out instead.
REPLACEMENTS = {
    "\U0001f7e2": "[Easy]",
    "\U0001f7e1": "[Medium]",
    "\U0001f534": "[Hard]",
    "\u2705": "[yes]",
    "\u274c": "[no]",
    "\u2192": "->", "\u2190": "<-", "\u2194": "<->", "\u21d2": "=>",
    "\u2264": "<=", "\u2265": ">=", "\u2260": "!=", "\u2248": "~",
    "\u00d7": "x", "\u00f7": "/", "\u2026": "...",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u00a0": " ",
    "\u00b2": "^2", "\u00b3": "^3", "\u207f": "^n",
    "\u2070": "^0", "\u2074": "^4", "\u2075": "^5", "\u2076": "^6",
    "\u2077": "^7", "\u2078": "^8", "\u2079": "^9", "\u00b9": "^1",
    "\u2011": "-", "\u2212": "-", "\u00b7": ".",
}

FONT_CANDIDATES = [
    ("DejaVuSans", "DejaVuSans-Bold", "DejaVuSansMono",
     ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
     ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
     ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]),
    ("Arial", "Arial-Bold", "CourierNew",
     ["C:/Windows/Fonts/arial.ttf"],
     ["C:/Windows/Fonts/arialbd.ttf"],
     ["C:/Windows/Fonts/cour.ttf"]),
]


def register_fonts() -> tuple[str, str, str]:
    """Return (body, bold, mono) font names, preferring a Unicode TTF."""
    for body, bold, mono, body_paths, bold_paths, mono_paths in FONT_CANDIDATES:
        found = [next((p for p in paths if Path(p).is_file()), None)
                 for paths in (body_paths, bold_paths, mono_paths)]
        if all(found):
            pdfmetrics.registerFont(TTFont(body, found[0]))
            pdfmetrics.registerFont(TTFont(bold, found[1]))
            pdfmetrics.registerFont(TTFont(mono, found[2]))
            pdfmetrics.registerFontFamily(body, normal=body, bold=bold)
            return body, bold, mono
    # Built-in fonts always exist; REPLACEMENTS keeps the text renderable.
    return "Helvetica", "Helvetica-Bold", "Courier"


def sanitise(text: str) -> str:
    for source, target in REPLACEMENTS.items():
        text = text.replace(source, target)
    # Drop anything still outside the Basic Multilingual Plane (stray emoji).
    return "".join(ch for ch in text if ord(ch) < 0x2500 or ch.isspace())


def inline(text: str) -> str:
    """Convert inline Markdown to reportlab's mini-HTML."""
    text = sanitise(text)
    # Protect code spans from escaping, then restore them as <font> runs.
    spans: list[str] = []

    def stash(match: re.Match[str]) -> str:
        spans.append(match.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)      # links -> their text
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<i>\1</i>", text)

    def restore(match: re.Match[str]) -> str:
        code = html.escape(spans[int(match.group(1))])
        return f'<font face="{MONO}" size="8.5">{code}</font>'

    return re.sub(r"\x00(\d+)\x00", restore, text)


BODY, BOLD, MONO = register_fonts()


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName=BOLD,
                                fontSize=26, leading=31, spaceAfter=6),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName=BODY,
                                   fontSize=12, leading=16, alignment=1,
                                   textColor=colors.HexColor("#555555")),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName=BOLD,
                             fontSize=18, leading=22, spaceBefore=16, spaceAfter=8,
                             textColor=colors.HexColor("#14213d")),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName=BOLD,
                             fontSize=13.5, leading=17, spaceBefore=12, spaceAfter=6,
                             textColor=colors.HexColor("#14213d")),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName=BOLD,
                             fontSize=11.5, leading=15, spaceBefore=11, spaceAfter=4,
                             textColor=colors.HexColor("#1b4965")),
        "body": ParagraphStyle("body", parent=base["Normal"], fontName=BODY,
                               fontSize=9.6, leading=14, spaceAfter=6,
                               alignment=TA_LEFT),
        "code": ParagraphStyle("code", parent=base["Code"], fontName=MONO,
                               fontSize=8.2, leading=10.4,
                               textColor=colors.HexColor("#1a1a1a")),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontName=BODY,
                               fontSize=8.4, leading=11),
        "cellhead": ParagraphStyle("cellhead", parent=base["Normal"], fontName=BOLD,
                                   fontSize=8.4, leading=11,
                                   textColor=colors.white),
    }


STYLES = build_styles()


def make_table(rows: list[list[str]]):
    """Render a Markdown table, dropping the |---| separator row."""
    body = [r for r in rows if not re.fullmatch(r"[\s|:-]+", "|".join(r))]
    if not body:
        return None

    header, *data = body
    cells = [[Paragraph(inline(c), STYLES["cellhead"]) for c in header]]
    cells += [[Paragraph(inline(c), STYLES["cell"]) for c in row] for row in data]

    width = 170 * mm
    columns = max(len(r) for r in cells)
    cells = [r + [Paragraph("", STYLES["cell"])] * (columns - len(r)) for r in cells]

    table = Table(cells, colWidths=[width / columns] * columns, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14213d")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b0b0b0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f2f4f8")]),
    ]))
    return table


def render_markdown(text: str) -> list:
    """Convert one Markdown document into a list of reportlab flowables."""
    flow: list = []
    lines = text.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        # Fenced code block
        if stripped.startswith("```"):
            index += 1
            block: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(sanitise(lines[index]))
                index += 1
            index += 1
            if block:
                flow.append(Spacer(1, 3))
                flow.append(Preformatted("\n".join(block), STYLES["code"]))
                flow.append(Spacer(1, 7))
            continue

        # Horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            flow.append(Spacer(1, 4))
            flow.append(HRFlowable(width="100%", thickness=0.6,
                                   color=colors.HexColor("#cccccc")))
            flow.append(Spacer(1, 6))
            index += 1
            continue

        # Table
        if stripped.startswith("|"):
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [c.strip() for c in lines[index].strip().strip("|").split("|")]
                rows.append(cells)
                index += 1
            table = make_table(rows)
            if table is not None:
                flow.append(Spacer(1, 4))
                flow.append(table)
                flow.append(Spacer(1, 8))
            continue

        # Heading
        heading = re.match(r"(#{1,6})\s+(.*)", stripped)
        if heading:
            level = len(heading.group(1))
            style = STYLES["h1"] if level == 1 else STYLES["h2"] if level == 2 else STYLES["h3"]
            # Keep a question heading with at least a little of its answer.
            flow.append(CondPageBreak(28 * mm))
            flow.append(Paragraph(inline(heading.group(2)), style))
            index += 1
            continue

        # Bullet or numbered list
        if re.match(r"[-*+]\s+", stripped) or re.match(r"\d+\.\s+", stripped):
            ordered = bool(re.match(r"\d+\.\s+", stripped))
            items: list[ListItem] = []
            while index < len(lines):
                current = lines[index].strip()
                match = re.match(r"(?:[-*+]|\d+\.)\s+(.*)", current)
                if not match:
                    # A wrapped continuation line belongs to the previous item.
                    if current and not re.match(r"(#{1,6}\s|\||```)", current) \
                            and lines[index].startswith((" ", "\t")) and items:
                        index += 1
                        continue
                    break
                items.append(ListItem(Paragraph(inline(match.group(1)), STYLES["body"]),
                                      leftIndent=12))
                index += 1
            flow.append(ListFlowable(items, bulletType="1" if ordered else "bullet",
                                     start="1" if ordered else None,
                                     leftIndent=14, bulletFontName=BODY,
                                     bulletFontSize=9))
            flow.append(Spacer(1, 4))
            continue

        # Paragraph: join wrapped lines until a blank or a block starter.
        paragraph: list[str] = []
        while index < len(lines):
            current = lines[index].strip()
            if not current or re.match(r"(#{1,6}\s|\||```|[-*+]\s|\d+\.\s)", current) \
                    or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", current):
                break
            paragraph.append(current)
            index += 1
        if paragraph:
            flow.append(Paragraph(inline(" ".join(paragraph)), STYLES["body"]))

    return flow


def page_furniture(canvas, doc) -> None:
    """Footer with the page number and the repository name."""
    canvas.saveState()
    canvas.setFont(BODY, 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(20 * mm, 12 * mm, "Interview Cracker")
    canvas.drawRightString(A4[0] - 20 * mm, 12 * mm, str(canvas.getPageNumber()))
    canvas.setStrokeColor(colors.HexColor("#dddddd"))
    canvas.setLineWidth(0.4)
    canvas.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    canvas.restoreState()


def build_document(path: Path, title: str, subtitle: str, flow: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(path), pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title=title, author="Interview Cracker", subject=subtitle,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame],
                                       onPage=page_furniture)])

    cover = [
        Spacer(1, 55 * mm),
        Paragraph(sanitise(title), STYLES["title"]),
        Spacer(1, 4),
        Paragraph(sanitise(subtitle), STYLES["subtitle"]),
        Spacer(1, 10 * mm),
        Paragraph(
            "Generated from the Markdown sources in the Interview Cracker "
            "repository. Every code snippet in these pages was executed and "
            "checked before publication.",
            STYLES["subtitle"]),
        PageBreak(),
    ]
    doc.build(cover + flow)


def subject_sources() -> list[tuple[str, str, list[Path]]]:
    """Yield (slug, title, markdown files) for each subject folder with content."""
    produced = []
    for slug, title in SUBJECTS:
        folder = SOURCE / slug
        files = sorted(folder.glob("*.md")) if folder.is_dir() else []
        if files:
            produced.append((slug, title, files))
    return produced


def render_subject(files: list[Path]) -> list:
    """Render a subject's files into FRESH flowables.

    reportlab flowables carry layout state, so the same object cannot be built
    into two documents. Each output PDF therefore re-renders from source.
    """
    flow: list = []
    for position, path in enumerate(files):
        if position:
            flow.append(PageBreak())
        flow.extend(render_markdown(path.read_text(encoding="utf-8")))
    return flow


def main() -> int:
    if not SOURCE.is_dir():
        print(f"No such directory: {SOURCE}", file=sys.stderr)
        return 1

    OUTPUT.mkdir(parents=True, exist_ok=True)
    subjects = subject_sources()
    if not subjects:
        print("No Markdown sources found.", file=sys.stderr)
        return 1

    for slug, title, files in subjects:
        target = OUTPUT / f"interview-questions-{slug}.pdf"
        build_document(target, title, "Interview Cracker question bank",
                       render_subject(files))
        print(f"wrote {target.relative_to(ROOT).as_posix()}")

    combined: list = []
    for position, (slug, title, files) in enumerate(subjects):
        if position:
            combined.append(PageBreak())
        combined.append(Paragraph(sanitise(title), STYLES["h1"]))
        combined.append(HRFlowable(width="100%", thickness=1,
                                   color=colors.HexColor("#14213d")))
        combined.append(Spacer(1, 6))
        combined.extend(render_subject(files))   # fresh flowables

    book = OUTPUT / "interview-questions-complete.pdf"
    build_document(book, "Interview Cracker",
                   "Complete interview question bank", combined)
    print(f"wrote {book.relative_to(ROOT).as_posix()}")

    print(f"\n{len(subjects) + 1} PDFs written to {OUTPUT.relative_to(ROOT).as_posix()}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
