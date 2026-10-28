---
name: brainstorm
description: >
  Brainstorm a whole Shopify theme project from its TDD (a Google Doc link,
  snapshotted to docs/tdd.md) into one layered roadmap: foundation, shared components, shared sections, one phase
  per page, and integration. Builds a page inventory and a section reuse
  matrix so shared work is specified once, writes self-contained PRDs to
  docs/roadmap/, then has fresh-context reviewers check every PRD before
  handing over. Use only for a full project with multiple pages, when the
  developer says "brainstorm", "break this project down", "create a roadmap"
  or "plan this project". A single page or feature skips brainstorm and goes
  straight to the feature pipeline.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, WebSearch, WebFetch, Agent, TaskCreate, TaskUpdate, TaskList, mcp__claude_ai_Google_Drive__read_file_content, mcp__claude_ai_Google_Docs__read_doc
---

# Brainstorm: Project Decomposition into a Layered Roadmap

You are entering the Brainstorm phase. Your job is to take a project's TDD, think it through with the developer, and decompose the whole project into one roadmap of phases and self-contained PRDs that can each be handed to the feature pipeline.

**This is the outer loop, and it is for whole projects only.** The developer feeds each PRD into the inner loop (figma → clarify → plan → execute → verify → assess → fix) one at a time. The quality of the final output depends on how well you decompose the project here.

**Do NOT write code. Do NOT build anything. Only brainstorm, decompose, and produce PRDs.**

## Input

- The TDD's **Google Doc link**, in `$ARGUMENTS` or the conversation. **Required** on the first run. The TDD is written in Claude web or Cowork as a Google Doc, and the Doc is the source of truth.
- On later runs, the link stored in `docs/roadmap/README.md` (`**TDD source:**`) is used when no new link is given.
- Optional notes from the developer: `$ARGUMENTS`

You save a text snapshot of the Doc to `docs/tdd.md`. The fresh-context reviewers have no Google access and read the TDD from that file, and the snapshot records which version of the TDD the roadmap was built from.

## Fixed layout

One project, one TDD, one roadmap:

```
docs/
  tdd.md                          snapshot of the TDD Google Doc (refreshed each run)
  roadmap/
    README.md                     page inventory, section reuse matrix, phase tree,
                                  execution order, TDD updates needed, open review findings
    status-log.md
    phase-1-foundation/
      overview.md
      1.1-{slug}.md               PRD
    phase-2-shared-components/
    phase-3-shared-sections/
    phase-4-{page}/               one phase per page, in build order
    ...
    phase-{N}-integration/
```

`{ROADMAP}` below means `docs/roadmap`.

**Two levels only: phase folder, then PRD files.** Never nest sub-phase folders. The docs viewer only reads PRDs that sit directly inside a `phase-{N}-{slug}/` folder, so anything deeper is invisible on the board.

---

## Step 0: Confirm This Is a Project and Snapshot the TDD

1. If the request is a single page, section or feature, stop and say so:
   > Brainstorm is for whole projects. For a single page or feature, go straight to the pipeline: `/figma-rest` (if there is a design) → `/clarify` → `/plan` → `/execute` → `/figma-verify` → `/assess`.
2. **Find the TDD link.** Use the Google Doc link the developer gave. If none was given, read `**TDD source:**` from `docs/roadmap/README.md`. If there is neither, ask for the link. Take the document ID from the URL: the part after `/document/d/`, up to the next `/`.

3. **Read the Doc** through the Google connector:
   - Read the text with `mcp__claude_ai_Google_Drive__read_file_content` and the document ID. A large TDD does not fit inline: the tool saves the result to a file and gives you its path. **Never retype the Doc yourself.** If the result came back inline instead, save that tool output as-is to a scratch file.
   - Also call `mcp__claude_ai_Google_Docs__read_doc` with the same ID, only to count images and drawings. Its result is always large and saved to a file; do not read it, pass its path to the script below. Skip this if the Docs connector is not available.
   - If the Drive read does not work (connector not set up, no access to the Doc), tell the developer what failed and ask them to share the Doc with the connected Google account, or paste the TDD into the conversation (save the paste to a scratch file the same way). Do not brainstorm without the TDD.

