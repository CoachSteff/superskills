# Audiobook Skill

Convert documents into professional narrated audiobooks with automatic chapter detection.

## Features

- **Multi-format Support**: PDF, TXT, Markdown, DOCX
- **Automatic Chapter Detection**: Markdown headings, numbered patterns, page breaks, custom regex
- **Smart Text Cleaning**: Automatically removes page numbers, headers, footers, and fixes hyphenation for natural narration
- **Multi-Provider TTS**: Gemini (default, 100k char limit), ElevenLabs, OpenAI (coming soon)
- **High-Quality Narration**: Google Gemini or ElevenLabs voice generation optimized for long-form content
- **Chapter-by-Chapter Output**: One MP3 file per chapter with sequential naming
- **Comprehensive Metadata**: JSON file with titles, durations, word counts, WPM
- **Smart Fallbacks**: Handles documents without clear chapters, splits oversized content

## Installation

### Dependencies

Install required Python packages:

```bash
pip install PyPDF2 python-docx google-genai pydub
# Optional for ElevenLabs: pip install elevenlabs
```

### Configuration

1. **Copy Templates:**
   ```bash
   cd superskills/audiobook
   cp voice_profiles.json.template voice_profiles.json
   cp PROFILE.md.template PROFILE.md
   ```

2. **Set API Key (Gemini - Default):**
   ```bash
   export GEMINI_API_KEY=your_gemini_api_key_here
   ```
   
   Or for ElevenLabs:
   ```bash
   export ELEVENLABS_API_KEY=your_api_key_here
   ```

3. **Edit Voice Profile (Optional):**
   
   The default `voice_profiles.json` uses Gemini with the "Puck" voice:
   ```json
   {
     "audiobook": {
       "provider": "gemini",
       "voice_id": "Puck",
       "voice_name": "Puck (Upbeat)",
       "language": "English",
       "model": "gemini-2.5-flash-preview-tts",
       "speed": 1.0
     }
   }
   ```
   
   To use ElevenLabs instead, edit `voice_profiles.json`:
   ```json
   {
     "audiobook": {
       "provider": "elevenlabs",
       "voice_id": "your_voice_id_here",
       "voice_name": "Your Voice Name",
       "language": "English",
       "model": "eleven_turbo_v2_5",
       "speed": 0.95,
       "stability": 0.65,
       "similarity_boost": 0.85,
       "style": 0.20
     }
   }
   ```

## Quick Start

### Python API

```python
from superskills.audiobook.src import AudiobookGenerator

# Initialize generator
generator = AudiobookGenerator(output_dir="audiobooks")

# Generate audiobook
result = generator.generate_audiobook("my_book.pdf", output_prefix="my_book")

# View results
print(f"Generated {result.total_chapters} chapters")
print(f"Duration: {result.total_duration_seconds / 3600:.1f} hours")
print(f"Files: {result.chapter_files}")
```

### CLI

```bash
# Basic usage (uses Gemini by default)
superskills call audiobook --input book.pdf

# With custom settings
superskills call audiobook \
  --input novel.docx \
  --output-prefix "my_novel" \
  --chapter-strategy markdown

# Process specific chapters
superskills call audiobook --input book.pdf --chapter-range 1      # First chapter only
superskills call audiobook --input book.pdf --chapter-range 1-5    # Chapters 1-5

# Use different TTS providers
superskills call audiobook --input book.pdf --tts-provider gemini --tts-voice Puck
superskills call audiobook --input book.pdf --tts-provider elevenlabs --tts-voice your_voice_id
```

## Usage Examples

### Example 1: Generate Audiobook from PDF

```python
from superskills.audiobook.src import AudiobookGenerator

generator = AudiobookGenerator(output_dir="output/audiobooks")
result = generator.generate_audiobook(
    file_path="documents/my_book.pdf",
    output_prefix="my_book"
)

print(f"✓ Generated {result.total_chapters} chapters")
print(f"✓ Total duration: {result.total_duration_seconds / 3600:.2f} hours")
print(f"✓ Metadata saved: {result.metadata_file}")
```

### Example 2: Custom Chapter Detection

```python
from superskills.audiobook.src import AudiobookGenerator

# Use custom regex pattern for chapters
generator = AudiobookGenerator(
    output_dir="audiobooks",
    chapter_strategy="custom",
    custom_chapter_patterns=[r"^PART \d+:", r"^Section [A-Z]:"]
)

result = generator.generate_audiobook("custom_format.txt")
```

### Example 3: Parse and Inspect Before Generating

