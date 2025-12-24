---
name: transcriber-local
description: Privacy-focused offline transcription using local Whisper models. Use when data privacy is critical, offline operation is needed, or avoiding API costs. Runs entirely on your machine.
version: 1.0.0
---

# Transcriber Local

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific model preferences, output formatting, and privacy settings.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Privacy-first offline transcription using local Whisper models. Perfect for sensitive content, offline workflows, and cost-conscious projects.

## Tools

**LocalTranscriber.py** (in src/):
- Runs Whisper models locally (no cloud API)
- Multiple model sizes (tiny, base, small, medium, large)
- GPU acceleration support (CUDA)
- Complete data privacy (nothing leaves your machine)
- No usage limits or API costs
- Word-level timestamps
- Multiple output formats (TXT, JSON, SRT, VTT)
- Batch processing support

## Core Workflow

### 1. Model Selection
- Choose model size based on accuracy/speed trade-off:
  - `tiny`: Fastest, lowest accuracy (~1GB RAM)
  - `base`: Fast, decent accuracy (~1GB RAM)
  - `small`: Balanced (~2GB RAM) **[Recommended]**
  - `medium`: High accuracy (~5GB RAM)
  - `large`: Highest accuracy (~10GB RAM)
- Models are cached after first download

### 2. Transcription
- Load model into memory (cached for subsequent runs)
- Process audio/video file locally
- Extract word-level timestamps
- Detect language automatically
- Generate confidence scores

### 3. Delivery
- Export in requested format (TXT, JSON, SRT, VTT)
- Save locally with metadata
- Compatible with same workflow integrations as cloud transcriber

## Usage

**Basic Local Transcription:**
```python
from superskills.transcriber_local.src import LocalTranscriber

transcriber = LocalTranscriber(model_size="small")
result = transcriber.transcribe("recording.mp3")
print(result.transcript)
```

**GPU Acceleration:**
```python
transcriber = LocalTranscriber(model_size="medium", device="cuda")
result = transcriber.transcribe("video.mp4")
```

**Batch Processing:**
```python
files = ["session1.mp3", "session2.mp3", "session3.mp3"]
results = transcriber.transcribe_batch(files)
```

## Privacy Benefits

✅ **No Data Transmission**: All processing happens locally
✅ **GDPR Compliant**: No third-party data sharing
✅ **Offline Capable**: Works without internet
✅ **No Usage Limits**: Transcribe unlimited content
✅ **Zero API Costs**: One-time model download only

## Performance Comparison

| Model | Speed (1hr audio) | Accuracy | VRAM |
|-------|-------------------|----------|------|
| tiny  | ~2 min           | Good     | 1GB  |
| base  | ~3 min           | Better   | 1GB  |
| small | ~5 min           | Great    | 2GB  |
| medium| ~12 min          | Excellent| 5GB  |
| large | ~30 min          | Best     | 10GB |

*Times on CPU. GPU acceleration 3-10x faster.*

## Integration with Other Skills

**→ author**: Converts transcripts into structured content
**→ editor**: Polishes transcripts for publication
**→ narrator**: Creates audio from edited transcripts (round-trip workflow)
**→ coursepackager**: Packages transcripts into training materials

## Setup

**Install Dependencies:**
```bash
pip install openai-whisper
# Optional GPU support:
pip install openai-whisper[cuda]  # NVIDIA
pip install openai-whisper[metal] # Apple Silicon
```

**First Run:**
```python
transcriber = LocalTranscriber(model_size="small")
# Model downloads automatically (~500MB for small model)
```

## When to Use Local vs Cloud

**Use transcriber-local when:**
- Privacy/compliance requires on-premise processing
- Working offline or with unreliable internet
- Processing large volumes (API costs add up)
- Need complete control over data flow

**Use transcriber (cloud) when:**
- Need fastest possible results (cloud GPUs)
- Don't have powerful local hardware
- Prefer not managing local models
- Working with very large files (>10GB)

## Quality Checklist

Before finalizing transcripts:
- [ ] Choose appropriate model size for your accuracy needs
- [ ] Verify language detection is correct
- [ ] Check timestamps align with audio/video
- [ ] Review confidence scores for low-quality sections
- [ ] Test with sample before batch processing
- [ ] Ensure sufficient disk space for model cache

## Troubleshooting

**Model Download Fails:**
- Check internet connection (first-time only)
- Verify disk space (~500MB-3GB per model)
- Try different model size

**Out of Memory:**
- Use smaller model (tiny or base)
- Process shorter segments
- Close other applications
- Add more RAM or use cloud transcriber

**Slow Performance:**
- Use GPU if available
- Choose smaller model
- Process shorter files
- Consider cloud transcriber for speed

## Examples

**Secure Client Recordings:**
```python
# Sensitive coaching sessions - never leave your machine
transcriber = LocalTranscriber(model_size="medium")
result = transcriber.transcribe("client_session.mp3")
```

**Offline Field Work:**
```python
# No internet? No problem
transcriber = LocalTranscriber(model_size="base")
results = transcriber.transcribe_batch(["interview1.wav", "interview2.wav"])
```

**Cost-Effective Bulk Processing:**
```python
# Process 100 hours of content with zero API costs
transcriber = LocalTranscriber(model_size="small", device="cuda")
for file in large_audio_collection:
    result = transcriber.transcribe(file)
```

## Security & Compliance

- **HIPAA**: Suitable for healthcare recordings (no PHI transmission)
- **GDPR**: Compliant (no personal data leaves your control)
- **SOC 2**: Compatible with on-premise requirements
- **Zero Trust**: No external API dependencies

## Next Steps

After transcription:
1. Review and edit transcripts
2. Extract key quotes or highlights
3. Create structured content with `author`
4. Package into course materials with `coursepackager`
5. Generate video captions (SRT/VTT output)
