---
name: audiobook
description: Convert documents (PDF, Text, Markdown, Docx) into high-quality narrated audiobooks with automatic chapter detection. Generates one MP3 file per chapter with metadata.
version: 1.0.0
---

# Audiobook

> **Note**: Review [PROFILE.md](PROFILE.md) in this skill folder for user-specific narration preferences, voice settings, and chapter handling guidelines.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Convert documents into professional audiobooks with automatic chapter detection, generating high-quality narrated MP3 files optimized for long-form listening.

## Supported Formats

- **PDF** (.pdf) - Text extraction from PDF documents
- **Plain Text** (.txt) - Plain text files
- **Markdown** (.md, .markdown) - Markdown documents
- **Word Documents** (.docx) - Microsoft Word files

## Tools

**DocumentParser.py** (in src/):
- Multi-format document text extraction
- UTF-8 and fallback encoding support
- PDF, Docx, Markdown, and plain text parsing
- Validation and error handling

**ChapterDetector.py** (in src/):
- Automatic chapter boundary detection
- Multiple detection strategies (markdown, numbered, pagebreak, custom)
- Smart fallback for documents without clear chapters
- Chapter splitting for oversized content
- Configurable custom regex patterns

**AudiobookConfig.py** (in src/):
- Voice profile configuration management
- Singleton pattern for efficient config loading
- Validation of voice settings
- Environment variable fallback support

**AudiobookGenerator.py** (in src/):
- Complete audiobook generation orchestration
- Chapter-by-chapter audio generation
- ElevenLabs API integration with model fallback
- Metadata JSON generation
- Progress tracking and logging

## Core Workflow

### 1. Document Parsing
- Load document from supported format (PDF, TXT, MD, DOCX)
- Extract full text content
- Handle encoding and format-specific quirks
- Validate text extraction success

### 2. Chapter Detection
- Analyze text structure using selected strategy
- Detect chapter boundaries automatically
- Extract chapter titles and content
- Handle edge cases (no chapters, oversized chapters)

### 3. Audio Generation
- Optimize text for natural speech delivery
- Generate audio for each chapter using ElevenLabs
- Apply audiobook-specific voice settings
- Calculate duration and WPM metadata
- Save individual chapter MP3 files

### 4. Metadata Export
- Create comprehensive metadata JSON
- Include chapter titles, durations, word counts
- Track generation timestamp and settings
- Provide formatted duration strings

## Chapter Detection Strategies

**auto** (default):
- Try detection strategies in priority order
- Prefer markdown headings → numbered patterns → page breaks
- Fallback to single chapter or size-based splitting

**markdown**:
- Detect chapters from `#` or `##` headings
- Best for markdown-formatted documents
- Preserves heading text as chapter titles

**numbered**:
- Detect "Chapter 1", "CHAPTER 1", "1. Title" patterns
- Case-insensitive matching
- Extracts chapter titles when present

**pagebreak**:
- Split on form feed (`\f`) or triple-dash (`---`) dividers
- Attempts to extract titles from first lines
- Falls back to "Section N" titles

**custom**:
- Use custom regex patterns from config or env var
- Flexible for non-standard document structures
- Pattern errors logged but don't crash generation

## Chapter Announcements

Every chapter audio file begins with a spoken announcement that includes:

**For regular chapters:**
- Book title (extracted from filename)
- Chapter number
- Chapter title (if available)

**For special sections (Prologue, Epilogue, Foreword, etc.):**
- Book title
- Section name and subtitle (if available)

**Example announcements:**
- Regular: *"The Great Novel. Chapter 1. The Beginning."*
- Special: *"The Great Novel. Prologue: The Dark Past."*

This feature ensures listeners always know where they are in the audiobook, especially useful when:
- Resuming playback after a break
- Navigating between chapter files
- Listening to audiobooks split across multiple sessions

**Implementation:** The announcement is prepended to the chapter text before sending to the text-to-speech API, creating a natural pause between the announcement and the chapter content.

## Prologue and Epilogue Support

The skill automatically detects and processes special book sections alongside regular chapters:

**Supported special sections:**
- **Prologue** / **PROLOGUE**: Story introduction or background
- **Epilogue** / **EPILOGUE**: Story conclusion or aftermath
- **Foreword** / **FOREWORD**: Author or expert introduction
- **Afterword** / **AFTERWORD**: Author reflections or commentary
- **Preface** / **PREFACE**: Book context or purpose

**Detection patterns:**
- Sections must appear on their own line (heading style)
- Case-insensitive matching (e.g., "Prologue", "PROLOGUE", "prologue")
- Optional subtitle after colon: `Prologue: The Dark Past`
- Properly ordered in output: Prologue → Chapters → Epilogue

