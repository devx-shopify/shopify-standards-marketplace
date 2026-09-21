---
name: decide
description: >
  Record a project decision as a numbered file in docs/decisions/, or supersede
  an earlier decision and flag every work item and PRD that cited it. Use
  whenever a human answers a question that fixes direction, scope, approach,
  or a shared-file change, and whenever an existing decision is being changed.
  Called by clarify, plan, execute, fix, and brainstorm; also usable directly
  when someone says "record this decision" or "we're changing D-004".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Decide: the project decision registry

One decision, one file, one human name on it. Decisions are how a change of
direction becomes traceable: every work item and PRD cites the decision IDs it
depends on, so when a decision changes, the things it invalidates are a grep.

**This skill never decides anything.** It records what a human decided. If you
cannot name the human, do not record; return to the caller and have it ask.

## Input

`$ARGUMENTS`, in either form:

```
record "<title>" --work {slug | roadmap-{track} | none} --by {name or handle}
       [--context "..."] [--decision "..."] [--consequences "..."]
       [--evidence <url or path>]

supersede D-{old} "<new title>" --work {...} --by {...} [same optional fields]
```

Natural language is fine ("record that the cart drawer closes on navigation,
decided by Priya in this thread"). Extract the fields. Anything not stated and
not recoverable from the conversation is asked for by the caller, not invented
here.

## Step 1: Resolve the ID

1. `mkdir -p docs/decisions/`
2. `Glob('docs/decisions/D-*.md')`. Take the highest number, add one, zero-pad
   to three digits. Empty folder: `D-001`.
3. Slug the title to kebab-case, at most six words. File is
   `docs/decisions/D-{NNN}-{slug}.md`.

## Step 2: Write the record

Read `${CLAUDE_SKILL_DIR}/templates/decision-template.md` and fill every field.
Rules for the content:

- `decided_by` is a person. If the answer came from a Slack thread, use the
  handle of the person who answered. If it came from a terminal session, use
  the git user name. If neither is known, stop and return to the caller.
- `work` is the work slug when called from the pipeline, `roadmap-{track}`
  when called from brainstorm, `none` when standalone.
- `evidence` is the thread permalink, PR, or document the decision came from.
  Write `none` rather than guessing.
- The Decision paragraph is the contract. It must be checkable against future
  code. "Use sessionStorage for drawer state" is a decision. "Handle state
  sensibly" is not; push back to the caller for the real answer.
- Context names the alternative that lost. A decision with no alternative was
  not a decision; record it only if the caller insists.

## Step 3: Supersede (only for `supersede`)

1. Open `docs/decisions/D-{old}-*.md`. Set `status: superseded` and
   `superseded_by: D-{NNN}`. Change nothing else in it. History is preserved,
   never rewritten.
2. In the new file set `supersedes: D-{old}`, and open the Context with one
   sentence on what was wrong or what changed.
3. Find everything that cited the old decision:
   ```bash
   grep -rl "D-{old}" docs/work docs/roadmap* docs/roadmaps 2>/dev/null
   ```
4. For each hit:
   - A file under `docs/work/{slug}/`: append to that work item's `intake.md`
     under `## Notes`: `{date}: D-{old} superseded by D-{NNN}. Re-check
     {clarify.md | plan.md} before continuing.`
   - A PRD under a roadmap: in that roadmap's `status-log.md`, add a row to the
     Deviations & Decisions Log: `| {PRD number} | D-{old} superseded by
     D-{NNN} | {one-line why} |`. If the PRD's tracker row is not `Done`, set
     its Status to `Blocked` and its Notes to `stale: D-{old}`.
5. List every flagged file in your report. That list is the blast radius.

## Step 4: Persist

The sandbox does not survive a pause. Stage `docs/decisions/` and every
`intake.md` or `status-log.md` you touched, commit with the message
`decide: D-{NNN} {slug}`, and push with `git push origin HEAD`. Stay on the
current branch; this skill never creates one. If there is no remote, or the push
is rejected, say so in one line and continue. Do not fail the skill over
persistence.

## Step 5: Report

Return to the caller, in this shape, nothing more:

```
Recorded D-{NNN}: {title} (decided by {name})
Supersedes: D-{old} | none
Flagged as stale: {n} items
  - docs/work/{slug}/intake.md
  - docs/roadmap-{track}/status-log.md (PRD 2.3)
```

## Rules

- One decision per file. Two questions answered means two files.
- Never delete a decision file. Never edit the Decision paragraph of an
  existing file. Supersede instead.
- `decided_by` is never Claude, second-brain, or "the team". A name or handle.
- Do not record choices nobody debated. A decision has an alternative that lost.
- IDs are assigned by the highest existing number plus one, never reused, never
  renumbered.