```python
from superskills.audiobook.src import DocumentParser, ChapterDetector

# Parse document
parser = DocumentParser()
text = parser.parse_file("book.pdf")
print(f"Extracted {len(text)} characters")

# Detect chapters
detector = ChapterDetector()
chapters = detector.detect_chapters(text, strategy="auto")

# Review chapters before generating audio
for ch in chapters:
    print(f"Chapter {ch.number}: {ch.title} ({ch.word_count} words)")

# Proceed with generation if satisfied
from superskills.audiobook.src import AudiobookGenerator
generator = AudiobookGenerator()
result = generator.generate_audiobook("book.pdf")
```

## Chapter Detection Strategies

### Auto (Default)
Tries strategies in order until chapters found:
1. Markdown headings
2. Numbered patterns
3. Page breaks
4. Fallback to single chapter or size-based split

### Markdown
Best for `.md` files or documents with heading structure:
- Detects `#` and `##` headings
- Uses heading text as chapter titles

### Numbered
Matches patterns like:
- "Chapter 1", "Chapter 1: Title"
- "CHAPTER 1", "CHAPTER ONE"
- "1. Title", "Part 1"

### Page Break
Splits on:
- Form feed characters (`\f`)
- Triple-dash dividers (`---`)

### Custom
Provide your own regex patterns:
```python
generator = AudiobookGenerator(
    chapter_strategy="custom",
    custom_chapter_patterns=[r"^BOOK \d+$", r"^\d+\. [A-Z]"]
)
```

## Output Structure

```
audiobooks/
├── my_book_chapter_01_introduction.mp3
├── my_book_chapter_02_the_beginning.mp3
├── my_book_chapter_03_rising_action.mp3
├── ...
└── my_book_metadata.json
```

### Metadata JSON

```json
{
  "title": "my_book",
  "source_file": "my_book.pdf",
  "total_chapters": 15,
  "total_duration_seconds": 28800,
  "total_duration_formatted": "8h 0m 0s",
  "total_word_count": 75000,
  "average_wpm": 156,
  "generated_at": "2026-01-09T14:30:00",
  "chapters": [
    {
      "number": 1,
      "title": "Introduction",
      "file": "my_book_chapter_01_introduction.mp3",
      "duration_seconds": 360,
      "duration_formatted": "6m 0s",
      "word_count": 940,
      "wpm": 157
    }
  ]
}
```

## Voice Settings

Audiobook-optimized defaults:
- **Speed**: 0.95 (slightly slower for comprehension)
- **Stability**: 0.65 (balanced consistency)
- **Similarity Boost**: 0.85 (natural voice)
- **Style**: 0.20 (minimal variation)

Customize in `voice_profiles.json` for different narration styles.

## Troubleshooting

### PDF Parsing Issues
- **Problem**: No text extracted from PDF
- **Solution**: PDF may be scanned image. Use OCR or text-based PDF

### Chapter Detection Fails
- **Problem**: All content in single chapter
- **Solution**: Try different detection strategy or use custom patterns

### API Errors
- **Problem**: "Voice not fine-tuned for model"
- **Solution**: Generator automatically tries model fallback (turbo → monolingual → flash)

### Token Limit Errors (Gemini)
- **Problem**: `400 INVALID_ARGUMENT: input token count exceeds maximum (8,192)`
- **Root Cause**: Gemini has an 8,192 token input limit (~32,000 characters or ~5,000-6,000 words)
- **Automatic Handling**: Chapters exceeding limits are automatically split into parts (a, b, c, etc.)
  - Output files: `book_chapter_01a.mp3`, `book_chapter_01b.mp3`, etc.
  - Each part includes a brief continuation announcement
- **Manual Prevention**: 
  - Use `--chapter-strategy page_break` for smaller chapters
  - Adjust `MAX_CHAPTER_WORDS` in `ChapterDetector.py` if needed

### Large Documents
- **Problem**: Document too large, high API costs
- **Solution**: Generator auto-splits chapters >5,000 words. For very large books, consider processing in batches.

## Best Practices

1. **Review Chapter Detection**: Always inspect detected chapters before generating audio
2. **Use Appropriate Strategy**: Match detection strategy to document format
3. **Monitor API Costs**: 100,000 words ≈ $15-30 (varies by model and voice)
4. **Keep Source Files**: Save original documents alongside audiobooks for reference
5. **Version Metadata**: Commit metadata JSON to track audiobook versions

## API Reference

See [SKILL.md](SKILL.md) for complete API documentation and integration examples.

## Support

For issues or feature requests, see [CONTRIBUTING.md](../../CONTRIBUTING.md).
