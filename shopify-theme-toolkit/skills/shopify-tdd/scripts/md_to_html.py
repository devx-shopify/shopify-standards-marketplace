#!/usr/bin/env python3
"""Convert a shopify-tdd Markdown file into styled HTML for Google Drive import,
and check the Markdown against the TDD rules first.

Standard library only.

Usage:
    python md_to_html.py tdd.md -o tdd.html      check, then convert
    python md_to_html.py tdd.md --check-only     only run the checks

Markdown supported (and nothing else, on purpose):
    # Title                    one only, first line: becomes the document title
    ## 1. Section              Heading 1 (real <h1>)
    ### Subsection             Heading 2 (real <h2>)
    plain paragraphs           <p>
    - item / * item            bullet list (indent 2 or 4 spaces for one nested level)
    1. item                    numbered list
    | a | b |                  table; the first row is the header, the second row
    |---|---|                  must be the separator line
    [[DIAGRAM 2: Name]]        diagram placeholder paragraph
    **bold**, *italic*, `code`, [text](url)

The check fails (exit code 1) on errors. Warnings are printed but do not fail.
"""

import argparse
import html
import re
import sys

HEADING_COLOR = "#000000"  # title and headings are black
HEADER_FILL = "#EEF3F7"
BLACK = "#000000"
BORDER = "#000000"
FONT = "Manrope, Arial, sans-serif"

REQUIRED_SECTIONS = [
    "Overview",
    "Page inventory",
    "Design system",
    "Global UI",
    "Shared building blocks",
    "Data model",
    "Apps and integrations",
    "Merchant editing",
    "Non-functional",
    "Decisions",
    "Open questions",
]

VERSION_RE = re.compile(r"^Version: v\d+, \d{4}-\d{2}-\d{2}$")
DIAGRAM_RE = re.compile(r"^\[\[DIAGRAM (\d+): (.+)\]\]$")
TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")
BULLET_RE = re.compile(r"^( *)[-*] (.*)$")
NUMBER_RE = re.compile(r"^( *)\d+\. (.*)$")
Q_ID_RE = re.compile(r"\bQ-\d+\b")
DEC_ID_RE = re.compile(r"\bDEC-\d+\b")


# ---------------------------------------------------------------- parsing

def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    # allow \| inside cells
    cells = re.split(r"(?<!\\)\|", line)
    return [c.strip().replace("\\|", "|") for c in cells]


def parse(text):
    """Return a list of blocks: (kind, data, line_number)."""
    # guidance comments in the template never reach the Doc
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = text.splitlines()
    blocks = []
    i = 0
    para = []
    para_start = 0

    def flush_para():
        nonlocal para
        if para:
            blocks.append(("p", " ".join(s.strip() for s in para), para_start))
            para = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        n = i + 1

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped.startswith("### "):
            flush_para()
            blocks.append(("h2", stripped[4:].strip(), n))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            blocks.append(("h1", stripped[3:].strip(), n))
            i += 1
            continue
        if stripped.startswith("# "):
            flush_para()
            blocks.append(("title", stripped[2:].strip(), n))
            i += 1
            continue

        m = DIAGRAM_RE.match(stripped)
        if m:
            flush_para()
            blocks.append(("diagram", (int(m.group(1)), m.group(2).strip()), n))
            i += 1
            continue

        if stripped.startswith("|"):
            flush_para()
            rows = []
            start = n
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            blocks.append(("table", rows, start))
            continue

        if BULLET_RE.match(line) or NUMBER_RE.match(line):
            flush_para()
            items = []
            start = n
            kind = "ul" if BULLET_RE.match(line) else "ol"
            while i < len(lines):
                cur = lines[i]
                mb = BULLET_RE.match(cur)
                mn = NUMBER_RE.match(cur)
                mm = mb or mn
                if not mm:
                    if cur.strip() and cur.startswith("  ") and items:
                        items[-1] = (items[-1][0], items[-1][1] + " " + cur.strip(), items[-1][2])
                        i += 1
                        continue
                    break
                level = 1 if len(mm.group(1)) >= 2 else 0
                items.append((level, mm.group(2).strip(), "ul" if mb else "ol"))
                i += 1
            blocks.append((kind, items, start))
            continue

        if not para:
            para_start = n
        para.append(line)
        i += 1

    flush_para()
    return blocks


