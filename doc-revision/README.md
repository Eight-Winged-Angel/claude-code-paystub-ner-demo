# doc-revision Skill

> **Template Intelligence Engine** - Generate enterprise documents by learning from previous versions

**Version**: 0.3
**Status**: Ready for Testing

---

## 🎯 What This Is

The **doc-revision** skill generates updated document versions by dynamically learning template structure from previous versions (PDF/Word/Markdown).

**Key Capabilities**:
- Extracts templates from previous documents (not hardcoded)
- Uses stability-based inheritance (smart defaults)
- Asks controlled, gap-focused questions (3-5 per turn)
- Builds documents incrementally (section-by-section)
- Outputs Confluence-ready content (copy-paste ready)
- Never asks about metadata (status, approvers, version, dates)

**This is NOT**: A template loader or one-time document generator

---

## 🏗️ Five-Phase Workflow

### Phase 1: Template Extraction
Parse structure, formatting, and section shapes from uploaded document

### Phase 2: Stability Classification
Classify sections as Stable/Evolving/Volatile

### Phase 3: Controlled Build Plan
Present plan, get user confirmation before proceeding

### Phase 4: Section-by-Section Construction
Incremental building with targeted interviews (3-5 questions per turn)

### Phase 5: Confluence Renderer
Copy-paste ready output with proper formatting

---

## 📂 Project Structure

```
doc-revision/
├── CLAUDE.md          # Full project memory (read this after /clear)
├── README.md          # This file
└── skills/            # Supporting skills library
    ├── doc-revision/  # Main skill (source of truth)
    │   └── SKILL.md
    ├── content-research-writer/
    ├── docx/
    ├── pdf/
    ├── markdown-tools/
    └── skill-creator/

.claude/skills/        # Claude Code registration directory
└── doc-revision/      # Synced from doc-revision/skills/doc-revision/
    └── SKILL.md
```

---

## 🎯 When to Use doc-revision

**Use this skill when:**
- User has a previous document version (PDF/Word/Markdown)
- User wants to create an updated version
- User provides trigger like "Feature X test plan 2.1" or "Write next version of this document"

**Example triggers:**
- "Feature X test plan 2.1"
- "Write next version of this document"
- "Update this enterprise document based on previous PDF"

---

## 🆚 doc-revision vs doc-expert

| Aspect | doc-revision | doc-expert |
|--------|--------------|-----------|
| **User Knowledge** | Has previous version | Doesn't know how to write |
| **Input** | Previous document (PDF/Word) | Minimal info (5 questions) |
| **Approach** | Template-driven update | Expert-driven generation |
| **Questions** | 3-5 questions per turn | 5 questions max per turn |
| **Metadata** | Inherits/auto-increments | Auto-fills all metadata |
| **Output** | Updated version | Draft from scratch |

---

## 🔑 Core Modules

| Module | Purpose |
|--------|---------|
| `template-extractor` | Parse docs → extract schema |
| `stability-classifier` | Classify sections (Stable/Evolving/Volatile) |
| `interview-engine` | Controlled questioning (3-5 per turn) |
| `incremental-writer` | Section-by-section construction |
| `confluence-renderer` | Confluence-ready output |
| `inheritance-logic` | Version-to-version defaults |

---

## 🔑 Key Principles

1. **Template-Driven**: Dynamically learns templates from previous versions (not hardcoded)
2. **Stability-Based**: Stable sections inherit by default, unstable sections force rewrite
3. **Controlled Interviews**: 3-5 focused questions per turn, no metadata questions
4. **Incremental Construction**: Build section-by-section, never auto-generate entire document
5. **Table Atomicity**: Table sections handled row-by-row (smallest unit of work)
6. **Metadata Inheritance**: Automatically inherit/increment version, status, dates
7. **Confluence-Ready**: Proper heading levels, table formatting, copy-paste ready

---

## 🚀 Workflow Example

```
Input: Previous Test Plan v2.0 (PDF) + "Feature X v2.1 Test Plan"
↓
[Phase 1] Template Extraction
→ Sections: 1. Overview, 2. Test Scope, 3. Test Cases (table)
→ Heading levels: H2 / H3 / H4
→ Table structure: 5 columns (ID, Description, Steps, Expected, Status)
↓
[Phase 2] Stability Classification
→ "Overview" → STABLE (inherit by default)
→ "Test Scope" → EVOLVING (ask for changes)
→ "Test Cases" → VOLATILE (force rewrite, row-by-row)
↓
[Phase 3] Build Plan
→ Present plan, get user confirmation
↓
[Phase 4] Section-by-Section Construction
→ For stable sections: Show previous, ask if changes needed
→ For volatile sections: Ask 3-5 questions, formalize, show preview
→ For tables: Row-by-row iteration
↓
[Phase 5] Confluence Renderer
→ Convert to Confluence format, copy-paste ready
```

---

## 📚 Documentation

- **CLAUDE.md**: Full project memory, architecture, detailed workflow
- **README.md**: This quick reference
- **skills/doc-revision/SKILL.md**: Main skill implementation

---

## 🎓 Document Type Profiles

Current support:
- ✅ **Test Plans** (primary use case)
- ⏳ PRDs (future)
- ⏳ BRDs (future)
- ⏳ Architecture Specs (future)
- ⏳ Risk Assessments (future)

---

## 🧪 Testing Instructions

1. Provide a previous version document (PDF/Word/Markdown)
2. Use trigger prompt: `"Feature X test plan 2.1"` or `"Write next version of this document"`
3. Skill should activate and follow 5-phase workflow
4. Verify no metadata questions (status, approvers, etc.)
5. Verify controlled interviews (3-5 questions per turn)

---

**Last Updated**: 2026-02-14
**Status**: v0.3 - Ready for Testing
**Location**: `.claude/skills/doc-revision/SKILL.md`
