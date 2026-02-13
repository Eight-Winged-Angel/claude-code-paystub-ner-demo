# Enterprise Structured Document Generation Framework

## Project Vision

We are building a **team-level reusable Enterprise Structured Document Generation Framework** to reduce the cognitive load of PMs/BAs when writing structured enterprise documents.

This is NOT:
- A one-off Test Plan writing tool
- A PRD generator
- A single-use prompt utility

This IS:
- A template-driven, controlled-interaction, version-aware, strongly constrained, extensible framework for structured enterprise documentation

---

## Core Objective

Reduce cognitive load through:
- **Template extraction** (not hardcoding)
- **Stability-based inheritance** (smart defaults)
- **Controlled, gap-focused questioning** (no unnecessary questions)
- **Incremental construction with review loops** (section-by-section)
- **Confluence-ready output** (copy-paste ready)

---

## Three-Layer Architecture

### Layer 1: Template Intelligence Layer
**Purpose**: Extract structure, formatting, and content shape from previous documents

**Responsibilities**:
- Parse previous doc (PDF/Word/Confluence export)
- Extract structure: sections, subsections, numbering rules
- Detect formatting: heading levels (H2/H3/H4), table structures, bold/normal text
- Identify "content shape" of each section
- Output: **Document Schema** (structured JSON/YAML)

**Key Principle**: Fully reusable across document types

---

### Layer 2: Structured Construction Engine (Core)
**Purpose**: The custom Skill we will build - orchestrates the entire document generation process

**Responsibilities**:

1. **Section Taxonomy & Stability Classification**
   - Classify content types (intro, table, checklist, narrative, etc.)
   - Classify stability (stable = inherit by default, unstable = force rewrite)
   - Determine unit-of-work granularity (section-level vs row-level)
   - **Key**: NOT hardcoded - decisions based on content type analysis

2. **Inheritance Decision Logic**
   - Stable sections → default inherit, ask user if changes needed
   - Unstable sections → force rewrite
   - Table sections → row-by-row iteration (smallest unit)
   - **Key**: Do not rely on section numbers (they may change)

3. **Controlled Interview Engine**
   - Uses AskUserQuestion tool
   - Length-limited questions
   - Gap-focused (no obvious questions)
   - Avoids unnecessary branching
   - User answers in casual language

4. **Incremental Writer**
   - Section-by-section construction
   - Subsection-by-subsection
   - Table row-by-row for large tables
   - Writes to SPEC.md progressively

5. **Formalization & Review Loop**
   - User provides casual input
   - Claude converts to formal documentation language
   - Shows preview
   - User confirms or requests changes
   - Iterates until approved

6. **Confluence Renderer**
   - Correct heading hierarchy mapping
   - Properly formatted tables
   - Bold/normal text rules
   - Link formatting
   - Copy-paste ready without adjustment

---

### Layer 3: Domain Adapter (Document Profiles)
**Purpose**: Extensibility layer for different document types

**Current Profile**: Test Plan (first validation scenario)

**Future Profiles**:
- PRD (Product Requirements Document)
- BRD (Business Requirements Document)
- Risk Assessment
- Architecture Document
- SOP (Standard Operating Procedure)
- Release Plan
- QA Strategy

**Profile Definition** (per document type):
- Section patterns (typical structure)
- Default stability suggestions
- Unit-of-work granularity rules
- Questioning strategy customization

---

## Ideal End-to-End Workflow