# ---------------------------------------------------------------- checks

def check(text, blocks):
    errors, warnings = [], []
    if "<!--" in text:
        warnings.append("template guidance comments are still in the file; they are dropped from the Doc.")

    # dashes
    for ln, line in enumerate(text.splitlines(), 1):
        if "\u2014" in line:
            errors.append(f"line {ln}: em dash found. Use a comma, a period or 'to'.")
        if "\u2013" in line:
            errors.append(f"line {ln}: en dash found. Use 'to' or a plain hyphen.")
        if " -- " in line:
            warnings.append(f"line {ln}: ' -- ' looks like a stand-in for a dash.")

    titles = [b for b in blocks if b[0] == "title"]
    if len(titles) != 1:
        errors.append(f"expected exactly one '# Title' line, found {len(titles)}.")
    elif blocks[0][0] != "title":
        errors.append("the '# Title' line must come first.")
    else:
        if not titles[0][1].startswith("TDD - "):
            warnings.append("title should follow 'TDD - Client - Project'.")
        if len(blocks) < 2 or blocks[1][0] != "p" or not VERSION_RE.match(blocks[1][1]):
            errors.append("the line right after the title must be 'Version: vN, YYYY-MM-DD'.")

    # sections in order
    h1 = [b for b in blocks if b[0] == "h1"]
    names = [re.sub(r"^\d+\.\s*", "", b[1]) for b in h1]
    if names != REQUIRED_SECTIONS:
        errors.append(
            "Heading 1 sections must be exactly, in order: "
            + "; ".join(f"{k + 1}. {s}" for k, s in enumerate(REQUIRED_SECTIONS))
            + f". Found: {names}"
        )
    for k, b in enumerate(h1):
        if not b[1].startswith(f"{k + 1}. "):
            errors.append(f"line {b[2]}: section heading should start with '{k + 1}. '.")

    # tables
    for kind, rows, ln in [b for b in blocks if b[0] == "table"]:
        if len(rows) < 2 or not TABLE_SEP_RE.match(rows[1]):
            errors.append(f"line {ln}: table needs a header row followed by a |---| separator line.")
            continue
        header = split_row(rows[0])
        if any(not c for c in header):
            errors.append(f"line {ln}: table header has an empty cell. Every column needs a name.")
        for r, row in enumerate(rows[2:], 3):
            cells = split_row(row)
            if len(cells) != len(header):
                errors.append(
                    f"line {ln + r - 1}: row has {len(cells)} cells, header has {len(header)}."
                )
        if len(rows) == 2:
            warnings.append(f"line {ln}: table has a header but no rows.")

    # diagrams: numbered 1..n in order, each followed by a table or list
    diag_idx = [k for k, b in enumerate(blocks) if b[0] == "diagram"]
    for expected, k in enumerate(diag_idx, 1):
        num, name = blocks[k][1]
        if num != expected:
            errors.append(f"line {blocks[k][2]}: diagram numbered {num}, expected {expected}.")
        nxt = blocks[k + 1] if k + 1 < len(blocks) else None
        # allow one short lead-in paragraph before the facts
        if nxt and nxt[0] == "p" and k + 2 < len(blocks):
            nxt = blocks[k + 2]
        if not nxt or nxt[0] not in ("table", "ul", "ol"):
            errors.append(
                f"line {blocks[k][2]}: DIAGRAM {num} must be followed by a table or list "
                "that carries all of its facts in text."
            )

    # section-specific content
    def section_blocks(name):
        out, inside = [], False
        for b in blocks:
            if b[0] == "h1":
                inside = re.sub(r"^\d+\.\s*", "", b[1]) == name
                continue
            if inside:
                out.append(b)
        return out

    sec_text = lambda name: "\n".join(
        b[1] if isinstance(b[1], str) else str(b[1]) for b in section_blocks(name)
    )

    oq = sec_text("Open questions")
    if oq and not Q_ID_RE.search(oq) and "None" not in oq:
        warnings.append("Open questions has no Q-n IDs. Write 'None.' if there are none.")
    dec = sec_text("Decisions")
    if dec and not DEC_ID_RE.search(dec) and "None" not in dec:
        warnings.append("Decisions has no DEC-n IDs. Write 'None.' if there are none.")

    if not any(b[0] == "table" for b in section_blocks("Page inventory")):
        errors.append("Page inventory must contain a table.")
    sb = section_blocks("Shared building blocks")
    if not any(b[0] == "table" for b in sb):
        errors.append("Shared building blocks must contain the section reuse matrix as a table.")

    # duplicate IDs
    for pat, label in ((Q_ID_RE, "Q"), (DEC_ID_RE, "DEC")):
        defs = re.findall(r"^\|\s*(" + label + r"-\d+)\s*\|", text, re.M)
        dupes = sorted({d for d in defs if defs.count(d) > 1})
        if dupes:
            errors.append(f"{label} IDs defined more than once: {', '.join(dupes)}.")

    # rough length check, about 3000 characters per page
    pages = len(text) / 3000
    if pages > 15:
        warnings.append(f"about {pages:.0f} pages of text; target is 5 to 15.")

    return errors, warnings