**Example document structure:**
```
Prologue: The Dark Past

[Prologue content...]

Chapter 1: The Beginning

[Chapter 1 content...]

Epilogue: What Happened Next

[Epilogue content...]
```

This generates 3 MP3 files:
- `001_prologue_the_dark_past.mp3`
- `002_chapter_1_the_beginning.mp3`
- `003_epilogue_what_happened_next.mp3`

## Text Cleaning

The audiobook skill automatically cleans extracted PDF text to improve narration quality:

### What Gets Removed

- **Page numbers**: "42", "Page 42", "42 | Chapter Title", "Chapter Title | 42", "42 of 200"
- **Headers/footers**: Repeated chapter titles, copyright notices (©), date stamps, "All rights reserved"
- **Hyphenated words**: Word breaks at line endings are rejoined ("exam-\nple" → "example")
- **Excessive whitespace**: Multiple blank lines reduced to maximum 2, multiple spaces to 1
- **Duplicate lines**: Repeated headers or OCR errors removed

### Configuration

Text cleaning is enabled by default for PDF files. To disable:

**Python API:**
```python
generator = AudiobookGenerator(clean_text=False)
```

**Custom Patterns:**

```python
from superskills.audiobook.src.TextCleaner import TextCleaner

cleaner = TextCleaner(
    remove_page_numbers=True,
    remove_headers_footers=True,
    custom_patterns=[
        r'^Confidential$',      # Remove "Confidential" headers
        r'^\d{4}-\d{2}-\d{2}'  # Remove date stamps
    ]
)

cleaned_text = cleaner.clean(raw_text)
```

**Why Text Cleaning Matters:**

- **Natural flow**: Narrator shouldn't read "Page 42" between paragraphs
- **Professional quality**: Copyright notices and headers disrupt listening experience
- **Correct pronunciation**: Rejoined hyphenated words prevent awkward pauses
- **Better chapter detection**: Cleaned text produces more accurate chapter boundaries

## Quality Checklist

- [ ] Document format supported and parsed successfully
- [ ] Chapters detected accurately (verify count and titles)
- [ ] Audio quality high (no artifacts or pronunciation issues)
- [ ] Chapter MP3 files generated with correct naming
- [ ] Metadata JSON complete and accurate
- [ ] Total duration and word counts match expectations
- [ ] Voice settings appropriate for long-form narration
- [ ] No page numbers or headers in generated audio (listen to sample)

## Usage

### Python API

**Basic Usage:**
```python
from superskills.audiobook.src import AudiobookGenerator

generator = AudiobookGenerator(output_dir="audiobooks")
result = generator.generate_audiobook("my_book.pdf", output_prefix="my_book")

print(f"Generated {result.total_chapters} chapters")
print(f"Total duration: {result.total_duration_seconds / 3600:.1f} hours")
print(f"Metadata: {result.metadata_file}")
```

**With Custom Settings:**
```python
generator = AudiobookGenerator(
    output_dir="audiobooks",
    profile_type="audiobook",
    chapter_strategy="markdown",
    custom_chapter_patterns=[r"^PART \d+:"]
)

result = generator.generate_audiobook(
    file_path="novel.docx",
    output_prefix="my_novel"
)

for chapter_file in result.chapter_files:
    print(f"Generated: {chapter_file}")
```

**Access Individual Components:**
```python
from superskills.audiobook.src import DocumentParser, ChapterDetector

# Parse document
parser = DocumentParser()
text = parser.parse_file("book.pdf")

# Detect chapters
detector = ChapterDetector()
chapters = detector.detect_chapters(text, strategy="auto")

for chapter in chapters:
    print(f"Chapter {chapter.number}: {chapter.title} ({chapter.word_count} words)")
```

### CLI Usage

**Basic Generation:**
```bash
superskills call audiobook --input book.pdf
```

**With Custom Prefix:**
```bash
superskills call audiobook --input novel.docx --output-prefix "my_novel"
```

**With Chapter Strategy:**
```bash
superskills call audiobook --input memoir.txt --chapter-strategy markdown
```

**Process Specific Chapters:**
```bash
# Process only first chapter (for testing)
superskills call audiobook --input book.pdf --chapter-range 1

# Process chapters 1-3
superskills call audiobook --input book.pdf --chapter-range 1-3

# Process chapters 5-10
superskills call audiobook --input book.pdf --chapter-range 5-10
```

**Use cases for chapter-range:**
- **Testing**: Quickly test voice/settings on first chapter before full conversion
- **Partial conversion**: Generate only specific sections of interest
- **Resource management**: Process large books in batches to manage costs/time
- **Corrections**: Re-generate specific chapters after source edits

**Notes:**
- Chapter numbers are 1-indexed (first chapter is 1, not 0)
- Range is inclusive: `1-3` processes chapters 1, 2, and 3
- If end chapter exceeds total chapters, processes up to last available chapter
- If start chapter exceeds total chapters, raises an error