```
Input: Previous Test Plan v2.0 (PDF) + "Feature X v2.1 Test Plan"
↓
[1] Template Extract (Layer 1)
    → Sections: 1. Overview, 2. Test Scope, 3. Test Cases (table), etc.
    → Numbering: 1 / 1.1 / 1.1.1
    → Tables: 5 columns (ID, Description, Steps, Expected, Status)
    → Heading levels: H2 / H3 / H4
↓
[2] Section Taxonomy + Stability Classifier (Layer 2)
    → "Overview" → Type: Narrative, Stability: STABLE (inherit by default)
    → "Test Scope" → Type: Checklist, Stability: SEMI-STABLE (ask for changes)
    → "Test Cases" → Type: Table, Stability: UNSTABLE (force rewrite, row-level)
↓
[3] Controlled Build Loop (Layer 2)
    For "Overview" (STABLE):
      Claude: "Previous version: 'Testing API v2.0'. Keep or update?"
      User: "Update to v2.1"
      Claude: Writes formal paragraph → shows preview → user confirms

    For "Test Cases" (UNSTABLE, row-level):
      Claude: "Describe test case 1"
      User: "Login with valid credentials"
      Claude: Formalizes into table row → shows preview → user confirms
      (Repeat for each row)
↓
[4] Incremental Write (Layer 2)
    → SPEC.md grows section-by-section
    → User can see progress in real-time
↓
[5] Confluence Render (Layer 2)
    → Convert markdown → Confluence-ready format
    → Correct heading levels, table structure, bold/normal text
    → Output: Copy-paste ready
```

---

## Key Design Principles

### 1. Template-Driven (Not Hardcoded)
- Extract structure dynamically from previous documents
- Do not hardcode section names or numbering rules
- Schema adapts to document variations

### 2. Stability-Based Inheritance
- Parts that rarely change → inherit by default (with confirmation option)
- Parts that change every version → force rewrite
- Sections with many items (tables) → row-level iteration

### 3. Controlled Questioning
- Only ask about real gaps
- No obvious questions
- Length-limited (avoid walls of text)
- Strictly follow template constraints

### 4. Incremental Construction
- Build section-by-section
- Show progress in real-time
- User can review as we go
- Avoid "big bang" generation

### 5. Version-Aware Inheritance
- For next version of same feature:
  - Show summary of previous content
  - Ask whether changes needed
  - Preserve stable parts by default

---

## Capabilities NOT Found in Marketplace

We identified existing marketplace skills to reuse:
- ✅ `content-research-writer` → formalization
- ✅ `pdf` skill → PDF parsing
- ✅ `docx` skill → Word parsing
- ✅ `markdown-tools` → rendering

**But we must build custom**:
1. ❌ Template extraction engine (schema output)
2. ❌ Section stability classifier (dynamic, not hardcoded)
3. ❌ Controlled interview engine (AskUserQuestion orchestration)
4. ❌ Row-level review iteration (for tables)
5. ❌ Confluence renderer (heading/table/bold formatting)
6. ❌ Version inheritance logic

---

## Core Skill We Will Build

**Name**: `enterprise-doc-framework`

**Location**: `.claude/skills/enterprise-doc-framework/`

**Structure**:
```
.claude/skills/enterprise-doc-framework/
├── SKILL.md                    # Main skill entry point
├── modules/
│   ├── template-extractor.md  # Layer 1: Template Intelligence
│   ├── taxonomy.md             # Layer 2: Section classification
│   ├── interview-engine.md    # Layer 2: Controlled questioning
│   ├── writer.md               # Layer 2: Incremental writing
│   ├── renderer.md             # Layer 2: Confluence output
│   └── inheritance.md          # Layer 2: Version logic
├── profiles/
│   ├── test-plan.md            # Layer 3: Test Plan profile (first)
│   ├── prd.md                  # Layer 3: PRD profile (future)
│   └── brd.md                  # Layer 3: BRD profile (future)
└── examples/
    ├── test-plan-v1.pdf        # Sample input
    ├── test-plan-v2.md         # Sample output
    └── extracted-schema.yaml   # Sample schema
```

---

## What "Module Architecture" Means (Option A)

**Module Architecture** refers to breaking down the skill into **logical components** (modules) that each handle a specific responsibility.

### Why Modular Design?

1. **Separation of Concerns**: Each module has one job
2. **Reusability**: Modules can be reused across document profiles
3. **Maintainability**: Easy to update one part without breaking others
4. **Testability**: Each module can be validated independently
5. **Extensibility**: Add new profiles without changing core modules

### Module Breakdown

