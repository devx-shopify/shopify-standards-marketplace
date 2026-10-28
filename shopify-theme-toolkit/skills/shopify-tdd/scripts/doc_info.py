#!/usr/bin/env python3
"""Small helpers for a Google Docs `read_doc` result saved as JSON.

Standard library only. The read_doc result is large, so save it to a file and
point these commands at the file instead of reading the JSON by eye.

Usage:
    python doc_info.py info    DOC.json      revisionId, tab id, body end index
    python doc_info.py outline DOC.json      one line per paragraph or table
    python doc_info.py find    DOC.json "text"   index range of each match
    python doc_info.py fix     DOC.json      update_doc arguments for the
                                             one-time style fix after creation
    python doc_info.py check   DOC.json      checks the devx style was kept

All indexes are the Docs API UTF-16 indexes for the first tab.
"""

import json
import re
import sys

HEADING_RGB = (0.0, 0.0, 0.0)  # title and headings are black
FONT = "Manrope"
MARGIN_PT = 54


# ---------------------------------------------------------------- loading

def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


def load(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # some tool results wrap the JSON in text; take the outermost object
        start, end = raw.find("{"), raw.rfind("}")
        data = json.loads(raw[start : end + 1])
    # a tool result may hold the document as a JSON string inside "text"
    if isinstance(data, list) and data and isinstance(data[0], dict) and "text" in data[0]:
        data = json.loads(data[0]["text"])
    if isinstance(data, dict) and "text" in data and isinstance(data["text"], str):
        try:
            data = json.loads(data["text"])
        except json.JSONDecodeError:
            pass
    return data


def first_tab(doc):
    tabs = doc.get("tabs") or find_key(doc, "tabs")
    if tabs:
        t = tabs[0]
        return t["tabProperties"]["tabId"], t["documentTab"]["body"], t["documentTab"].get("documentStyle", {})
    body = doc.get("body") or find_key(doc, "body")
    return None, body, doc.get("documentStyle", {})


def named_styles(doc):
    ns = find_key(doc, "namedStyles") or {}
    return {x["namedStyleType"]: x for x in ns.get("styles", [])}


# ---------------------------------------------------------------- walking

def paragraphs(content, in_table=False, table_start=None, cell=None):
    """Yield (paragraph_element, in_table, table_start, (row, col))."""
    for el in content:
        if "paragraph" in el:
            yield el, in_table, table_start, cell
        elif "table" in el:
            for r, row in enumerate(el["table"]["tableRows"]):
                for c, tc in enumerate(row["tableCells"]):
                    yield from paragraphs(tc["content"], True, el["startIndex"], (r, c))


def para_text(p):
    return "".join(e.get("textRun", {}).get("content", "") for e in p["paragraph"]["elements"])


def style_type(p):
    return p["paragraph"].get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")


def body_end(body):
    return body["content"][-1]["endIndex"]


def tables(body):
    return [el for el in body["content"] if "table" in el]


# ---------------------------------------------------------------- commands

def cmd_info(doc):
    tab, body, dstyle = first_tab(doc)
    print("revisionId:", doc.get("revisionId") or find_key(doc, "revisionId"))
    print("tabId:", tab)
    print("bodyEndIndex:", body_end(body))
    print("lastTextIndex (bodyEnd - 1):", body_end(body) - 1)
    print("tables:", len(tables(body)))
    for side in ("marginTop", "marginBottom", "marginLeft", "marginRight"):
        m = dstyle.get(side, {})
        print(f"{side}:", m.get("magnitude"), m.get("unit"))


def cmd_outline(doc):
    tab, body, _ = first_tab(doc)
    print("revisionId:", doc.get("revisionId") or find_key(doc, "revisionId"))
    seen_tables = set()
    for el in body["content"]:
        if "table" in el:
            t = el["table"]
            first = [para_text(p).strip() for p, *_ in paragraphs(t["tableRows"][0]["tableCells"][0]["content"])]
            print(f"[{el['startIndex']}-{el['endIndex']}] TABLE {t['rows']}x{t['columns']} first cell: {first[:1]}")
        elif "paragraph" in el:
            txt = para_text(el).rstrip("\n")
            print(f"[{el['startIndex']}-{el['endIndex']}] {style_type(el)}: {txt[:90]}")
    print("bodyEndIndex:", body_end(body))


def cmd_find(doc, needle):
    tab, body, _ = first_tab(doc)
    hits = 0
    for p, in_table, tstart, cell in paragraphs(body["content"]):
        for run in p["paragraph"]["elements"]:
            tr = run.get("textRun")
            if not tr:
                continue
            content = tr["content"]
            for m in re.finditer(re.escape(needle), content):
                # UTF-16 offset of the match inside the run
                pre = content[: m.start()]
                off = len(pre.encode("utf-16-le")) // 2
                ln = len(needle.encode("utf-16-le")) // 2
                s = run["startIndex"] + off
                where = f" table@{tstart} cell{cell}" if in_table else ""
                print(f"[{s}-{s + ln}] {style_type(p)}{where} bold={bool(tr.get('textStyle', {}).get('bold'))}")
                hits += 1
    if not hits:
        print("no match (a match cannot span two text runs; try a shorter piece)")


def cmd_fix(doc):
    """One-time fix after Drive created the Doc from HTML."""
    tab, body, _ = first_tab(doc)
    rev = doc.get("revisionId") or find_key(doc, "revisionId")
    end = body_end(body)
    loc = {"tabId": tab} if tab else {}
    reqs = [
        {
            "updateDocumentStyle": {
                "documentStyle": {
                    side: {"magnitude": MARGIN_PT, "unit": "PT"}
                    for side in ("marginTop", "marginBottom", "marginLeft", "marginRight")
                },
                "fields": "marginTop,marginBottom,marginLeft,marginRight",
                **loc,
            }
        },
    ]
    # Drive maps the HTML <style> block onto the Doc's Normal text style, so the
    # body is usually Manrope already. Only force the font when it is not.
    normal = named_styles(doc).get("NORMAL_TEXT", {}).get("textStyle", {})
    if normal.get("weightedFontFamily", {}).get("fontFamily") != FONT:
        reqs.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": 1, "endIndex": end - 1, **loc},
                    "textStyle": {"weightedFontFamily": {"fontFamily": FONT, "weight": 400}},
                    "fields": "weightedFontFamily",
                }
            }
        )
    # first paragraph is the document title
    first = next((el for el in body["content"] if "paragraph" in el and para_text(el).strip()), None)
    if first and style_type(first) != "TITLE":
        reqs.append(
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": first["startIndex"], "endIndex": first["endIndex"], **loc},
                    "paragraphStyle": {"namedStyleType": "TITLE"},
                    "fields": "namedStyleType",
                }
            }
        )
    if first:
        # Applying TITLE resets the line's own size and color (tested), so set
        # them again right after, in the same batch.
        reqs.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": first["startIndex"], "endIndex": first["endIndex"] - 1, **loc},
                    "textStyle": {
                        "bold": True,
                        "fontSize": {"magnitude": 24, "unit": "PT"},
                        "foregroundColor": {"color": {"rgbColor": dict(zip(("red", "green", "blue"), HEADING_RGB))}},
                        "weightedFontFamily": {"fontFamily": FONT, "weight": 400},
                    },
                    "fields": "bold,fontSize,foregroundColor,weightedFontFamily",
                }
            }
        )
    # Headings: bold (Drive drops font-weight from the heading CSS, and the
    # connector rejects updateNamedStyle), and keep with the next paragraph.
    for el in body["content"]:
        if "paragraph" in el and style_type(el).startswith("HEADING"):
            reqs.append(
                {
                    "updateTextStyle": {
                        "range": {"startIndex": el["startIndex"], "endIndex": el["endIndex"] - 1, **loc},
                        "textStyle": {
                            "bold": True,
                            "foregroundColor": {"color": {"rgbColor": dict(zip(("red", "green", "blue"), HEADING_RGB))}},
                        },
                        "fields": "bold,foregroundColor",
                    }
                }
            )
            reqs.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": el["startIndex"], "endIndex": el["endIndex"], **loc},
                        "paragraphStyle": {"keepWithNext": True},
                        "fields": "keepWithNext",
                    }
                }
            )
    # rows never split across pages; pin the header row so it repeats on a new page
    for t in tables(body):
        reqs.append(
            {
                "pinTableHeaderRows": {
                    "tableStartLocation": {"index": t["startIndex"], **loc},
                    "pinnedHeaderRowsCount": 1,
                }
            }
        )
        reqs.append(
            {
                "updateTableRowStyle": {
                    "tableStartLocation": {"index": t["startIndex"], **loc},
                    "tableRowStyle": {"preventOverflow": True},
                    "fields": "preventOverflow",
                }
            }
        )
    print(json.dumps({"requests": reqs, "writeControl": {"requiredRevisionId": rev}}, indent=1))


