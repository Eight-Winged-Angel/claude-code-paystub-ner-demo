# Enterprise Structured Document Generation Framework

> A team-level reusable framework to reduce PM/BA cognitive load when writing structured enterprise documents

---

## 🎯 What This Is

An **Enterprise Structured Document Generation Framework** that:
- Extracts templates from previous documents (not hardcoded)
- Uses stability-based inheritance (smart defaults)
- Asks controlled, gap-focused questions (no unnecessary prompts)
- Builds documents incrementally (section-by-section)
- Outputs Confluence-ready content (copy-paste ready)

**This is NOT**: A one-off Test Plan writer, PRD generator, or single-use prompt tool

---

## 🏗️ Three-Layer Architecture

### Layer 1: Template Intelligence
Extracts structure, formatting, and content shape from previous documents

### Layer 2: Construction Engine (Core Skill)
Orchestrates the entire generation process:
- Section taxonomy & stability classification
- Inheritance logic
- Controlled interview engine
- Incremental writer
- Formalization & review loops
- Confluence renderer

### Layer 3: Domain Adapter
Document-specific profiles:
- **Test Plan** (Phase 1)
- PRD, BRD, Architecture Doc, Risk Assessment (Future)

---

## 📂 Project Structure

```
enterprise-doc-framework/
├── CLAUDE.md          # Full project memory (read this after /clear)
├── PROGRESS.md        # Milestone tracker
└── README.md          # This file

.claude/skills/
├── pdf/               # Parse PDF files
├── docx/              # Create Word documents
├── markdown-tools/    # Convert to markdown
├── skill-creator/     # Skill development guide
└── content-research-writer/  # Formalize casual → professional (customized for PM/BA)
```

---

## ✅ Milestone 1: Foundation Setup (COMPLETE)

**Completed**:
1. ✅ Project structure created
2. ✅ Explained module architecture
3. ✅ Downloaded 5 marketplace skills
4. ✅ Customized content-research-writer for PM/BA use

**Date**: 2026-02-13

---

## ⏳ Next: Milestone 2 - Skill Design

After `/clear`, proceed with:
1. Read `CLAUDE.md` to restore full context
2. Design the `enterprise-doc-framework` skill structure
3. Design module interfaces
4. Create Test Plan profile

---

## 📊 Module Architecture

| Module | Purpose |
|--------|---------|
| `template-extractor` | Parse docs → extract schema |
| `taxonomy` | Classify sections (type + stability) |
| `interview-engine` | Controlled questioning |
| `writer` | Formalize + write incrementally |
| `renderer` | Confluence-ready output |
| `inheritance` | Version-to-version logic |

---

## 🔑 Key Principles

1. **Template-Driven**: Extract structure dynamically, not hardcoded
2. **Stability-Based**: Stable sections inherit, unstable rewrite
3. **Controlled**: Only ask about real gaps, length-limited
4. **Incremental**: Build section-by-section
5. **Version-Aware**: Smart inheritance from previous versions

---

## 📚 Documentation

- **CLAUDE.md**: Full project memory, architecture, workflow
- **PROGRESS.md**: Milestone tracker with detailed status
- **README.md**: This quick reference

---

## 🚀 Future Vision

Extend to multiple document types:
- Test Plans (Phase 1)
- PRDs
- BRDs
- Architecture Specs
- Risk Assessments
- QA Strategies
- Release Plans
- SOPs

---

**Last Updated**: 2026-02-13
**Status**: Milestone 1 Complete → Ready for Milestone 2
