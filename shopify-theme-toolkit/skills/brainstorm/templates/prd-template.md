# PRD: {N.M} - {PRD title}

**Phase:** {N} {phase name}
**Priority:** {P0 / P1 / P2}
**Depends on:** {list of PRD numbers with titles, or "None, can start immediately"}
**Estimated scope:** {Small (1-3 files) / Medium (4-7 files) / Large (8+ files)}

## Design Reference

<!-- Include this section ONLY when a Figma design exists for this PRD. Omit entirely otherwise. -->

- **Desktop:** {Figma URL for the desktop frame}
- **Mobile:** {Figma URL for the mobile frame, or "Same file as desktop"}
- **Frames:** {Which sections/frames in the Figma file correspond to this PRD}

> Run `/figma-rest` with these URLs before running `/clarify` for this PRD.

## Context

{2-4 sentences. What state the project is in when a developer picks this up.
What prior PRDs built that this builds on, referenced by path, e.g., "After 1.1
(docs/roadmap/phase-1-foundation/1.1-design-tokens.md), the color and spacing
tokens exist." A page PRD names every shared PRD it uses, by path, and does
not re-specify them.}

**Interfaces:** {Shared snippet: its `render` parameters. Shared section: the setting
IDs and blocks pages configure. Page PRD: the shared interfaces it uses, with
exactly those names. Omit for PRDs with no shared interface.}

## Goal

{1-2 sentences. What this PRD delivers when done. Written as a deliverable,
not a process. "A working user registration flow with email verification"
not "Implement user registration."}

## Requirements

### Functional
- {Specific, testable behavior}
- {Specific, testable behavior}
- {Specific, testable behavior}

### Non-Functional
- {Performance, security, accessibility, or quality requirement, only if relevant}

## Approach

{4-8 sentences. The recommended technical approach. Specific enough that a developer
or AI pipeline knows HOW to build this: name the section and snippet files, schema
settings and blocks, data sources (metafields with namespace and key), and patterns.
Not pseudocode, clear direction.}

## Expected Output

- {File or artifact 1, with purpose}
- {File or artifact 2, with purpose}

## Dependencies

### Upstream (must be done first)
- {PRD X.Y: what it provides that this PRD needs}

### Downstream (unblocked by this PRD)
- {PRD X.Y: what it can start once this is done}

## Constraints

- {Technical constraint relevant to this PRD}
- {Platform limitation or decision from brainstorming that limits approach}

## Acceptance Criteria

- [ ] {Verifiable criterion: a developer can check this off}
- [ ] {Verifiable criterion}
- [ ] {Verifiable criterion}
- [ ] {Edge case criterion: blank settings, zero blocks, empty collection, missing image}