def rgb(ts, key):
    c = ts.get(key, {}).get("color", {}).get("rgbColor")
    if c is None:
        return None
    return (c.get("red", 0.0), c.get("green", 0.0), c.get("blue", 0.0))


def close(a, b, tol=0.02):
    return a is not None and all(abs(x - y) <= tol for x, y in zip(a, b))


def effective(ts, named, key):
    if key in ts and ts[key] != {}:
        return ts[key]
    return named.get(key)


def cmd_check(doc):
    tab, body, dstyle = first_tab(doc)
    ns = named_styles(doc)
    problems = []
    expected = {"TITLE": (24, True), "HEADING_1": (16, True), "HEADING_2": (13, True)}
    counts = {}
    fonts = set()
    for p, in_table, tstart, cell in paragraphs(body["content"]):
        st = style_type(p)
        counts[st] = counts.get(st, 0) + 1
        is_heading = st.startswith("HEADING") or st == "TITLE"
        for run in p["paragraph"]["elements"]:
            tr = run.get("textRun")
            if not tr or not tr["content"].strip():
                continue
            ts = tr.get("textStyle", {})
            nts = ns.get(st, {}).get("textStyle", {})
            normal_ts = ns.get("NORMAL_TEXT", {}).get("textStyle", {})
            fam = (effective(ts, nts, "weightedFontFamily") or effective({}, normal_ts, "weightedFontFamily") or {}).get("fontFamily")
            fonts.add(fam)
            if fam and fam != FONT and "Mono" not in fam:
                problems.append(f"[{run['startIndex']}] font {fam}: {tr['content'][:40]!r}")
            col = rgb(ts, "foregroundColor") if ts.get("foregroundColor", {}).get("color") else rgb(nts, "foregroundColor")
            if st in expected:
                size = (effective(ts, nts, "fontSize") or {}).get("magnitude")
                bold = effective(ts, nts, "bold")
                want_size, want_bold = expected[st]
                if size != want_size or bool(bold) != want_bold:
                    problems.append(f"[{run['startIndex']}] {st} is {size}pt bold={bold}, expected {want_size}pt bold: {tr['content'][:40]!r}")
            elif in_table:
                size = (effective(ts, nts, "fontSize") or {}).get("magnitude")
                if size != 10:
                    problems.append(f"[{run['startIndex']}] table text is {size}pt, expected 10pt: {tr['content'][:30]!r}")
            if is_heading:
                if col is not None and not close(col, HEADING_RGB):
                    problems.append(f"[{run['startIndex']}] heading not black: {tr['content'][:40]!r}")
            elif col is not None and not close(col, (0, 0, 0)):
                problems.append(f"[{run['startIndex']}] body text colored {col}: {tr['content'][:40]!r}")
            if "\u2014" in tr["content"]:
                problems.append(f"[{run['startIndex']}] em dash: {tr['content'][:60]!r}")
            if "\u2013" in tr["content"]:
                problems.append(f"[{run['startIndex']}] en dash: {tr['content'][:60]!r}")
    # bold-as-heading: a normal paragraph that is entirely bold and short, outside tables
    for p, in_table, *_ in paragraphs(body["content"]):
        if in_table or style_type(p) != "NORMAL_TEXT":
            continue
        runs = [e["textRun"] for e in p["paragraph"]["elements"] if e.get("textRun", {}).get("content", "").strip()]
        txt = para_text(p).strip()
        if runs and all(r.get("textStyle", {}).get("bold") for r in runs) and not txt.startswith("DIAGRAM "):
            if len(txt) < 80:
                problems.append(f"[{p['startIndex']}] bold paragraph that may be a fake heading: {txt!r}")
    # tables: header row fill
    for t in tables(body):
        row0 = t["table"]["tableRows"][0]["tableCells"]
        fills = [rgb(c.get("tableCellStyle", {}), "backgroundColor") for c in row0]
        if not all(close(f, (0xEE / 255, 0xF3 / 255, 0xF7 / 255)) for f in fills):
            problems.append(f"table@{t['startIndex']}: header row fill is not #EEF3F7 ({fills[:1]})")
    for side in ("marginTop", "marginBottom", "marginLeft", "marginRight"):
        m = dstyle.get(side, {}).get("magnitude")
        if m != MARGIN_PT:
            problems.append(f"{side} is {m}, expected {MARGIN_PT}pt")

    print("paragraph styles:", counts)
    print("fonts seen:", sorted(f for f in fonts if f))
    print("tables:", len(tables(body)))
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for x in problems[:60]:
            print(" -", x)
        if len(problems) > 60:
            print(f" ... and {len(problems) - 60} more")
        sys.exit(1)
    print("\nStyle check passed.")


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    cmd, path = sys.argv[1], sys.argv[2]
    doc = load(path)
    if cmd == "info":
        cmd_info(doc)
    elif cmd == "outline":
        cmd_outline(doc)
    elif cmd == "find":
        cmd_find(doc, sys.argv[3])
    elif cmd == "fix":
        cmd_fix(doc)
    elif cmd == "check":
        cmd_check(doc)
    else:
        print("unknown command:", cmd)
        sys.exit(2)


if __name__ == "__main__":
    main()
