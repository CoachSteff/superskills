---
name: videoeditor
description: Automated video editing using FFmpeg. Use when trimming videos, merging clips, adding audio, or automating video production workflows.
version: 1.0.0
---

# Video Editor

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific video quality settings, encoding preferences, and workflow defaults.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Automate video editing tasks with FFmpeg-powered operations including trimming, merging, audio mixing, and format conversion.

## Tools

**VideoEditor.py** (in src/):
- Video trimming and cutting
- Clip merging and concatenation
- Audio track mixing and replacement
- Format conversion (MP4, MOV, AVI, etc.)
- Resolution and quality adjustment
- Thumbnail extraction
- Batch processing support
- Metadata preservation

## Core Workflow

### 1. Video Preparation
- Receive video file(s) and editing requirements
- Validate file formats and codecs
- Determine output specifications
- Plan editing operations

### 2. Editing Operations
- Trim videos to specific time ranges
- Merge multiple clips into one
- Add or replace audio tracks
- Convert formats and resolutions
- Extract thumbnails or frames
- Apply basic filters if needed

### 3. Delivery
- Export in requested format and quality
- Validate output file integrity
- Package with metadata (duration, resolution, file size)
- Handoff for distribution or further processing

## Usage

**Trim Video:**
```python
from superskills.videoeditor.src import VideoEditor

editor = VideoEditor(output_dir="output/videos")

result = editor.trim_video(
    input_file="long_recording.mp4",
    start_time="00:02:30",
    end_time="00:15:45",
    output_name="trimmed_section"
)

print(f"Trimmed video: {result.output_file}")
print(f"Duration: {result.duration_seconds}s")
```

**Merge Multiple Videos:**
```python
clips = [
    "intro.mp4",
    "main_content.mp4",
    "outro.mp4"
]

result = editor.merge_videos(
    input_files=clips,
    output_name="complete_video"
)

print(f"Merged video: {result.output_file}")
```

**Add Audio Track:**
```python
result = editor.add_audio(
    video_file="video.mp4",
    audio_file="narration.mp3",
    output_name="video_with_audio"
)
```

**Convert Format:**
```python
result = editor.convert_format(
    input_file="video.mov",
    output_format="mp4",
    quality="high"
)
```

**Extract Thumbnail:**
```python
thumbnail = editor.extract_thumbnail(
    video_file="video.mp4",
    timestamp="00:00:10",
    output_name="thumbnail.jpg"
)
```

## Environment Variables

```bash
# No API keys required - FFmpeg is a local tool
# Ensure FFmpeg is installed on system
```

**FFmpeg Installation:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from ffmpeg.org
```

## Quality Checklist

- [ ] FFmpeg installed and accessible
- [ ] Input video formats supported
- [ ] Output quality appropriate for use case
- [ ] Audio sync maintained (if applicable)
- [ ] File size reasonable for distribution
- [ ] Metadata preserved or updated
- [ ] Output validated before delivery

## Avoid

- **Quality Loss**: Re-encoding unnecessarily → Use copy codec when possible
- **Audio Desync**: Ignoring timing → Validate audio sync after edits
- **Large Files**: Maximum quality always → Match quality to distribution needs
- **Format Issues**: Unsupported codecs → Convert to widely supported formats
- **Missing FFmpeg**: Assume installed → Check FFmpeg availability first

## Escalate When

- FFmpeg not installed or misconfigured
- Complex editing beyond basic operations (effects, transitions)
- Need professional-grade color grading
- Performance issues with large files
- Codec compatibility problems

## Integration Examples

**With Transcriber (Add Subtitles):**
```python
from superskills.transcriber.src import Transcriber
from superskills.videoeditor.src import VideoEditor

transcriber = Transcriber()
subs = transcriber.transcribe("video.mp4", output_format="srt")

editor = VideoEditor()
result = editor.add_subtitles(
    video_file="video.mp4",
    subtitle_file=subs.output_file,
    output_name="video_with_subs"
)
```

**With Narrator (Add Voiceover):**
```python
from superskills.narrator.src import VoiceoverGenerator
from superskills.videoeditor.src import VideoEditor

narrator = VoiceoverGenerator()
audio = narrator.generate(
    script="Welcome to this tutorial...",
    content_type="educational"
)

editor = VideoEditor()
result = editor.add_audio(
    video_file="silent_video.mp4",
    audio_file=audio['output_file'],
    output_name="video_with_narration"
)
```

**With CoursePackager (Package Video Course):**
```python
from superskills.videoeditor.src import VideoEditor
from superskills.coursepackager.src import CoursePackager

editor = VideoEditor()

# Merge lesson videos
lessons = ["lesson1.mp4", "lesson2.mp4", "lesson3.mp4"]
full_course = editor.merge_videos(lessons, output_name="full_course")

# Package with materials
packager = CoursePackager()
package = packager.package_course(
    course_name="Video Course",
    files=[full_course.output_file, "workbook.pdf"]
)
```

## Common Operations

**Trim**: Cut video to specific time range  
**Merge**: Concatenate multiple clips  
**Add Audio**: Mix or replace audio track  
**Convert**: Change format/codec  
**Extract**: Get thumbnails or frames  
**Resize**: Change resolution  
**Compress**: Reduce file size  

## Dependencies

```bash
# System dependency
ffmpeg (install via package manager)

# Python wrapper
pip install ffmpeg-python
```