# ---------------------------------------------------------------- rendering

def inline(s):
    """Escape and apply inline Markdown. Code spans are protected first."""
    codes = []

    def keep_code(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep_code, s)
    s = html.escape(s, quote=False)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        s,
    )
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(
        r"\x00(\d+)\x00",
        lambda m: '<span style="font-family:\'Roboto Mono\',monospace;">'
        + html.escape(codes[int(m.group(1))], quote=False)
        + "</span>",
        s,
    )
    return s


def style(*parts):
    return "; ".join(x.strip().rstrip(";") for x in parts) + ";"


BODY = style(f"font-family:{FONT}", "font-size:11pt", f"color:{BLACK}", "font-weight:400")
P_STYLE = style(BODY, "margin:0 0 6pt 0")
TITLE_STYLE = style(f"font-family:{FONT}", "font-size:24pt", "font-weight:700", f"color:{HEADING_COLOR}", "margin:0 0 4pt 0")
H1_STYLE = style(f"font-family:{FONT}", "font-size:16pt", "font-weight:700", f"color:{HEADING_COLOR}", "margin:18pt 0 6pt 0")
H2_STYLE = style(f"font-family:{FONT}", "font-size:13pt", "font-weight:700", f"color:{HEADING_COLOR}", "margin:12pt 0 4pt 0")
TABLE_STYLE = style("border-collapse:collapse", "width:100%", "margin:4pt 0 10pt 0")
CELL = style(f"border:1px solid {BORDER}", "padding:4pt 6pt", "vertical-align:top",
             f"font-family:{FONT}", "font-size:10pt", f"color:{BLACK}", "text-align:left")
TH_STYLE = style(CELL, f"background-color:{HEADER_FILL}", "font-weight:700")
TD_STYLE = style(CELL, "font-weight:400")
DIAGRAM_STYLE = style(BODY, "font-weight:700", "margin:10pt 0 6pt 0")


