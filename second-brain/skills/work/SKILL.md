---
name: work
description: >
  The single entry point for any development request in this project: a plain
  ask, a bug report, a ClickUp task URL, a Figma URL, a PRD path from a roadmap,
  or a TDD to decompose. Classifies the request, sizes the pipeline to it, runs
  the right skills in order with a persistent work folder under docs/work/,
  stops for human decisions and records them, and finishes with a draft PR.
  Use for any request to build, change, fix, plan, or break down work. Prefer
  this over calling clarify, plan, execute, fix, figma, clickup, or brainstorm
  directly.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
---

# Work: the front door

You receive a request in any shape and turn it into finished, reviewable work.
You do not build anything yourself. You classify, set up the work folder, and
run the pipeline skills in the right order, carrying three constants that every
path inherits.

## The three constants

These hold on every route, for every size of task. They are not repeated in
each skill; they are enforced here.

**1. Decision boundary.** You decide alone: naming, file placement, internal
structure, formatting, lint, tests, and anything the plan already fixed. A
human decides: any new or changed entry in `docs/decisions/`, any change of
scope, any edit to a shared file, any new dependency or integration, and
anything the requester reserved in their message ("come back to me before
..."). Shared files are the list under `## Shared files` in the project's
`CLAUDE.md`; if there is none, use: the theme layout file, the settings schema,
base CSS and JS bundles, package manifests, and CI configuration. When a
human-class decision comes up at any step: stop, ask with `AskUserQuestion`,
record the answer with `Skill('decide')`, then continue. Never decide and note.

**2. Assess before PR.** No pull request opens until `assess` has run on the
work. Small tasks skip clarify and plan detail, never verification.

**3. Persist.** Every skill commits and pushes its artifacts as it goes. You
commit the intake before the first skill runs. Nothing lives only in the
sandbox.

## Input

`$ARGUMENTS`: the request, plus optional `--work {slug}` to resume or name a
work item explicitly.

## Step 0: Load project context

Read, if present: `CLAUDE.md`, the titles of every file in `docs/decisions/`
(one `Glob` and the first heading of each), and `docs/learnings.md`. Read the
full text of any decision whose title touches the area of the request. This
takes a minute and prevents the most expensive mistake: building against a
decision that already exists.

## Step 1: Classify

First match wins. Quote the trigger in your report.

| Signal in the request | Route |
|---|---|
| A ClickUp URL (`app.clickup.com/t/...`) or task ID | `clickup` |
| A Figma URL (`figma.com/design/...` or `figma.com/file/...`) | `figma` |
| A path under `docs/roadmap*/` ending in `.md`, or "PRD" naming one | `prd` |
| A path under `docs/inputs/` or `docs/tdds/`, an attached TDD or brief, or "brainstorm", "roadmap", "break this down", "decompose", "plan this project" | `brainstorm` |
| "grill", "interview me", "poke holes", "pressure-test" | `grill` |
| "explain", "understand", "how does", "walk me through" with no change asked | `understand` |
| "bug", "broken", "error", "exception", "not working", "regression", "crash", a stack trace, or "wrong on {device}" | `bug` |
| Anything else that asks for a change | `feature` |

If the request could be a bug or a feature and you cannot tell, ask one
question with `AskUserQuestion`. Do not guess.

## Step 2: Open the work folder

Skip this step for `brainstorm`, `grill`, and `understand`; they do not produce
a work item.

1. **Slug.** If `--work {slug}` was given, use it. Otherwise derive a kebab-case
   slug of at most four words from the request (`cart-drawer-scroll`,
   `hero-banner`). For `prd`, derive it from the PRD title.
2. **Resume check.** If `docs/work/{slug}/` already exists, this is a resume.
   Read `intake.md`, note which artifacts already exist (`clarify.md`,
   `plan.md`, `execution-log.md`, `assessment-report.md`), and skip to Step 4
   at the first missing artifact. Never redo a step whose artifact exists
   unless the requester asks.
3. **Create** `docs/work/{slug}/`. Write `intake.md` from
   `${CLAUDE_SKILL_DIR}/templates/intake-template.md`. The request goes in
   verbatim. Fill the decision boundary section from the constants above plus
   anything the requester reserved. For `prd`, copy the PRD's `Decisions` and
   `Depends on` lines into the intake.
4. **Set the pointer.** Write the slug to `docs/work/.current`. Skills read it
   as a fallback; you still pass `--work {slug}` explicitly to every skill so
   parallel threads never collide.
5. **Branch.** If the current branch is the default branch (`main` or
   `master`), create and switch to `feature/{slug}`, or `fix/{slug}` for the
   `bug` route. Record the branch in `intake.md`.
6. **Persist.** Stage `docs/work/{slug}/` and `docs/work/.current`, commit
   `work: intake {slug}`, push with `git push -u origin HEAD`. If there is no
   remote, or the push is rejected, say so in one line and continue.

## Step 3: Size the pipeline (`feature` route only)

Run `clarify` unless **all** of these are true:

- The request is unambiguous: one reading, no missing information.
- It touches at most two files.
- Nothing in it crosses the decision boundary.
- There is no design reference to interpret.

When all four hold, go straight to `plan`. When in doubt, clarify. A wasted
clarify costs minutes; a skipped one costs a rebuild.

## Step 4: Run the route

Invoke each skill with the `Skill` tool, passing `--work {slug}` and the
request or source. Use `TaskCreate` for each step so the checklist shows
progress. Skills stop on their own when they hit a question; that pause is the
system working. When the thread resumes, re-enter here with `--work {slug}` and
continue from the first missing artifact.

| Route | Sequence |
|---|---|
| `clickup` | `clickup` (it fetches the task and routes to clarify or fix) → then the `feature` or `bug` sequence below from that point |
| `figma` | `figma` → `clarify` → `plan` → `execute` → `compare` → `assess` |
| `prd` | read the PRD and every decision it cites → `clarify` with the PRD path as the request → `plan` → `execute` → `assess` → update the roadmap's `status-log.md` (see below) |
| `brainstorm` | `brainstorm` → stop. It writes the roadmap and no code. |
| `grill` | `grill-me` on the named target → stop |
| `understand` | `understand` → stop |
| `bug` | `fix` → `assess` |
| `feature` (small) | `plan` → `execute` → `assess` |
| `feature` (full) | `clarify` → `plan` → `execute` → `assess` |

**Roadmap bookkeeping for `prd`.** When the sequence starts, set the PRD's row
in `docs/roadmap-{track}/status-log.md` to `In Progress` with today's date.
When it finishes, set `Done`, or `Done with deviations` if any D-file was
created during the work, and add one row per created decision to the
Deviations & Decisions Log.

**After `assess`.** Read the verdict.

- `PASS`: continue to Step 5.
- `FAIL`: run `fix` once with the assessment report as input, then `assess`
  again. If it still fails, stop. Report what failed and what a human needs to
  decide. Do not open a PR.

## Step 5: Open the draft PR

Only after `assess` passed.

```bash
gh pr create --draft \
  --title "{slug}: {one line from the request}" \
  --body "$(cat <<'EOF'
## Request
{verbatim request, with source link}

## Work folder
docs/work/{slug}/

## Decisions
{one line per D-id created or applied, with decided_by; or "None"}

## Assessment
{verdict and one-line summary from assessment-report.md}

## Files
{list from execution-log.md}
EOF
)"
```

If `gh` is unavailable or the PR cannot be created, say so and report the
branch name instead. Update `intake.md`: `status: pr-open`, `pr: {url}`,
`decisions: [...]`. Commit `work: pr {slug}` and push.

## Step 6: Report

One message, this shape:

```
Route: {route} (trigger: "{quoted signal}")
Work: docs/work/{slug}/ on {branch}
Decisions: D-014 (Priya), D-015 (Aditya) | none
Assess: PASS | FAIL: {one line}
PR: {url} | not opened: {why}
Needs a human: {the question, or "nothing"}
```

## Rules

- You never write code, plans, or requirements yourself. Skills do. You route.
- `execute` is only ever reached through `plan`. Never call it directly.
- Pass `--work {slug}` to every skill. The `.current` file is a fallback, not
  the mechanism.
- One request, one work folder, one branch, one PR. A request that is really
  three tasks becomes three work items; say so and ask which to start.
- If a skill stops with a question, do not answer it yourself. The pause is
  the point.
