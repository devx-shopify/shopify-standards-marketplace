---
name: plan
description: >
  Create a detailed technical specification for a feature. Produces per-file
  decisions (settings, classes, tokens, structure) so /execute has zero
  creative decisions. Use after /clarify when requirements are confirmed.
allowed-tools: Read, Write, Grep, Glob, Agent, Skill, AskUserQuestion
---

# Plan — Technical Specification

You are entering the Plan phase. Your job is to produce a specification so detailed that `/execute` is pure implementation — zero decisions, zero guessing.

**Plan produces DECISIONS, not CODE.** The plan specifies what settings, what classes, what tokens, what structure. /execute writes the actual code using those decisions + skill standards.

**Do NOT write implementation code. Pseudocode or brief snippets ONLY when referencing existing codebase patterns that must be followed.**

## Input
Context or overrides: `$ARGUMENTS`

## Artifact Resolution
1. If `$ARGUMENTS` contains `--work {slug}`, use that slug. Otherwise read `docs/work/.current` for the active feature name
2. If the file doesn't exist, look in `docs/work/` for feature folders containing `clarify.md`
3. If one folder exists → use it
4. If multiple folders exist → ask the user which feature to plan
5. If no clarify.md found → ask the user to run `/clarify` first

Read from `docs/work/{feature-name}/`:
- `clarify.md` — the requirements (REQUIRED)
- `design-tokens.json` — available design tokens (if exists)
- `design-context.md` — design specs: typography, colors, spacing, layout (if exists)

---

## Process

### Step 1: Read All Inputs
Read the requirements and all available artifacts. Understand the full picture before analyzing the codebase.

### Step 2: Analyze the Codebase
Use `Glob` and `Grep` for quick context:
- `Glob('sections/*.liquid')` — existing sections
- `Glob('snippets/*.liquid')` — reusable snippets
- `Glob('assets/*.css')` + `Glob('assets/*.js')` — asset files
- `Glob('templates/*.json')` — templates
Then dispatch the **codebase-analyzer** agent:

> Analyze this Shopify theme codebase to inform planning for: [one-line task description from requirements]
>
> Read `docs/work/{feature-name}/clarify.md` for requirements.
> If `docs/work/{feature-name}/design-context.md` exists, read it for design context.
>
> Focus on:
> - Naming conventions (file names, setting IDs, CSS class prefixes)
> - Existing snippets and utilities to REUSE
> - Potential naming conflicts to AVOID
> - File locations and organization
>
> Do NOT recommend code patterns, CSS architecture, or schema structures —
> plugin standards are the authority for those. Report what EXISTS for naming
> and conflict detection only.

The agent discovers naming conventions, reusable code, and potential conflicts. Plugin standards (loaded via Skill tool during /execute) are the authority for code patterns, structure, and architecture. Use the agent's findings for naming and reuse decisions only.

### Step 3: Research (if needed)
If the requirements involve Shopify features you're not confident about after reading the codebase analysis:
- Dispatch a research subagent to search shopify.dev
- Only for genuine knowledge gaps
- Skip if the codebase analysis + requirements provide enough context

### Step 4: Design the Solution
Using the requirements + codebase analysis, make every decision:

**For each file to create/modify, decide:**

1. **File path** — following codebase naming conventions discovered by agent
2. **Schema settings** — exact IDs, types, labels, groups (following section-standards skill rules, with ID prefixes from codebase conventions)
3. **CSS classes** — exact BEM class names (following css-standards skill rules, with naming prefix from codebase conventions)
4. **Block types** — if section has repeatable content, exact block type names and their settings
5. **Null checks** — which settings need blank/empty guards
6. **Design values** — exact colors, font sizes, spacing, and layout from design-context.md
7. **CSS loading strategy** — preload (above fold) or lazy load (below fold)
8. **JS approach** — none, DOMContentLoaded, or Web Component (and why)
9. **Existing code to reuse** — snippets, patterns, utilities found by agent

**When the plan references an existing codebase pattern:** Include a brief note like "Follow wrapper pattern from testimonials.liquid — uses `data-section-id` attribute." This is pointing to a reference, not writing code.

### Step 5: Write the Specification

Write the plan to `docs/work/{feature-name}/plan.md`.

**Decisions before the spec.** Before writing, read every file in `docs/decisions/` whose title or work field touches this feature, and honor them. Any choice in Step 4 not dictated by the requirements, the standards, or an existing decision is a new decision. Inside the agent boundary (naming, file placement, internal structure) state it in the Approach section. Outside it (scope, a shared file, a new dependency or integration, or anything that contradicts an existing decision) stop, ask with `AskUserQuestion`, and record the answer with `Skill('decide')`. List every decision ID applied or created under `## Decisions` in plan.md.

Read the template structure from `${CLAUDE_SKILL_DIR}/templates/plan-template.md` and fill it in with the feature's specification. Every file must have a complete File Spec — no file is just a "TODO" without details.

### Step 6: Persist the Artifact

The sandbox does not survive a pause. Commit and push before asking for approval:

1. If the current branch is the default branch (`main` or `master`), create and switch to `feature/{feature-name}` first. Never commit artifacts to the default branch.
2. Stage `docs/work/{feature-name}/`.
3. Commit with the message `plan: {feature-name}`.
4. Push with `git push -u origin HEAD`. If there is no remote, or the push is rejected, say so in one line and continue. Do not fail the skill over persistence.

### Step 7: Present and Confirm
Save the plan to the artifact file. Then tell the user:
- Where the plan was saved
- A 2-3 line summary of the approach

Use `AskUserQuestion` to confirm:
- **Approve plan** — proceed to /execute
- **Request changes** — user provides feedback to revise the plan

**Do NOT output the full plan in conversation. The artifact file is the source of truth.**

### Next Step
Once the user confirms the plan, tell them:
```
→ Run /execute to implement the plan.
  Remaining: /execute → /compare (if built from Figma) → /assess
```

**Context tip:** If your conversation is getting long, you can `/clear` before running `/execute` — it reads from artifacts, not conversation history.

---

## Rules
- Zero creative decisions for /execute — if /execute has to decide, the plan failed
- Reference design-context.md for exact design values — never guess colors, sizes, or spacing when the design context specifies them
- Standards skills are the AUTHORITY for how code should be written — always follow them
- Codebase analyzer informs naming conventions (file names, setting ID prefixes, CSS class prefixes) and identifies reusable code — but never overrides standards for code patterns, structure, or architecture
- If the existing codebase violates standards, the new code STILL follows standards — do not replicate bad patterns
- If the task is too large (>8 files), suggest breaking into smaller plans
- Test cases must be specific and verifiable — "works correctly" is not a test case