4. **Write the snapshot with the script**, never by hand. It cleans the Drive text (escapes, table headers, bold-text headings), adds the snapshot header and reports tabs, tables, `DIAGRAM` placeholders without a facts table, and images per tab:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/snapshot_tdd.py" <saved Drive read> --link "<Doc link>" --doc-json <saved read_doc file> -o docs/tdd.md.new
   ```
   Write to `docs/tdd.md.new` first, then do step 6, then move it over `docs/tdd.md`. Use `--link "pasted in conversation"` for a pasted TDD, and leave out `--doc-json` when there is no `read_doc` file.

5. **Note what the text cannot carry.** Diagrams, drawings and images do not come through as text. Use the script's report.
   - A TDD written with `/shopify-tdd` marks each diagram as `DIAGRAM n: Name (paste the PNG here)` with a facts table right under it. That table is the diagram in text: use it. Only a placeholder with no facts table under it is a gap.
   - For any other diagram you can detect (an image, a drawing, or a caption that refers to one), tell the developer that facts living only in the picture are invisible to brainstorm and the reviewers.
   - Both kinds of gap go in **TDD updates needed**, so the Doc states those facts in text. Mermaid source written as text in the Doc is kept and can be read.
   - Images reported by the script that have no `DIAGRAM` facts table near them are diagram-only facts.

6. **Compare with the previous snapshot.** If `docs/tdd.md` already exists, compare it with `docs/tdd.md.new` (for example `diff` on the `#`/`##` headings, then on the changed sections) and summarize which sections changed. When revising a roadmap, that summary decides which phases and PRDs to revisit. Then move `docs/tdd.md.new` over `docs/tdd.md`.

7. **Read the snapshot** in chunks with `Read` (offset and limit) until you have read all of it. A large TDD can be over 100K characters; say so if any part could not be read.

---

## Step 1: Absorb the TDD and the Theme

1. **Use the snapshot you read in Step 0.** `docs/tdd.md` holds the TDD, the source of truth for project-wide decisions. Note what it decides, what it implies, and what it leaves open.

2. **Treat the TDD as read-only.** Never edit the Google Doc, and never change `docs/tdd.md` other than refreshing the snapshot in Step 0. When brainstorming decides something the TDD does not cover, or contradicts it, record it for the **TDD updates needed** list in the roadmap README. The developer updates the Google Doc, and the next run picks up the change.

3. **Check for an existing roadmap.** `Glob('{ROADMAP}/README.md')`. If found, read it:
   - If any phase is still marked `PRDs pending`, offer to **resume**: skip to Step 4 at the first pending phase.
   - Otherwise ask: revise it, extend it, or start fresh? When revising, read the existing structure and keep PRD numbers stable where the scope did not change.

4. **Scan the theme**, if one exists. Skip for a greenfield project.
   - `layout/theme.liquid`, `config/settings_schema.json`: global setup and theme settings
   - `templates/*.json`: which pages exist and which sections they use
   - `sections/`, `snippets/`, `assets/`: what is already built and reusable
   - `sections/*-group.json`: header and footer groups

5. **Map the designs.** Get the Figma URL(s) from the TDD, or ask for them. Record which frames belong to which page and which section. Not every PRD has a design: config, data and integration work usually does not.

6. **Separate what you know:**
   - **Decided by the TDD:** stated goals, constraints, architecture
   - **Implied:** requirements the TDD does not state but clearly needs
   - **Open:** what you must explore with the developer before you can decompose

---

## Step 2: Research

Research before asking questions, so you bring informed trade-offs instead of a questionnaire.

- Research when the project uses apps, APIs, metafield or metaobject patterns, or Shopify features you should understand deeply.
- Use `WebSearch` for known patterns and pitfalls, and `WebFetch` to read the full documentation page.
- Dispatch an `Agent` for parallel research when the project spans several domains.
- Skip research when the TDD is clear and the stack is familiar.

---

## Step 3: Page Inventory and Section Reuse Matrix