| Module | Responsibility | Inputs | Outputs |
|--------|---------------|--------|---------|
| `template-extractor.md` | Parse previous doc, extract structure | PDF/Word file | Document schema (JSON/YAML) |
| `taxonomy.md` | Classify sections by type & stability | Document schema | Section metadata (type, stability, granularity) |
| `interview-engine.md` | Orchestrate controlled questioning | Section metadata, user context | User answers (casual input) |
| `writer.md` | Formalize input, write to SPEC.md | User answers, template constraints | Formal documentation sections |
| `renderer.md` | Convert to Confluence format | SPEC.md (markdown) | Confluence-ready output |
| `inheritance.md` | Manage version-to-version logic | Previous version, schema | Inheritance decisions per section |

### How Modules Work Together

```
User Input: "Create Test Plan v2.1 based on v2.0.pdf"
↓
[template-extractor] → Parses v2.0.pdf → schema
↓
[taxonomy] → Analyzes schema → classifies sections (stable/unstable)
↓
[inheritance] → Compares with v2.0 → suggests inherit/rewrite per section
↓
[interview-engine] → Asks user about gaps/changes
↓
[writer] → Formalizes answers → writes to SPEC.md (section-by-section)
↓
[renderer] → Converts SPEC.md → Confluence format
```

---

## Current Phase: Design

**What we're doing now**:
1. ✅ Create project structure
2. ✅ Write CLAUDE.md for project memory
3. 🔄 Explain module architecture (this section)
4. 🔄 Download marketplace skills
5. ⏳ Design the skill structure (SKILL.md + modules)
6. ⏳ Validate with Test Plan scenario

---

## Success Criteria (Phase 1: Test Plan Profile)

1. ✅ Can extract structure from previous Test Plan PDF
2. ✅ Can classify sections as stable/unstable
3. ✅ Can ask controlled, gap-focused questions
4. ✅ Can build document incrementally (section-by-section)
5. ✅ Can inherit stable sections (with confirmation)
6. ✅ Can force rewrite unstable sections (row-by-row for tables)
7. ✅ Output is Confluence-ready (correct formatting)

---

## Project Milestones

### Milestone 1: Foundation Setup ✅
- Create project folder structure
- Write CLAUDE.md (project memory)
- Download marketplace skills
- Explain architecture

### Milestone 2: Skill Design (Next)
- Design SKILL.md structure
- Design module interfaces
- Design Test Plan profile
- Create example fixtures

### Milestone 3: Template Extractor
- Build PDF parsing logic
- Extract structure (sections, headings, tables)
- Output schema format (YAML/JSON)
- Test with sample Test Plan

### Milestone 4: Taxonomy + Inheritance
- Build section classifier
- Build stability analyzer
- Build inheritance logic
- Test classification accuracy

### Milestone 5: Interview Engine
- Build AskUserQuestion orchestrator
- Implement length limits
- Implement gap detection
- Test question quality

### Milestone 6: Writer + Renderer
- Build incremental writer (SPEC.md)
- Build formalization logic
- Build Confluence renderer
- Test output formatting

### Milestone 7: End-to-End Test
- Run full workflow with real Test Plan
- Validate output quality
- Collect feedback
- Refine

### Milestone 8: Extensibility (Future)
- Add PRD profile
- Add BRD profile
- Validate profile independence

---

## Environment

- Project root: `D:\_0026W\claudecode\`
- This project: `D:\_0026W\claudecode\enterprise-doc-framework\`
- Skills location: `D:\_0026W\claudecode\.claude\skills\`
- Node.js: v22.12.0
- Platform: Windows 11
- Model: Claude Sonnet 4.5

---

## Next Steps

1. Download marketplace skills (content-research-writer, pdf, docx, markdown-tools)
2. User will run `/clear` to reset context
3. Design the skill structure (SKILL.md + modules)
4. Build Phase 1: Template Extractor + Test Plan profile

---

## Strategic Positioning

We are NOT building a prompt tool.

We ARE building:
- An **Enterprise Structured Document Generation Framework**
- A **team-level reusable system**
- A **cognitive load reducer for PMs/BAs**

Future use cases:
- Test Plan (current)
- PRD
- BRD
- Architecture Spec
- Risk Assessment
- QA Strategy
- Release Plan
- SOP

---

**Last Updated**: 2026-02-13
**Status**: Milestone 1 Complete → Moving to Milestone 2 (Skill Design)
