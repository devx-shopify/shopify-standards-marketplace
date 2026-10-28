# Updating an existing TDD

Use this when the user gives a link to a TDD that already exists. The Doc is edited in place so its link never changes, because brainstorm and the PRDs point at that link. Never create a second TDD for the same project.

Drive can only turn HTML into a Doc when it creates a new file. It cannot replace the content of an existing Doc. So an update is always a set of small Google Docs `update_doc` edits: insert text, replace text, delete a range, add or remove a table row, set a style.

If the `google-workspace` skill is available, read its `references/docs.md` too. Its rules on positions, revision guards and table edits apply here.

## Steps

1. **Read the current text.** Drive `read_file_content` with `includeComments: true`. Use it to understand what the Doc says. Never compute positions from it.
2. **Work out the changes** from what the user asked, plus the fixed bookkeeping for every update:
   - Version line: `Version: vN, YYYY-MM-DD` becomes `vN+1` with today's date.
   - Every change gets a DEC-n row in Decisions (next unused number), with a one-line reason.
   - An answered question: its Q-n row is removed from Open questions, and its DEC-n row ends with "(Was Q-n, decided in vN+1.)". Q and DEC numbers are never reused or renumbered.
   - New unknowns get new Q-n rows.
   - If a page, section or component changes, update every place it appears: page inventory, the DIAGRAM facts tables, the reuse matrix.
3. **Show the change list and wait for approval.** One line per edit, grouped by section, for example:
   - Page inventory: add row P7 page.store-locator, New, Figma links.
   - Section reuse matrix: add column P7.
   - Open questions: remove Q-3. Decisions: add DEC-5 "Use Judge.me for reviews. Reason: client already pays for it. (Was Q-3, decided in v3.)"
   - Version: v2 to v3.
   Also list which diagrams need re-exporting, if their facts changed.
4. **Read for positions.** Docs `read_doc`. The result is large; if it is saved to a file, run `python scripts/doc_info.py outline <file>` and `find <file> "text"` to get index ranges and the `revisionId`. If the result is cut off and not saved, use only `replaceAllText` edits, or tell the user the Doc is too large to edit by position here.
5. **Apply the edits** in as few `update_doc` calls as possible:
   - Text swaps that are unique in the Doc (the version line, one table cell value): `replaceAllText` with enough surrounding words to match only that place.
   - Everything else: index edits, ordered from the highest index to the lowest, with `writeControl.requiredRevisionId` from the latest read.
   - New table row: `insertTableRow` below the last row, then read again and fill the new cells at each cell's `startIndex + 1`, last cell first. Tested: a row added below a normal row takes that row's style (10pt, not bold). A row added directly below the header row comes out bold, so clear bold on it.
   - The version line, a filled cell and new table rows can go in one guarded batch (tested): row inserts first, highest table first, then text inserts from the highest index down, then `replaceAllText` for the version line.
   - New text must match what is around it: Manrope weight 400, black, 11pt in body, 10pt in tables. New headings must also be set bold and black directly. Set it with `updateTextStyle` after inserting.
   - New headings use `updateParagraphStyle` with `HEADING_1` or `HEADING_2`, never bold body text.
   - After any write, all earlier positions are stale. Read again before the next index edit.
6. **Verify.** Read again with `read_doc`, save it, and run `python scripts/doc_info.py check <file>`. Then read the text with Drive `read_file_content` and confirm each item in the approved change list is there. Report anything that did not land.
7. **If a change is too big** for small edits (for example reorganising most of a section), say so before starting and ask how to proceed. Do not quietly create a new Doc.

## Diagrams on update

If a diagram's facts changed, redraw it in Excalidraw, update its facts table in the Doc, and tell the user which DIAGRAM n placeholder needs a fresh PNG pasted in. The old pasted image stays until they replace it, so say clearly that it is now out of date.