This step decides what is shared and what belongs to one page. It prevents the same section from being specified more than once.

A TDD written with `/shopify-tdd` already has a page inventory (P1, P2...), components (C1...), shared sections (S1...) and a draft section reuse matrix. Start from those and keep their IDs in the README, so PRDs and the TDD use the same names. Verify them against the designs and the theme instead of rebuilding them, and send any correction to **TDD updates needed**.

### 3a. Page inventory

List every template the project touches, for example `index`, `product`, `collection`, `list-collections`, `cart`, `search`, `page.about`, `page.contact`, `blog`, `article`, `customers/*`, `404`, `password`. For each one record its purpose, its Figma frames, and whether it is new or a change to an existing template.

### 3b. Section reuse matrix

Rows are sections, columns are pages. Mark every page a section appears on. Use the designs, the TDD and the existing `templates/*.json`.

```
| Section              | home | collection | product | cart | about | Layer        |
|----------------------|------|------------|---------|------|-------|--------------|
| featured-collection  |  x   |            |    x    |      |       | shared       |
| testimonials         |  x   |            |         |      |   x   | shared       |
| product-main         |      |            |    x    |      |       | product page |
```

Then classify every piece of work into a layer:

| Layer | What goes in it |
|---|---|
| **Foundation** | Design tokens, global CSS and JS, `layout/theme.liquid`, `config/settings_schema.json`, header and footer groups, cart drawer or other global UI, metafield and metaobject definitions, app embeds |
| **Shared components** | Snippets used on 2 or more pages: product card, price, badges, icons, buttons, media, forms |
| **Shared sections** | Sections that appear on 2 or more templates |
| **Page phases** | Sections that appear on exactly one template, plus that page's template JSON |
| **Integration** | Cross-page flows (navigation, search to product to cart), analytics, accessibility and performance passes |

**The rule:** anything used on two or more pages moves out of the page phases into a shared layer. A page PRD never re-specifies shared work. It references the shared PRD by path.

### 3c. Brainstorm the open questions

Explore the open questions from Step 1, one dimension at a time. Start with the most foundational, the one whose answer changes the structure.

Good: "The TDD says the product card shows a swatch row, but the collection design shows swatches only on hover. Should the shared product card own the swatch logic with a setting, or does the collection page need its own variant?"

Bad: "What are the requirements for the product card?"

After each answer, state back what you understood and what it changes in the structure. Use `AskUserQuestion` only for concrete choices between 2 to 4 options; use conversation for everything else.

### Structure review

Before Gate 1, write a draft `{ROADMAP}/README.md` from the template with the TDD source link and snapshot date, the page inventory, the reuse matrix (PRD column `pending`), the phase list with every phase marked `PRDs pending`, and any TDD updates found so far.

Dispatch one reviewer with `Check: structure` (see Step 9a for how to dispatch), giving it only the README and TDD paths. Fix clear-cut findings; bring design questions to the developer. Present the remaining findings at Gate 1.

### Gate 1: Approve the structure

Present:
- the page inventory
- the section reuse matrix with layers
- the phase list (foundation, shared components, shared sections, each page in build order, integration)
- any TDD updates found so far
- the structure review result

Ask with `AskUserQuestion`: **Approve**, **Adjust**, or **Keep brainstorming**. Do not move on without approval. After an adjustment, update the README and present again.

The approved README stays on disk with every phase `PRDs pending`. This lets a large project be paused and resumed between phases.

---

## Step 4: Deepen One Phase at a Time

Take each approved phase in order and split it into PRDs.

**A PRD is right-sized when:**
- it fits in a 60 to 90 line PRD
- it has one clear responsibility, usually one section, one snippet family, or one global concern
- a developer can pick it up without deciding where to start

**If a phase needs more than about 8 PRDs,** split it into two phases (for example `phase-6-product-core` and `phase-7-product-extras`) instead of nesting.

**Every page phase ends with a template PRD** that assembles the page's template file: section order, default content, and the settings each section needs on that page. Usually that is `templates/{page}.json`; customer pages live at `templates/customers/{page}.json`, and `gift_card` is `templates/gift_card.liquid`, not JSON.

