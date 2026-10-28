# TDD - <Client> - <Project>

Version: v1, YYYY-MM-DD

<!--
How to use this template
- Keep all 11 sections, in this order, with these exact names. If a section has nothing yet, write one sentence saying so and add a Q-n item.
- Every fact needs a source (brief, Figma, call notes, repo, or "decided by <person> on <date>"). If you cannot source it, it goes to Open questions, not into the body.
- Tables: first row is the header. No empty header cells.
- Diagrams: [[DIAGRAM n: Name]] line, then right under it a table or list with every fact the diagram shows.
- No em dashes or en dashes anywhere. Use commas, periods or "to".
- Project-wide facts only. No per-section field lists, acceptance criteria, coding standards, estimates or pixel specs.
- These comment blocks are removed by the converter; delete them anyway when done.
-->

## 1. Overview

<!-- One short paragraph on what the project is. Then the facts table. -->

| Item | Value |
|---|---|
| Client | |
| Goal | |
| Launch date | |
| Base theme | <themex boilerplate, Dawn, or existing theme name and version> |
| Store URL | |
| Preview URL | |
| Figma file | |
| Sources used for this TDD | <list each input: brief link, Figma link, call notes, repo> |

### In scope

- 

### Out of scope

- 

[[DIAGRAM 1: Architecture]]

<!-- Facts table for the architecture diagram: every box and every arrow as a row. -->

| From | To | What moves | How |
|---|---|---|---|
| | | | |

## 2. Page inventory

<!-- One row per template. Type is New or Change. Figma links to the exact frames. Template is the Shopify template name, e.g. product, product.bundle, page.about. -->

| ID | Template | Purpose | Type | Figma desktop | Figma mobile |
|---|---|---|---|---|---|
| P1 | index | | New | | |

[[DIAGRAM 2: Page and section map]]

<!-- Facts list: each page and the sections on it, top to bottom, using the section IDs from section 5. -->

| Page | Sections, top to bottom |
|---|---|
| P1 index | |

## 3. Design system

<!-- For each token: value, and whether the merchant can change it in theme settings or it is a fixed CSS variable. Values come from Figma only; anything not found is a Q-n. -->

### Colors

| Token | Value | Used for | Theme setting or fixed CSS variable |
|---|---|---|---|
| | | | |

### Type scale

| Token | Font | Size desktop | Size mobile | Weight | Line height | Theme setting or fixed |
|---|---|---|---|---|---|---|
| | | | | | | |

### Spacing and breakpoints

| Token | Value | Notes |
|---|---|---|
| | | |

### Buttons

| Variant | Use | States designed | Theme setting or fixed |
|---|---|---|---|
| | | | |

## 4. Global UI

<!-- Behaviour, not looks. One H2 per element that exists in this project. -->

### Header and mega menu

- 

### Announcement bar

- 

### Footer

- 

### Cart

<!-- Cart drawer or cart page, what opens it, what it shows, upsells, free shipping bar, notes, discount codes. -->

- 

[[DIAGRAM 3: Cart flow]]

| Step | User action | What the store does |
|---|---|---|
| 1 | | |

### Search

- 

### Popups

- 

## 5. Shared building blocks

### Components

<!-- Snippets and blocks that repeat across pages. -->

| ID | Component | Where it appears | Notes |
|---|---|---|---|
| C1 | Product card | | |

### Shared sections

| ID | Section | Purpose | Base theme already has it |
|---|---|---|---|
| S1 | | | |

### Section reuse matrix (draft)

<!-- Rows are sections, columns are page IDs from section 2. Yes or blank. -->

| Section | P1 |
|---|---|
| S1 | |

## 6. Data model

### Metafields

| namespace.key | Type | Owner | Used by | Filled by |
|---|---|---|---|---|
| | | | | |

### Metaobjects

| Type | Fields | Used by |
|---|---|---|
| | | |

### Tags, collections and filters

- 

[[DIAGRAM 4: Data flow]]

| Data | Source | Stored in | Shown on |
|---|---|---|---|
| | | | |

## 7. Apps and integrations

| App or service | Purpose | How it connects | Pages | Notes |
|---|---|---|---|---|
| | | App block, App embed, or Custom code | | |

## 8. Merchant editing

| Area | Merchant can change in theme editor | Fixed in code |
|---|---|---|
| | | |

## 9. Non-functional

| Item | Target | Source |
|---|---|---|
| LCP | | |
| CLS | | |
| JS weight | | |
| Accessibility level | | |
| Browsers and devices | | |
| SEO | | |
| Markets and languages | | |

## 10. Decisions

<!-- IDs are never reused or renumbered. An answered question moves here with "(Was Q-n, decided in vN.)". -->

| ID | Decision | Reason | Decided by, date |
|---|---|---|---|
| DEC-1 | | | |

## 11. Open questions

<!-- IDs are never reused or renumbered. When answered, the row moves to Decisions. -->

| ID | Question | Owner | Blocks | Asked in |
|---|---|---|---|---|
| Q-1 | | | | v1 |
