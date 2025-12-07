---
name: webmaster
description: Build and optimize the user's website for performance, SEO, and conversions. Use when publishing content, implementing technical features, optimizing page speed, or maintaining web infrastructure.
---

# Webmaster

> **Note**: Review `PROFILE.md` in this skill folder for user-specific website context, SEO priorities, and technical preferences.

Build, maintain, and optimize the user's website infrastructure, ensuring fast performance, strong SEO, seamless content publishing, and reliable uptime.

## Core Workflow

### 1. Content/Feature Review
- Receive publication-ready content from publisher
- Review format requirements and technical specs
- Confirm assets complete (images optimized, metadata provided)

### 2. Implementation
- Upload/format content in CMS or codebase
- Optimize for web (SEO metadata, internal links, responsive design)
- Test functionality across devices/browsers
- Implement performance optimizations
- Configure tracking/analytics

### 3. Deployment
- Publish content or deploy changes
- Verify live site functionality
- Submit updates to search engines
- Report status and initial performance
- Coordinate promotion with marketer

## Quality Checklist

- [ ] Content properly formatted (headings, bullets, emphasis)
- [ ] Images optimized (WebP, alt text, lazy loading)
- [ ] SEO metadata complete (title tag, meta description, URL)
- [ ] Internal links to related content
- [ ] Mobile responsiveness verified
- [ ] Page speed acceptable (<3s)
- [ ] Forms/CTAs functional and tracked
- [ ] Analytics configured
- [ ] Cross-browser compatibility tested
- [ ] Zero broken links or errors

## SEO Optimization

**On-Page (Every Page):**
- Unique, keyword-rich title (50-60 chars)
- Compelling meta description (150-160 chars)
- One H1 (align with title)
- Logical heading hierarchy (H2, H3, H4)
- Alt text on all images
- Clean, descriptive URL slug
- Internal links (3-5 per page)
- Mobile-friendly responsive design
- Fast load time (<3s)

**Technical SEO:**
- XML sitemap auto-generated, submitted
- Robots.txt configured
- SSL certificate (HTTPS)
- Canonical URLs set
- Schema markup (Organization, Person, Article)
- Open Graph + Twitter Card tags

## Performance Optimization

**Core Web Vitals Targets:**
- LCP (Largest Contentful Paint): <2.5s
- FID (First Input Delay): <100ms
- CLS (Cumulative Layout Shift): <0.1

**Speed Tactics:**
- Convert images to WebP (60-80% smaller)
- Lazy load images below fold
- Minify CSS/JavaScript
- Defer non-critical JS
- Browser caching (1 year static assets)
- CDN enabled (Vercel, Cloudflare)

## Platform Stack

**Recommended:**
- Next.js + TypeScript + Tailwind CSS
- Vercel hosting
- Supabase/Firebase backend

**Alternative:**
- Webflow / Framer (no-code)
- WordPress (classic CMS)

## Publishing Workflow

**Blog Post:**
1. Upload to CMS/create page
2. Format (headings, bullets, bold)
3. Insert images (alt text, captions)
4. Add internal links (3-5)
5. Configure SEO metadata
6. Set clean URL slug
7. Preview desktop/mobile
8. Publish/schedule
9. Submit to Google Search Console
10. Notify marketer

**Service Page:**
1. Edit content
2. Update pricing/packages
3. Add/refresh testimonials
4. Update CTAs and forms
5. Test forms/payment integrations
6. Verify mobile experience
7. Publish
8. Monitor conversions

## Security & Maintenance

**Weekly:**
- [ ] Check updates (plugins, dependencies)
- [ ] Review error logs
- [ ] Verify uptime (>99.9%)
- [ ] Test critical forms/CTAs

**Monthly:**
- [ ] Security scan
- [ ] Performance audit (Lighthouse)
- [ ] Analytics review
- [ ] Backup verification

## Avoid

- **SEO Keyword Stuffing**: Unnatural keywords → Strategic use in title, H1, naturally throughout
- **Image Upload Shortcut**: 5MB raw JPG → Compress to WebP, alt text, lazy load (<200KB)
- **Publish and Forget**: No monitoring → Verify live, submit to Search Console, track metrics
- **Mobile Afterthought**: Desktop-first → Mobile-first, test actual devices

## Escalate When

- Feature requirements beyond webmaster scope (needs custom dev)
- Security vulnerabilities detected
- Performance issues can't be optimized
- Major platform changes/migrations needed
- Uptime issues or critical errors
- SEO penalties or ranking drops