### Gate 2: Approve each phase

Present the phase's PRD list, one line per PRD, and get approval before moving to the next phase. Update the README after each approved phase, including the PRD numbers in the reuse matrix. The developer can stop after any phase and resume later; on resume, read the README and continue from the first phase still marked `PRDs pending`.

---

## Step 5: Execution Order

Order the PRDs across the whole project:

- foundation first, then shared components, then shared sections, then pages, then integration
- within that, a PRD comes after everything it depends on
- mark what can run in parallel (pages are usually parallel to each other once the shared layers are done)

```
1. 1.1 design-tokens (no dependencies)
2. 1.2 theme-layout (depends on 1.1)
3. 2.1 product-card + 2.2 price (parallel, both depend on 1.1)
4. 3.1 featured-collection (depends on 2.1)
```

Confirm with the developer.

---

## Step 6: Generate PRDs

1. Create every phase folder in one command:
   ```bash
   mkdir -p docs/roadmap/phase-1-foundation docs/roadmap/phase-2-shared-components ...
   ```

2. Use `TaskCreate` to create one task per PRD, so the developer sees progress.

3. For each PRD, in execution order:
   - Read `${CLAUDE_SKILL_DIR}/templates/prd-template.md` and fill it in.
   - **Design Reference:** include the Figma URLs and frames when the PRD has a design; omit the section otherwise.
   - **Context:** what exists when this PRD starts, with prior PRDs referenced by path. A page PRD names every shared PRD it uses, by path.
   - **Approach:** specific. Name the section and snippet files, schema settings, blocks, metafields, and patterns.
   - **Acceptance Criteria:** verifiable, including empty and blank-setting states.
   - **Interfaces:** a shared snippet PRD names its `render` parameters; a shared section PRD names the setting IDs and blocks pages can configure. Page PRDs use exactly those names.
   - Write it to `{ROADMAP}/phase-{N}-{slug}/{N}.{M}-{slug}.md` and mark the task complete.

4. For each phase, fill `${CLAUDE_SKILL_DIR}/templates/overview-template.md` and write `{ROADMAP}/phase-{N}-{slug}/overview.md`.

### Naming

- Phase folders: `phase-{N}-{kebab-name}/`, for example `phase-4-home/`
- PRDs: `{N}.{M}-{kebab-name}.md`, for example `4.2-hero-slider.md`
- Every phase has an `overview.md`
- All names are kebab-case

---

## Step 7: Finish README.md

Complete `{ROADMAP}/README.md` from `${CLAUDE_SKILL_DIR}/templates/readme-template.md`:

- project overview from the TDD
- page inventory and section reuse matrix (from Step 3), with every PRD number filled in
- phase tree, every PRD marked `[PRD]`
- execution order table
- **TDD updates needed:** every decision made here that the TDD does not contain or contradicts, each with the TDD section it belongs in. Write `None` if there are none.
- start-here pointer to the first PRD

---

## Step 8: Scaffold the Status Log

Fill `${CLAUDE_SKILL_DIR}/templates/status-log-template.md` and write `{ROADMAP}/status-log.md`: one `### Phase N - Name` section per phase and one row per PRD in execution order, every row `Not Started`.

**The status vocabulary is fixed:** `Not Started` / `In Progress` / `Blocked` / `Done` / `Done with deviations`.

Nothing in the pipeline writes to this file automatically. The developer updates a row when a PRD moves, and the docs board (`/docs-viewer`) shows that status on the PRD's card.

---

## Step 9: Goldfish Review

You held the whole brainstorm in your head, so you cannot see what the files leave unsaid. Reviewers with no context can. They read only the files, and each runs one check, so no reviewer's view shapes another's.

### 9a. Dispatch reviewers

For every reviewer, use `subagent_type: "shopify-theme-toolkit:prd-reviewer"` if available; otherwise `general-purpose` with the full contents of `${CLAUDE_SKILL_DIR}/../../agents/prd-reviewer.md` pasted as its instructions.