**Custom Voice Profile:**
```bash
superskills call audiobook --input textbook.pdf --voice-profile narration
```

## Configuration

### Voice Profiles (voice_profiles.json)

Create `voice_profiles.json` from template:
```bash
cp voice_profiles.json.template voice_profiles.json
```

Edit with your ElevenLabs voice settings:
```json
{
  "audiobook": {
    "voice_id": "your_voice_id_here",
    "voice_name": "Your Audiobook Voice",
    "language": "English",
    "model": "eleven_turbo_v2_5",
    "speed": 0.95,
    "stability": 0.65,
    "similarity_boost": 0.85,
    "style": 0.20
  }
}
```

### Environment Variables (.env)

```bash
# Required
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Optional
AUDIOBOOK_CHAPTER_STRATEGY=auto
AUDIOBOOK_CUSTOM_CHAPTER_PATTERN=^Chapter \d+:
```

### Voice Settings Explained

**speed** (0.7-1.2): Narration speed
- 0.95 recommended for audiobooks (slightly slower for comprehension)

**stability** (0.0-1.0): Voice consistency
- 0.65 recommended (balanced between consistent and natural)

**similarity_boost** (0.0-1.0): Voice similarity to original
- 0.85 recommended (natural but clear)

**style** (0.0-1.0): Expressiveness variation
- 0.20 recommended (minimal variation for long-form)

## Output

### Chapter Files
- **Naming**: `{prefix}_chapter_{number:02d}_{title}.mp3`
- **Example**: `my_book_chapter_01_introduction.mp3`
- **Format**: MP3 with 320kbps quality
- **One file per chapter**

### Metadata File
- **Naming**: `{prefix}_metadata.json`
- **Example**: `my_book_metadata.json`

**Structure:**
```json
{
  "title": "my_book",
  "source_file": "my_book.pdf",
  "total_chapters": 15,
  "total_duration_seconds": 32400.5,
  "total_duration_formatted": "9h 0m 0s",
  "total_word_count": 85000,
  "average_wpm": 157,
  "generated_at": "2026-01-09T14:30:00",
  "profile_type": "audiobook",
  "voice_name": "Your Voice",
  "chapters": [
    {
      "number": 1,
      "title": "Introduction",
      "file": "my_book_chapter_01_introduction.mp3",
      "duration_seconds": 420.5,
      "duration_formatted": "7m 0s",
      "word_count": 1100,
      "wpm": 157
    }
  ]
}
```

## Avoid

- **Poor Chapter Detection**: Manual chapter review → Verify chapter strategy matches document structure
- **Wrong Voice Settings**: Generic settings → Use audiobook-optimized profile (slower speed, balanced stability)
- **Large Files Without Splitting**: Processing entire book at once → Auto-splits oversized chapters for manageable API calls
- **Missing Metadata**: Generate audio only → Always create metadata JSON for tracking and organization
- **Ignoring Format Issues**: Assume parsing worked → Validate text extraction and chapter detection before generating audio

## Escalate When

- Document exceeds 200,000 words (cost and time concerns)
- PDF extraction quality poor (scanned images, complex layouts)
- Chapter detection completely fails (needs manual chapter markers)
- API rate limits hit during generation (needs throttling or batch processing)
- Voice compatibility issues persist across all model fallbacks
- Custom chapter patterns needed but unclear from document structure
- Multi-language content requires different voice profiles per section

## Integration Examples

**With Author Skill (Script → Audiobook):**
```python
from superskills.author.src import Author
from superskills.audiobook.src import AudiobookGenerator

# Generate book content
author = Author()
book_content = author.write_long_form("Write a short story about...")

# Save to file
with open("story.txt", "w") as f:
    f.write(book_content)

# Convert to audiobook
generator = AudiobookGenerator()
result = generator.generate_audiobook("story.txt", "my_story")
```

**With Publisher (Audiobook Distribution):**
```python
from superskills.audiobook.src import AudiobookGenerator
from superskills.publisher.src import Publisher

# Generate audiobook
generator = AudiobookGenerator()
result = generator.generate_audiobook("book.pdf", "audiobook")

# Publish chapter files
publisher = Publisher()
for chapter_file in result.chapter_files:
    publisher.upload_to_platform(chapter_file, platform="podcast")
```

## Technical Notes

- **API Costs**: ElevenLabs charges per character. 100,000 words ≈ 500,000 characters.
- **Generation Time**: ~1 minute per 5,000 words (varies by API load)
- **Model Fallback**: Automatically tries turbo → monolingual → flash if voice incompatible
- **Memory Usage**: Processes chapters sequentially to avoid memory issues
- **File Limits**: PDF parsing limited by PyPDF2 capabilities (text-based PDFs only)
