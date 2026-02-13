---
name: doc-revision
description: Generate enterprise documents by learning template structure from previous versions (PDF/Word/Markdown). Extract formatting, hierarchy, and section patterns from uploaded documents, then guide section-by-section construction with controlled interviews. Use when user provides a previous document version and wants to create an updated version (e.g., "Feature X test plan 2.1", "Write next version of this document", "Update this enterprise document based on previous PDF"). This is a template intelligence engine, not a template loader - it dynamically learns and applies document patterns.
---

# Document Revision

This skill enables Claude Code to generate new enterprise documents by:

- Extracting template structure from a previous version (PDF or similar)
- Learning formatting, hierarchy, and section content shape
- Dynamically classifying section stability
- Driving a controlled, section-by-section construction workflow
- Producing Confluence-ready output
- Minimizing PM/BA cognitive load

**This is NOT a template loader.**
**This is a template intelligence and structured construction engine.**

---

## 1. Trigger Conditions

Activate when user intent includes:

- "Write next version of this document"
- "Feature X test plan 2.1"
- "Generate updated version based on previous PDF"
- "Use this document as template"
- "Update this enterprise document"

**Input Requirements:**

- A previous version of an enterprise document (PDF / Word / Markdown)
- A short prompt describing the new version scope

---

## 2. High-Level Workflow

The workflow has five phases:

1. **Template Extraction**
2. **Section Taxonomy & Stability Classification**
3. **Controlled Build Plan**
4. **Section-by-Section Construction Loop**
5. **Confluence Renderer Output**

---

## 3. Phase 1 — Template Extraction

Claude must analyze the uploaded document and extract:

### 3.1 Structure

- Section hierarchy (1 / 1.1 / 1.1.1)
- Heading levels (H2 / H3 / H4 mapping)
- Section titles
- Subsection depth

Build a structured tree representation internally.

### 3.2 Formatting Rules

Identify:

- Numbering pattern
- Bold conventions
- Table header formatting
- Paragraph style patterns
- Bullet usage patterns
- Link formatting style

### 3.3 Section Shape Detection

For each section/subsection, determine:

- Paragraph-based
- Table-based
- List-based
- Hybrid

If table-based:

- Extract column names
- Identify whether rows represent atomic units

### 3.4 Content Pattern Inference

For each section, infer:

- Is this informational?
- Is this administrative metadata?
- Is this evolving content?
- Is this decision/criteria driven?
- Is this large table content?

This inference is used later for stability classification.

### 3.5 Metadata Handling

**CRITICAL: Never ask users about document metadata.**

Common metadata fields in enterprise documents:

- **Status** (Draft / In Review / Approved / Final)
- **Version Number** (1.0, 2.0, 2.1, etc.)
- **Author / Owner**
- **Approvers / Reviewers**
- **Last Modified Date**
- **Next Review Date**

**Default Value Strategy:**

| Field | Strategy |
|-------|----------|
| Status | Always set to **"DRAFT"** |
| Version | Inherit from previous version and increment patch (2.0 → 2.1), or extract from user prompt (e.g., "v2.1") |
| Author | Inherit from previous version or leave blank |
| Approvers | Inherit from previous version or leave blank |
| Last Modified | Use current date |
| Next Review Date | Inherit from previous version or leave blank |

**Rationale:**

- Generated documents are always drafts requiring human review
- Approval workflows are outside this tool's scope
- Users will manually update these fields during review process

---

## 4. Phase 2 — Section Taxonomy & Stability Classification

**Do NOT rely on section numbers.**

Instead classify each section into:

- **Stable**
- **Evolving**
- **Volatile**

### Guidelines:

**Stable:**

- Metadata
- Contact info
- Static environment info
- Process logistics

**Evolving:**

- Scope
- References
- High-level overview

**Volatile:**

- Risks
- Assumptions
- Entry/Exit Criteria
- Test Cases
- Requirement mappings

This classification is a recommendation, not a hard rule.

**Claude must show classification to user before construction.**

---

## 5. Phase 3 — Controlled Build Plan

Before writing content:

**Present:**

- Extracted section tree
- Stability classification
- Identified table sections

**Ask user:**

- Confirm classification adjustments
- Confirm document scope for new version

Use `AskUserQuestion` tool.

**Limit questions to:**

- Short
- High signal
- Directly relevant to structure

**Do NOT ask about formatting here.**

---

## 6. Phase 4 — Section-by-Section Construction Loop

