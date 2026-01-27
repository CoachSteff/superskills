---
name: publisher
description: Format polished content and prepare final deliverables for distribution. Use when creating platform-specific versions, formatting for publication, or preparing multi-format content packages.
version: 1.0.0
---

# Publisher

> **Note**: Review [PROFILE.md](PROFILE.md) in this skill folder for user-specific brand standards, platform requirements, and file management preferences.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Format edited content and prepare deliverables for final delivery.

## Workflow

### 1. Review Content
- Read edited content completely
- Note target platform(s) or format(s)
- Review special formatting requirements
- Check if multiple versions needed
- Understand end-use context

### 2. Choose Format Strategy
- Single format: One deliverable
- Multiple versions: Platform-specific adaptations
- Document creation: DOCX, PPTX, PDF
- Web-ready: HTML or markdown

### 3. Format the Content
- Apply platform-specific formatting
- Optimize for readability
- Add visual hierarchy
- Include metadata
- Ensure accessibility

### 4. Create Deliverables
- Generate all requested formats
- Name files clearly: `[project]-[type]-[date].[ext]`
- Include usage guide if needed
- Add supporting materials

### 5. Move to Outputs
- **CRITICAL:** Copy all files to `~/Documents/Outputs` (or your configured output directory via $OUTPUT_DIR)
- Verify files accessible
- Prepare `file://` links

### 6. Document
- List deliverables with descriptions
- Note platform considerations
- Include usage recommendations
- Provide file locations

## Output Format

```markdown
# Publication Package: [Project]
**Published by:** Publisher
**Date:** [Date]
**Source:** [Edited file]
**Status:** Ready

---

## Deliverables Created

### 1. [Deliverable Name]
- **File:** `[filename.ext]`
- **Location:** `~/Documents/Outputs/[filename]`
- **Format:** [Description]
- **Purpose:** [How to use]
- **Notes:** [Platform details]

### 2. [Additional deliverables]
[Continue pattern]

---

## Usage Recommendations

**For [Platform]:**
[Specific posting tips]

---

## Quality Checks
- ✅ All files in outputs directory
- ✅ File naming follows conventions
- ✅ Formatting appropriate
- ✅ Content renders correctly
- ✅ Links intact
- ✅ Metadata included

---
**Handoff to:** Manager
**File:** `workspace/publication-[project]-[date].md`
```

## Platform Specifications

**LinkedIn:**
- Feed: 1200x627px
- Square: 1200x1200px
- Professional, minimal text
- Mobile-readable

**Blog (Markdown):**
- Proper H1, H2, H3 hierarchy
- 3-5 sentence paragraphs
- SEO-friendly headers
- Blockquotes for insights

**Workshop Materials:**
- Clear visual hierarchy
- Adequate white space
- Timing markers
- Print-friendly

## Quality Checks

- All files in `~/Documents/Outputs` (or your configured output directory)?
- File names make sense?
- Formatting clean and professional?
- Content renders correctly?
- Usage guidance included?
- Ready to use immediately?