def render_list(items, inline_styles=False):
    out = []
    stack = []  # list of (tag, level)
    for level, text, tag in items:
        while stack and stack[-1][1] > level:
            out.append(f"</li></{stack.pop()[0]}>")
        if not stack or stack[-1][1] < level:
            out.append(f'<{tag} style="margin:0 0 6pt 0;">' if inline_styles else f"<{tag}>")
            stack.append((tag, level))
        else:
            out.append("</li>")
        out.append(f'<li style="{BODY}">{inline(text)}' if inline_styles else f"<li>{inline(text)}")
    while stack:
        out.append(f"</li></{stack.pop()[0]}>")
    # the very first "</li>" for a new list would be wrong; clean it
    joined = "".join(out)
    joined = re.sub(r'(<(?:ul|ol)(?: style="[^"]*")?>)</li>', r"\1", joined)
    return joined


CSS = f"""
body {{ {BODY} }}
p {{ {P_STYLE} }}
li {{ {BODY} }}
ul, ol {{ margin:0 0 6pt 0; }}
h1 {{ {H1_STYLE} }}
h2 {{ {H2_STYLE} }}
p.title {{ {TITLE_STYLE} }}
p.diagram {{ {DIAGRAM_STYLE} }}
table {{ {TABLE_STYLE} }}
th {{ {TH_STYLE} }}
td {{ {TD_STYLE} }}
"""


def render(blocks, inline_styles=False):
    """Compact mode (default) puts the styles in one <style> block.
    Inline mode repeats them on every tag; use it only if Drive ignores the block."""
    def attr(s):
        return f' style="{s}"' if inline_styles else ""

    title = next((b[1] for b in blocks if b[0] == "title"), "TDD")
    out = ["<!DOCTYPE html>", '<html><head><meta charset="utf-8">', f"<title>{html.escape(title)}</title>"]
    if not inline_styles:
        out.append("<style>" + CSS + "</style>")
    out += ["</head>", f"<body{attr(BODY)}>"]
    for kind, data, _ in blocks:
        if kind == "title":
            out.append(f'<p class="title"{attr(TITLE_STYLE)}><b>{inline(data)}</b></p>')
        elif kind == "h1":
            out.append(f"<h1{attr(H1_STYLE)}>{inline(data)}</h1>")
        elif kind == "h2":
            out.append(f"<h2{attr(H2_STYLE)}>{inline(data)}</h2>")
        elif kind == "p":
            out.append(f"<p{attr(P_STYLE)}>{inline(data)}</p>")
        elif kind == "diagram":
            num, name = data
            out.append(f'<p class="diagram"{attr(DIAGRAM_STYLE)}><b>DIAGRAM {num}: {inline(name)} (paste the PNG here)</b></p>')
        elif kind in ("ul", "ol"):
            out.append(render_list(data, inline_styles))
        elif kind == "table":
            header = split_row(data[0])
            body = [split_row(r) for r in data[2:]]
            out.append(f"<table{attr(TABLE_STYLE)}>")
            out.append("<tr>" + "".join(f"<th{attr(TH_STYLE)}><b>{inline(c)}</b></th>" for c in header) + "</tr>")
            for row in body:
                out.append("<tr>" + "".join(f"<td{attr(TD_STYLE)}>{inline(c)}</td>" for c in row) + "</tr>")
            out.append("</table>")
    out.append("</body></html>")
    return "\n".join(out)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("-o", "--output", help="HTML output path (default: same name, .html)")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--no-check", action="store_true", help="skip checks (not recommended)")
    ap.add_argument("--inline-styles", action="store_true",
                    help="repeat styles on every tag (bigger file); use only if Drive ignores the <style> block")
    args = ap.parse_args()

    with open(args.markdown, encoding="utf-8") as f:
        text = f.read()
    blocks = parse(text)

    if not args.no_check:
        errors, warnings = check(text, blocks)
        for w in warnings:
            print("WARNING:", w)
        for e in errors:
            print("ERROR:", e)
        if errors:
            print(f"\n{len(errors)} error(s). Fix the Markdown and run again.")
            sys.exit(1)
        print("Checks passed.")
    if args.check_only:
        return

    out_path = args.output or re.sub(r"\.md$", "", args.markdown) + ".html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render(blocks, args.inline_styles))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