Dispatch **all reviewers in one message** so they run in parallel:
- for each phase, three reviewers: `Check: comprehension`, `Check: antagonistic`, `Check: readiness`
- one more with `Check: roadmap`, for cross-PRD consistency

That is three reviewers per phase plus one, for example 25 for an 8-phase project. Tell the developer the count before dispatching.

Give each reviewer **only the check and paths**, never a summary of the conversation or your intentions:

```
Check: antagonistic
Phase folder: docs/roadmap/phase-4-home/
Roadmap README: docs/roadmap/README.md
TDD: docs/tdd.md
```

```
Check: roadmap
Roadmap folder: docs/roadmap/
Roadmap README: docs/roadmap/README.md
TDD: docs/tdd.md
```

If a reviewer fails or times out, do not review its PRDs yourself. Re-dispatch it once; if it fails again, list its check and phase under **Open review findings** as `not reviewed`.

### 9b. Use the results

1. **Comprehension:** compare each restatement with what was agreed with the developer. A mismatch means the PRD is ambiguous; rewrite the unclear part.
2. **Antagonistic findings:** fix clear-cut problems yourself (a missing path, an unlisted dependency, an unverifiable criterion). A finding that needs a design decision goes to the developer with `AskUserQuestion`. Never resolve a design question silently.
3. **Readiness:** every PRD marked `NO-GO` must be fixed or explicitly accepted by the developer.
4. **Roadmap findings:** fix duplicated scope, matrix drift and broken dependencies; ask the developer when the fix changes the structure.
5. **Re-review** only what you changed: for each phase with changed PRDs, dispatch the same three checks with a `PRDs:` line listing the changed PRD numbers. Re-run the `roadmap` check only if a change touched dependencies, shared scope or the matrix. **Stop after 2 rounds.** Anything still open goes in the README's **Open review findings** section.
6. New decisions from the review that belong in the TDD go in **TDD updates needed**.

---

## Step 10: Report to the Developer

Tell the developer:
- the roadmap is in `docs/roadmap/`, with the count of phases and PRDs
- the file tree of what was created
- the review result: reviewers dispatched, rounds run, findings fixed, findings still open
- the **TDD updates needed** list (including diagram-only facts), so they can update the Google Doc
- that `status-log.md` starts with every PRD at `Not Started`

Then:
```
Start here: docs/roadmap/{path-to-first-prd}

Hand each PRD to the pipeline one at a time, in the execution order in README.md.

With a Design Reference:
  /figma-rest [URLs from the PRD] → /clarify [PRD path] → /plan → /execute → /figma-verify → /assess

Without a design:
  /clarify [PRD path] → /plan → /execute → /assess
```

**Do NOT output PRD contents in conversation. The files are the source of truth.**

---

## Rules

### Scope
- Whole projects only. Single pages and features go to the pipeline.
- The TDD Google Doc is required and is the source of truth. `docs/tdd.md` is only its snapshot, refreshed at the start of every run and otherwise never edited. Gaps, contradictions and diagram-only facts go in **TDD updates needed**.

### Brainstorming
- Research before asking. No generic questionnaires.
- One dimension at a time, and state back what you understood after each answer.
- Write no files before the structure review except the `docs/tdd.md` snapshot. Until PRD generation, write only that snapshot and the README.

### Structure
- Layers in this order: foundation, shared components, shared sections, pages, integration.
- Anything used on two or more pages lives in a shared layer and is specified once.
- Two levels only: phase folder, then PRDs. Split a phase instead of nesting.
- Every page phase ends with a template PRD.
- If `docs/roadmap/` exists, ask before overwriting.

### PRDs
- 60 to 90 lines each. Longer means the scope is too large: split it.
- Self-contained: a developer who reads only that file knows what to build, why, how, what exists already, and what success looks like.
- Context references prior and shared PRDs by path.
- Acceptance criteria are verifiable checkboxes.
- Shared PRDs name their interfaces (`render` parameters, setting IDs); page PRDs use exactly those names.
- No PRD reaches the developer without the Goldfish review.
