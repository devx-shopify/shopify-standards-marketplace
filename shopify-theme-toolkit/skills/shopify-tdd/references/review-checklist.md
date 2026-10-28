# TDD review checklist

The reviewer works with fresh context. It gets only these three things:

1. The TDD Markdown file.
2. The list of inputs (and their text, if they were files or notes).
3. This checklist.

It does not get the interview, the chat, or the writer's reasoning. That is the point: it reads the TDD the way brainstorm and the PRD reviewers will.

In Claude Code, run it as a subagent with exactly that input. In Claude web or Cowork, where there are no subagents, do it as a separate pass: start a new step, re-read only the Markdown file and the inputs from disk, and go through this list as if seeing the TDD for the first time.

## Run the script first

`python scripts/md_to_html.py tdd.md --check-only` catches the mechanical problems: section order, version line, table header rows, diagram fact tables, duplicate IDs, dashes. Fix all its errors before the manual review.

## Manual checks

Report each finding as: section, what is wrong, suggested fix, and whether it is a clear fix or needs a decision from the user.

1. **Coverage.** Every requirement in the inputs is either in the TDD body or listed as a Q-n. Go through the inputs line by line. List any requirement that is in neither.
2. **No invented facts.** Every value (date, URL, token value, metafield, app name, performance target) traces to an input or to an answer the user gave. A value with no source is a finding. Defaults suggested by the writer and accepted by the user count as sourced only if the TDD says so ("default, accepted by Aditya").
3. **Diagram facts in text.** Each DIAGRAM n placeholder is followed by a table or list that holds every box, arrow and label. A reader with no image must lose nothing.
4. **Brainstorm can build from text alone.** From the text only, could you write out: the full list of pages (with template names), the sections on each page in order, which sections are shared, and the reuse matrix? If any page in section 2 has no row in DIAGRAM 2's facts, or any section ID used anywhere is not defined in section 5, that is a finding.
5. **IDs are consistent.** Page IDs (P1...), component IDs (C1...), section IDs (S1...), Q-n and DEC-n are each defined once and every reference points to something that exists.
6. **No section-level build detail.** Remove per-section schema field lists, acceptance criteria, coding standards, task estimates, and pixel values that belong in Figma. Global tokens in section 3 are allowed.
7. **Open questions are usable.** Each Q-n has an owner and says what it blocks.
8. **Decisions have reasons.** Each DEC-n has a one-line reason.
9. **Plain writing.** No marketing language, no filler, no em dashes or en dashes.
10. **Length.** 5 to 15 pages (about 3,000 characters per page).

## After the review

- Fix every clear issue in the Markdown.
- Ask the user about each real decision, one at a time, with options and a suggested default.
- Run the review again. Stop after 2 rounds total, even if minor findings remain, and list what is left in the handover message.
