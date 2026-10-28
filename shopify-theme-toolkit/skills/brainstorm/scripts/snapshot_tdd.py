#!/usr/bin/env python3
"""Write docs/tdd.md from a Google Doc read, without retyping the Doc.

The Drive connector's read of a large TDD is too big to come back inline, so the
tool saves it to a file. This script takes that file (or a plain text file),
cleans up the Drive text and writes the snapshot with its header:

- removes Drive's backslash escapes (\\*, \\_, \\#, \\-- ...), keeping \\| inside tables
- tables whose first row is empty get their bold second row promoted to the header
- bold-only numbered lines ("**3.2 Type Scale**") become ## / ### headings
- a bold line repeating the heading right above it is dropped

With --doc-json (a saved Google Docs read_doc result) it also counts images and
drawings per tab, because the Drive text drops them without a trace.

Usage:
  snapshot_tdd.py READ_FILE --link URL [--date YYYY-MM-DD] [--doc-json FILE] [-o docs/tdd.md]

READ_FILE is the saved Drive read_file_content result ({"fileContent": ...}) or a
plain text / Markdown file. Prints a short report. Standard library only.
"""

import argparse
import datetime
import json
import re
import sys

ESCAPE = re.compile(r"\\+([\\`*_{}\[\]()#+\-.!~<>])")
BOLD_LINE = re.compile(r"^\*\*(.+?)\*\*\s*$")
NUMBERED = re.compile(r"^(\d+)(\.\d+)*\.?\s+\S")
SEPARATOR = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
DIAGRAM = re.compile(r"DIAGRAM\s+(\d+)\s*:\s*([^(\n]+)")


def load_text(path):
    raw = open(path, encoding="utf-8").read()
    try:
        data = json.loads(raw)
    except ValueError:
        return raw
    if isinstance(data, dict):
        for key in ("fileContent", "content", "text"):
            if isinstance(data.get(key), str):
                return data[key]
    sys.exit("{}: JSON without a fileContent field; pass the Drive read_file_content result".format(path))


def cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def row(values):
    return "| " + " | ".join(values) + " |"


def clean(text, report):
    lines = [l.rstrip() for l in text.replace("\r\n", "\n").split("\n")]
    # unescape outside of table pipes
    lines = [ESCAPE.sub(r"\1", l) for l in lines]

    # Drive sometimes leaves a stray ** on a heading ("# Homepage Sprint**")
    # or a bold marker split onto its own line
    lines = [re.sub(r"^(#+\s+)\**(.*?)\**$", r"\1\2", l) if l.startswith("#") else l for l in lines]
    lines = [l for l in lines if not re.match(r"^\*+$", l.strip())]

    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        # table with an empty header row and a bold first data row
        if line.strip().startswith("|") and SEPARATOR.match(nxt.strip()):
            head = cells(line)
            body_start = i + 2
            first = cells(lines[body_start]) if body_start < len(lines) and lines[body_start].strip().startswith("|") else None
            if first and not any(head) and all(BOLD_LINE.match(c) or not c for c in first):
                labels = [BOLD_LINE.match(c).group(1).strip() if c else "" for c in first]
                out.append(row(labels))
                out.append(row(["---"] * len(labels)))
                i = body_start + 1
                report["tables_fixed"] += 1
                continue
        m = BOLD_LINE.match(line.strip())
        if m:
            label = m.group(1).strip()
            prev = next((l for l in reversed(out) if l.strip()), "")
            if prev.startswith("#") and prev.lstrip("#").strip() == label:
                report["duplicate_titles"] += 1
                i += 1
                continue
            if NUMBERED.match(label):
                depth = label.split()[0].rstrip(".").count(".")
                out.append(("## " if depth == 0 else "### ") + label)
                report["headings"] += 1
                i += 1
                continue
        out.append(line)
        i += 1
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def diagrams(text):
    """DIAGRAM n placeholders and whether a table or list follows each one."""
    found = []
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        m = DIAGRAM.search(line)
        if not m:
            continue
        follow = next((l.strip() for l in lines[idx + 1:] if l.strip()), "")
        found.append((m.group(1), m.group(2).strip(), follow.startswith("|") or follow.startswith("-")))
    return found


def images_per_tab(path):
    data = json.load(open(path, encoding="utf-8"))
    doc = data.get("content", data)
    counts = []

    def walk(tabs):
        for t in tabs:
            dt = t.get("documentTab", {})
            n = len(dt.get("inlineObjects", {})) + len(dt.get("positionedObjects", {}))
            counts.append((t.get("tabProperties", {}).get("title", "?"), n))
            walk(t.get("childTabs", []))

    walk(doc.get("tabs", []))
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("read_file")
    ap.add_argument("--link", required=True, help="the TDD Google Doc link, or 'pasted in conversation'")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--doc-json", help="saved Google Docs read_doc result, to count images per tab")
    ap.add_argument("-o", "--out", default="docs/tdd.md")
    a = ap.parse_args(argv)

    report = {"tables_fixed": 0, "headings": 0, "duplicate_titles": 0}
    body = clean(load_text(a.read_file), report)
    header = ("> Snapshot of the TDD Google Doc: {}\n"
              "> Taken {}. Edit the Google Doc, not this file. /brainstorm refreshes it.\n\n").format(a.link, a.date)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(header + body)

    tabs = [l[2:].strip() for l in body.split("\n") if l.startswith("# ")]
    print("Wrote {} ({:,} characters)".format(a.out, len(header + body)))
    print("Top-level sections (# headings, one per Doc tab when the Doc has tabs): {}".format(len(tabs)))
    for t in tabs:
        print("  - " + t)
    print("Tables with a promoted header row: {}".format(report["tables_fixed"]))
    print("Bold numbered lines turned into headings: {}".format(report["headings"]))
    print("Repeated bold titles removed: {}".format(report["duplicate_titles"]))
    dia = diagrams(body)
    print("DIAGRAM placeholders: {}".format(len(dia)))
    for n, name, has_facts in dia:
        print("  - DIAGRAM {}: {}{}".format(n, name, "" if has_facts else "  (NO facts table under it)"))
    if a.doc_json:
        counts = images_per_tab(a.doc_json)
        total = sum(n for _, n in counts)
        print("Images and drawings in the Doc: {}".format(total))
        for title, n in counts:
            if n:
                print("  - {}: {}".format(title, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
