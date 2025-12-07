---
name: marketer
description: Distribute content across social platforms using Notion+n8n for scheduling and automation. Use when optimizing posts for each platform, managing content calendar, or building community engagement.
---

# Marketer

> **Note**: Review `PROFILE.md` in this skill folder for user-specific platform strategy, brand voice, target audiences, and best posting times.

Distribute content across social media, optimize for engagement, manage content calendar, analyze performance, and build community.

## Tools

**Note**: This skill now uses Notion+n8n for content distribution (previously Postiz). Python tools included for reference but primary workflow uses Notion database + n8n automation.

**SocialMediaPublisher.py** (in src/ - reference implementation):
- Multi-platform posting (LinkedIn, Twitter, Instagram)
- Platform-specific formatting
- Scheduling with optimal timing
- Post preview/validation
- Hashtag strategy

**Primary Workflow**: Notion database → n8n automation → Platform publishing

## Core Workflow

### 1. Content Reception
- Receive publication-ready content from publisher/author
- Review strategic objective and target audience
- Confirm platform assets complete (images, captions, links)

### 2. Distribution
- Add to Notion content calendar with platform tags
- Optimize for each platform (format, length, hashtags)
- Schedule via n8n based on best times
- Execute engagement tactics (comment, respond)
- Monitor performance and adjust

### 3. Reporting
- Confirm scheduling with calendar overview
- Report engagement metrics
- Recommend optimizations
- Flag opportunities for reactive content

## Quality Checklist

- [ ] Content optimized per platform (not copy-paste)
- [ ] Best posting times selected
- [ ] Hashtags relevant and strategic (3-5 max)
- [ ] CTAs clear and aligned
- [ ] Visual assets platform-appropriate
- [ ] Links functional and tracked
- [ ] Engagement plan in place
- [ ] Performance tracking configured

## Platform Optimization

**LinkedIn (Primary):**
- Frequency: 3-5x/week
- Best Times: Tue-Thu, 8-10am, 12-1pm, 5-6pm ET
- Format: [Hook line] → [Context 2-3 paragraphs] → [Insight/framework] → [CTA] → #Hashtags
- Engagement: Post as personal, comment on 5-10 posts before, respond within 1hr

**Twitter/X:**
- Frequency: 5-7x/week
- Best Times: Mon-Fri, 9am, 12pm, 5pm ET
- Format: Threads (1/ Hook → 2-8/ Insights → 9/ Summary+CTA)
- Engagement: Quote tweet news, reply to conversations

**Instagram:**
- Frequency: 3-4x/week
- Best Times: Mon/Wed/Fri, 11am, 2pm, 7pm ET
- Format: Carousels/Reels with captions, first line hooks
- Engagement: Stories for behind-scenes, polls, questions

## Content Repurposing

1 blog post → 13+ social pieces:
- LinkedIn article (full)
- 3 LinkedIn posts (key insights)
- Twitter thread (summary)
- 5 standalone tweets (quotes)
- Instagram carousel (visual breakdown)
- 2 Instagram posts (quotes)
- 1 Instagram Reel (video summary)

## Automation with Notion+n8n

**Notion Content Calendar:**
- Columns: Title, Platform, Status, Publish Date, Content, Image, Hashtags
- Views: By Platform, This Week, Published, Drafts

**n8n Workflow:**
1. Trigger: Notion item status → "Ready to Publish"
2. Extract content, image, platform
3. Format per platform specs
4. Schedule via platform APIs
5. Update Notion status → "Published"
6. Log to analytics

## Avoid

- **Copy-Paste Broadcast**: Identical content everywhere → Optimize for each platform
- **Post and Ghost**: Schedule and disappear → Comment, respond, engage
- **Hashtag Spam**: 20+ irrelevant tags → 3-5 strategic, relevant hashtags
- **Vanity Metrics**: Chase followers/likes → Track engagement rate, leads, conversions

## Escalate When

- Content underperforming (2+ weeks low engagement)
- Negative feedback or reputation issues
- Algorithm changes impacting reach
- Competitor activity requires response
- Major timely opportunity outside calendar
