# Marketer Agent Tools

Social media distribution and scheduling for CoachSteff using Postiz API.

## Overview

The Marketer Agent provides Python tools for multi-platform social media posting:
- **SocialMediaPublisher.py** - Unified posting to LinkedIn, Twitter/X, Instagram via Postiz

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
export POSTIZ_API_KEY="your_postiz_api_key"
export POSTIZ_WORKSPACE_ID="your_workspace_id"
```

## Usage

### Basic Post

```python
from agents.marketer.src.SocialMediaPublisher import SocialMediaPublisher, Platform

publisher = SocialMediaPublisher()

results = publisher.post(
    content="New blog post: Why AI Adoption Fails (And How to Fix It)",
    platforms=[Platform.LINKEDIN, Platform.TWITTER],
    hashtags=["AIAdoption", "Productivity", "Leadership"]
)

for result in results:
    print(f"{result.platform}: {result.status} - ID: {result.post_id}")
```

### Scheduled Post

```python
from datetime import datetime, timedelta

# Schedule for tomorrow at optimal time
optimal_time = publisher.get_optimal_time(Platform.LINKEDIN, days_ahead=1)

results = publisher.post(
    content="Join our upcoming webinar on AI-native workflows!",
    platforms=[Platform.LINKEDIN],
    schedule_time=optimal_time,
    link="https://coachsteff.com/webinar"
)
```

### Platform-Specific Optimization

```python
# Preview how content will appear on each platform
preview_linkedin = publisher.preview_post(
    content="Long-form content here...",
    platform=Platform.LINKEDIN,
    hashtags=["AI", "Productivity"]
)

preview_twitter = publisher.preview_post(
    content="Same content automatically optimized for Twitter",
    platform=Platform.TWITTER,
    hashtags=["AI", "Productivity"]
)

print(f"LinkedIn: {preview_linkedin['character_count']} chars")
print(f"Twitter: {preview_twitter['character_count']} chars")
```

### Post with Image

```python
results = publisher.post(
    content="Check out our new infographic on AI adoption!",
    platforms=[Platform.LINKEDIN, Platform.INSTAGRAM],
    image_path="output/images/ai-adoption-framework.png",
    hashtags=["AIStrategy", "Infographic"]
)
```

## Platform Specifications

### Character Limits
- **LinkedIn**: 3,000 characters
- **Twitter/X**: 280 characters
- **Instagram**: 2,200 characters
- **Facebook**: 63,206 characters

### Optimal Posting Times (EST)
- **LinkedIn**: Tuesday 10am, Wednesday 12pm, Thursday 9am
- **Twitter**: Monday 9am, Wednesday 12pm, Friday 9am
- **Instagram**: Monday 11am, Wednesday 2pm, Friday 4pm

### Hashtag Strategy
- **LinkedIn**: 3-5 hashtags at end of post
- **Twitter**: 2-3 hashtags inline
- **Instagram**: 5-10 hashtags on separate line

## Documentation

See `SKILL.md` for full agent capabilities, quality gates, and marketing best practices.
