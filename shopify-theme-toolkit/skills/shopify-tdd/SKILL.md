---
name: shopify-tdd
description: Writes or updates the Technical Design Document (TDD) for a whole Shopify storefront project as a styled Google Doc, ready for /brainstorm to break into a roadmap. Use when the user asks to "write a TDD", "create a technical design document", "technical design for a Shopify project", "TDD for a client", "approach doc for a storefront build", or gives an existing TDD Google Doc link and asks to change it. One TDD per project, project-wide facts only. Replaces the older `tdd` skill for Shopify storefront work.
---

# shopify-tdd

Writes the one Technical Design Document for a Shopify storefront project, as a Google Doc.

## Who reads the TDD

1. **People** read the Google Doc and look at the diagrams.
2. **`/brainstorm`** (shopify-theme-toolkit, in Claude Code) reads the Doc through the Google Drive connector **as plain text only**. It builds the roadmap (foundation, shared components, shared sections, one phase per page, integration) and the PRDs from it.
3. **Reviewer agents** later check every PRD against the TDD text.

So every fact must exist in text. A fact that only lives in a diagram image does not exist for brainstorm.

## Scope

One TDD per project. Project-wide facts and decisions only.

- **In:** pages, architecture, shared components, data model, apps, global conventions, constraints, decisions, open questions.
- **Out:** per-section build detail (schema field lists), acceptance criteria, coding standards, task estimates, pixel specs. Link the Figma frames instead. Section-level detail belongs in the PRDs brainstorm writes.
- **Length:** 5 to 15 pages.

## Ground rules

- **Never invent a fact.** Every value comes from an input or from the user's answer. If it is unknown, it becomes a Q-n in Open questions. A default the user accepted is written as accepted ("default, accepted in interview").
- **IDs:** pages P1, P2...; components C1...; shared sections S1...; open questions Q-1, Q-2...; decisions DEC-1, DEC-2.... IDs are never reused or renumbered. An answered question moves from Open questions to Decisions with "(Was Q-n, decided in vN.)".
- **Plain writing.** Simple words, short sentences, no marketing tone.
- **No em dashes or en dashes anywhere**, in the Doc or in messages. Use commas, periods or "to".
- **Doc name:** `TDD - <Client> - <Project>`, for example `TDD - Mokobara - UAE Store`. The name never changes; the version lives inside the Doc.

Script and file paths in this skill are relative to the skill's own folder (`${CLAUDE_SKILL_DIR}` in Claude Code), not to the current project.

## Tools this skill needs

Check before starting. On surfaces where tools are deferred, search for and load them.

| Tool | Used for | If missing |
|---|---|---|
| Google Drive `create_file`, `read_file_content` | Create the Doc from HTML, read Docs as text | Write the Markdown only, tell the user which connector to turn on |
| Google Docs `read_doc`, `update_doc` | Fix font and margins, edit an existing TDD | New TDD: create it, but say the style fix needs this connector. Update: stop and ask the user to turn it on |
| Excalidraw `read_me`, `create_view` | Draw diagrams in the chat | Write the diagram facts tables only, and say so |
| Figma connector (optional) | Map pages and repeated components | Ask for frame links or a PDF export |
| Fathom, Granola (optional) | Read call notes | Ask the user to paste notes |

If the `google-workspace` skill is available, read its `references/docs.md` before the first Docs edit.

## Workflow for a new TDD

### 1. Collect inputs

Ask for, in one message:
- the Google Drive folder link where the Doc should go (required)
- client and project name (for the Doc name)
- whatever inputs exist: brief or PRD, Figma file, existing theme repo or base theme, call notes (Fathom, Granola)

### 2. Read everything first

Read every input before asking anything else.
- **Brief or PRD:** Drive `read_file_content`, or the uploaded file.
- **Figma:** keep calls few, because some seats have a low monthly limit. Start with the file's page and frame list, find the page frames and the components that repeat across them, and fetch detail only for those. If the `shopify-theme-toolkit:figma` skill is available, follow it. Do not fetch every frame.
- **Theme repo or base theme:** note what already exists (sections, snippets, settings) so the TDD builds on it instead of re-specifying it.
- **Call notes:** Fathom or Granola transcripts and summaries.

Then make a private fact sheet: each fact with its source, and a gap list for the 11 sections.

### 3. Interview about the gaps

- **One topic at a time.** Use the tappable question tool when it is available.
- Each question gives 2 to 4 options and marks a suggested default. Explain any technical term in plain words.
- Ask only about real gaps. Do not ask about anything the inputs already answer.
- If the user does not know, record it as Q-n with an owner instead of pushing for an answer.
- Usual order: overview facts (launch date, base theme, URLs, scope) > page list > global UI behaviour > shared blocks > data model > apps > merchant editing > non-functional targets.
- Non-functional targets have no house standard in this skill. You may suggest common ones (for example Core Web Vitals "good" thresholds, WCAG 2.1 AA), but they only go in the TDD if the user accepts them, marked as accepted defaults.

### 4. Draw the diagrams

Draw in the chat with Excalidraw (call its `read_me` first) so the user can see and edit them:
1. Architecture (store, theme, apps, external systems, data in and out)
2. Page and section map
3. Cart flow
4. Data flow

Skip one only if it has nothing in it for this project, and say why.

