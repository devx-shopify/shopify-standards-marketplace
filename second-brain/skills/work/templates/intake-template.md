---
work: {slug}
origin: {clickup | figma | prd | bug | feature | brainstorm}
source: {ClickUp URL, Figma URL, PRD path, or "plain request"}
requested_by: {name or Slack handle}
date: {YYYY-MM-DD}
status: open
route: {skills in order, e.g. clarify -> plan -> execute -> assess}
branch: {feature/{slug} | fix/{slug}}
decisions: []
pr: none
---

# {slug}

## Request (verbatim)
{The request exactly as received. Links included. Do not paraphrase here.}

## Decision boundary for this work
- Agent decides: naming, file placement, internal structure, formatting, lint, tests, anything the plan already fixes.
- Human decides: any new or changed entry in docs/decisions/, any change of scope, any edit to a shared file, any new dependency or integration, and anything the requester reserved below.
- Reserved by requester: {quote it, or "nothing extra"}
- Shared files for this repo: {list from CLAUDE.md "## Shared files", or the default list}

## Notes
{Appended over time: stale-decision notices from decide, blockers, handoffs.}
