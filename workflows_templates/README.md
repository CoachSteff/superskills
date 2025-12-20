# Workflow Templates

This directory contains example workflow templates for SuperSkills. These are starter templates that you can copy and customize for your own use.

## Quick Start

**First-time setup:**

```bash
# Copy templates to create your personal workflows directory
cp -r workflows_templates workflows

# Or copy individual workflows
cp -r workflows_templates/podcast-generation workflows/
```

The `workflows/` directory is gitignored, so your personal workflows and data remain private.

## Available Templates

### 1. Podcast Generation
**Location:** `podcast-generation/`  
**Purpose:** Generate professional podcast audio from markdown scripts  
**Skills Used:** copywriter → narrator-podcast  
**Input:** Markdown script files  
**Output:** Enhanced script + MP3 audio

**Use case:** Transform written content into engaging podcast episodes with optimized narration.

### 2. Content Creation
**Location:** `content-creation/`  
**Purpose:** End-to-end content production from research to publication  
**Skills Used:** researcher → strategist → author → editor  
**Input:** Topic or research query  
**Output:** Publication-ready content

**Use case:** Automated content pipeline for blog posts, articles, or social media.

### 3. Training Material Development
**Location:** `training-material/`  
**Purpose:** Convert recordings into structured training content  
**Skills Used:** transcriber → author → editor  
**Input:** Audio/video training session recordings  
**Output:** Formatted training documentation

**Use case:** Turn training sessions, webinars, or workshops into reusable documentation.

## Usage

After copying templates to `workflows/`:

```bash
# List available workflows
superskills workflow list

# Run a workflow in watch mode (auto-process new files)
superskills run podcast-generation --watch

# Process all files in input directory
superskills run podcast-generation --batch

# Process single file
superskills run podcast-generation --input your-file.md

# Dry-run to preview (no API calls)
superskills run content-creation --dry-run
```

## Customization

Each workflow includes:
- `workflow.yaml` - Workflow configuration
- `README.md` - Specific usage instructions
- `input/` - Place your input files here
- `output/` - Processed results appear here

Edit `workflow.yaml` to customize:
- Skill parameters
- Variable mappings
- Input/output paths
- Processing steps

## Creating New Workflows

Use these templates as starting points:

1. Copy an existing template
2. Modify `workflow.yaml` with your skills and steps
3. Update `README.md` with your workflow description
4. Test with `--dry-run` first

See [CLI Setup Guide](../dev/CLI_SETUP.md) for detailed workflow syntax.

## Directory Structure

```
workflows_templates/          # Templates (committed to git)
├── README.md                 # This file
├── podcast-generation/       # Example workflow
│   ├── workflow.yaml
│   ├── README.md
│   ├── input/
│   └── output/
└── content-creation/         # Example workflow
    └── ...

workflows/                    # Your personal workflows (gitignored)
├── podcast-generation/       # Copied from template
├── my-custom-workflow/       # Your custom workflow
└── ...
```

## Notes

- Templates are read-only examples (committed to git)
- Your workflows in `workflows/` are private (gitignored)
- Input files and API keys remain local
- Output files are also gitignored for privacy
- Always test with `--dry-run` to estimate costs