**Never try to put the image into the Doc.** The Drive connector cannot carry image data, and public image-rendering services would leak client data. Instead each diagram gets a placeholder line in the Markdown, `[[DIAGRAM n: Name]]`, which becomes "DIAGRAM n: Name (paste the PNG here)" in the Doc. Directly under it goes a table or list with every box, arrow and label from the diagram.

**Getting the PNG for the user to paste:**
- In Claude web or Cowork, the user exports each diagram from the Excalidraw view.
- In Claude Code, the terminal does not show the Excalidraw view. Save each diagram's elements array (the same JSON passed to `create_view`) as `diagram-n.json` and render it locally: `python scripts/render_diagram.py diagram-n.json diagram-n.png`. It needs Pillow (`pip install pillow`) and runs entirely on the machine; nothing is uploaded. Tell the user where the PNGs are.

### 5. Write the Markdown

Copy `templates/tdd-template.md` to a working file (for example `tdd.md`) and fill it in.
- Keep all 11 sections, in order, with their exact names. Empty section: one sentence saying so, plus a Q-n.
- Title line `# TDD - <Client> - <Project>`, then `Version: v1, YYYY-MM-DD` (today's date).
- `##` is Heading 1, `###` is Heading 2. The converter turns them into real `<h1>` and `<h2>`, so the Doc gets real heading styles. Never use bold text as a heading.
- Every table starts with a real header row.
- Remove the template's comment blocks.

Run the checker and fix every error:

```
python scripts/md_to_html.py tdd.md --check-only
```

### 6. Review with fresh context

Follow `references/review-checklist.md`. In Claude Code, use a subagent that gets only the Markdown, the inputs and the checklist. In Claude web or Cowork, do a separate, clearly scoped pass that re-reads only those files. Fix clear issues, ask the user about real decisions, at most 2 rounds.

### 7. Create the Google Doc

1. Convert: `python scripts/md_to_html.py tdd.md -o tdd.html`. The HTML keeps all styles in one `<style>` block (about 20 KB for a 5 page TDD). Drive maps that block onto the Doc's own styles, so body text arrives as Manrope 11pt black and headings get the right sizes. Use `--inline-styles` only if a future Drive change stops honouring the block; that file is about 6 times bigger.
2. Create with Drive `create_file`:
   - `title`: `TDD - <Client> - <Project>`
   - `contentMimeType`: `text/html`
   - `textContent`: the full HTML file content
   - `parentId`: the folder ID from the folder link (the part after `/folders/`)
3. Fix what Drive does not carry over, in one `update_doc` call:
   - `read_doc` the new Doc. The result is large (several MB) and is usually saved to a file. Run `python scripts/doc_info.py fix <file>` and pass its output as the `requests` and `writeControl` of one `update_doc` call.
   - It sets 54pt margins (Drive uses 72pt), gives the first line the Title style and then sets its 24pt bold black again (applying Title wipes them), makes every heading bold and black (Drive drops heading bold), sets keep-with-next on headings, stops table rows splitting across pages, and pins each table's header row. It forces Manrope on the body only if the Normal text style is not already Manrope.
   - Tested limits: `updateNamedStyle` is listed in the tool description but the connector rejects it, so headings are styled directly, not through the heading style.
4. Verify: `read_doc` again, save, run `python scripts/doc_info.py check <file>`. It checks fonts, sizes, bold and color for title, headings, body and table text, the header fill, margins, dashes, and bold paragraphs that look like fake headings. Fix what it reports.
5. Read the Doc with Drive `read_file_content` (with `includeComments: true`) and confirm the page inventory, the DIAGRAM fact tables and the reuse matrix read correctly as text, since that is what brainstorm sees. Known quirk: Drive's text export shows every Docs table with an empty first row, then the real header as a bold row. This cannot be changed from the Doc (pinning the header row does not change it). The facts are complete; brainstorm should treat the first bold row as the header.

### 8. Hand over

Short message:
- The Doc link, with the name as the link text.
- Which DIAGRAM placeholders need a PNG pasted in.
- Open questions count, and the ones that block the most work.
- Anything the review found that is still open.
- Remind the user that developers running `/brainstorm` need at least view access to the Doc.

## Updating an existing TDD

Follow `references/update-procedure.md`. In short: edit in place (same link), show the change list and wait for approval, bump the version, record each change as a DEC-n, then read back and check.

## Files

| File | What it is |
|---|---|
| `templates/tdd-template.md` | The 11-section TDD template |
| `scripts/md_to_html.py` | Checks the Markdown against the rules, then converts it to styled HTML (standard library only) |
| `scripts/doc_info.py` | Reads a saved `read_doc` result: positions, the style-fix request, the style check |
| `scripts/render_diagram.py` | Renders an Excalidraw elements JSON to a PNG locally (Pillow), for surfaces that cannot show the Excalidraw view |
| `references/review-checklist.md` | What the fresh-context reviewer checks |
| `references/update-procedure.md` | How to edit an existing TDD in place |

## devx document style (applied by the scripts)

- Manrope, normal weight
- All text black (#000000), including the title and headings; nothing is colored
- Tables bordered, header row filled #EEF3F7
- Title 24pt bold, Heading 1 16pt bold, Heading 2 13pt bold, body 11pt, table text 10pt
- Margins 54pt (0.75 inch)