Work strictly in order unless user overrides.

### 6.1 Stable Sections

**Behavior:**

- Show concise summary of previous content
- Ask: "Keep as is, modify, or rewrite?"
- If modify → ask targeted clarifying questions
- Convert casual answers into formal documentation language

**Exception: Metadata Sections**

If section contains only metadata (status, version, approvers, dates):

- **Do NOT ask user**
- Apply default values per Section 3.5
- Set status to "DRAFT"
- Inherit version and increment, or extract from user prompt
- Inherit author/approvers or leave blank
- Update last modified date to current date

### 6.2 Evolving Sections

**Behavior:**

- Show previous content summary
- Ask what has changed
- Rewrite section with updated content
- Confirm with user

### 6.3 Volatile Sections

**Behavior:**

- Do NOT inherit content
- Ask user high-level intent first
- Generate structured draft
- Use `AskUserQuestion` for review
- Iterate until approved

### 6.4 Table Sections (Row-Level Mode)

If a section contains a large table:

- Treat each row as atomic unit
- Work row-by-row:
  1. Draft row
  2. Review
  3. Revise
  4. Proceed to next row

**Never attempt to regenerate full table at once.**

---

## 7. Controlled Interview Rules

When using `AskUserQuestion`:

- Limit to 1–3 focused questions per turn
- Avoid obvious questions
- Avoid generic filler
- Only ask what impacts document correctness
- Never ask formatting questions
- Never ask speculative domain expansion questions

**NEVER ask about metadata:**

- ❌ "What status should this document have?" (Always DRAFT)
- ❌ "Who needs to approve this?" (Inherit or leave blank)
- ❌ "Is this document in review?" (Not relevant)
- ❌ "Who is the document owner?" (Inherit or leave blank)
- ❌ "What version number should this be?" (Extract from prompt or auto-increment)
- ❌ "When should this be reviewed next?" (Inherit or leave blank)

**Focus only on content substance:**

- ✅ "What changed in the new feature scope?"
- ✅ "What are the key test scenarios?"
- ✅ "What risks should be documented?"

---

## 8. Quality Check Rules

Quality checks must align with document role.

**Example:**

- For Test Plan → validate test coverage logic
- For BRD → validate requirement clarity

**Do NOT apply irrelevant quality checks.**

Ask user only when:

- Missing required logical element
- Contradiction detected
- Critical gap found

---

## 9. Integration With Other Skills

When needed:

- Use `content-research-writer` for formalization
- Use `pdf` skill for document parsing
- Use `docx` skill if Word export is requested

**Do NOT depend on external template files.**

---

## 10. Confluence Renderer

Output must:

- Preserve heading hierarchy
- Preserve numbering
- Render tables cleanly
- Use correct bold conventions
- Preserve links

**Output format must be copy-paste ready.**

- No markdown artifacts.
- No raw formatting syntax.

---

## 11. Document Profile System (Extensibility)

Internally support profile configuration.

Profile may define:

- Section pattern recognition hints
- Default stability suggestions
- Unit-of-work granularity
- Domain-specific validation rules

**Initial implementation:**

- Test Plan profile

**Future:**

- BRD
- PRD
- Risk Document
- Architecture Spec

**Profiles must not alter core engine.**

---

## 12. Strict Constraints

- Never auto-generate entire document at once.
- Always work incrementally.
- Always confirm before moving to next major section.
- Always preserve template style.
- Never introduce new sections unless user explicitly requests.
- **Never ask about document metadata** (status, approvers, version, dates)
- **Always treat output as DRAFT** requiring human review and approval
- **Apply safe defaults for all metadata fields** per Section 3.5

---

## 13. Version History & Current Scope

**Current Version: v0.3**

**v0.3 Changes (2026-02-13):**

- Added metadata handling strategy (Section 3.5)
- Document status always set to "DRAFT"
- Version numbers auto-increment or extracted from user prompt
- Author/approvers inherited or left blank
- Interview rules explicitly prohibit metadata questions
- Strict constraints updated to enforce metadata defaults

**v0.1 - v0.2:**

- Core template intelligence engine
- 5-phase workflow
- Section-by-section construction
- Controlled interviews

**Out of scope:**

- Enterprise approval workflow automation
- Compliance language injection
- Domain regulatory knowledge
- Prebuilt template libraries
- Version history tables

**Framework remains extensible for future inclusion.**

---

## END OF SKILL
