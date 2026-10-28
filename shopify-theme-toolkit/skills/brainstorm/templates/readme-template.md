# {Project Name}: Roadmap

**Generated:** {date}
**TDD source:** {Google Doc link}
**TDD snapshot:** `docs/tdd.md`, taken {YYYY-MM-DD}
**Total phases:** {phase-count}
**Total PRDs:** {prd-count}

## Overview

{3-5 sentences from the TDD. What this project is, what problem it solves, who it's for.}

## Page Inventory

| Template | Purpose | New / Change | Figma |
|----------|---------|--------------|-------|
| {index} | {purpose} | {New} | {frame link or "None"} |

## Section Reuse Matrix

Anything on two or more pages lives in a shared layer and is specified once. The PRD column says `pending` until that phase is decomposed.

| Section / snippet | {page} | {page} | {page} | Layer | PRD |
|-------------------|--------|--------|--------|-------|-----|
| {name} | x | x | | Shared sections | {3.1} |

## Phase Tree

```
{Mark every PRD with [PRD]. While brainstorming is in progress, mark phases
that are not yet decomposed with "PRDs pending".}

1. Foundation
   1.1 {Name} ........................ [PRD]
2. Shared Components
   2.1 {Name} ........................ [PRD]
3. Shared Sections
   3.1 {Name} ........................ [PRD]
4. {Page}
   4.1 {Name} ........................ [PRD]
   4.2 {Page} template ............... [PRD]
{N}. Integration
   {N}.1 {Name} ...................... [PRD]
```

## Execution Order

Delivery status lives in `status-log.md`, not here.

| Order | PRD | Path | Depends On | Can Parallel With |
|-------|-----|------|------------|-------------------|
| 1 | {name} | {path} | None | - |
| 2 | {name} | {path} | #1 | #3 |

## TDD Updates Needed

Decisions made during brainstorming that the TDD does not contain or contradicts. Update the Google Doc; the next `/brainstorm` run refreshes `docs/tdd.md` from it.

Diagram-only facts (shown in a diagram but not written in text) are listed here too, because brainstorm and the reviewers read only text.

| Decision | Why | TDD section |
|----------|-----|-------------|
| {decision} | {reason} | {section} |

## Open Review Findings

Findings from the fresh-context PRD review that were not resolved. Write "None" if every finding was fixed.

| PRD | Finding | Severity |
|-----|---------|----------|

## How to Use This Roadmap

Each file marked [PRD] is a self-contained specification. Hand PRDs to the pipeline one at a time, in the execution order above.

**Start here:** `{path-to-first-prd}`
