---
name: emailcampaigner
description: Email campaign management using SendGrid. Use when sending marketing emails, creating campaigns, or managing audience communication at scale.
---

# Email Campaigner

Manage and execute email campaigns with professional templates, personalization, and delivery tracking using SendGrid.

## Tools

**EmailCampaigner.py** (in src/):
- Email sending via SendGrid API
- Template rendering with Jinja2
- Batch campaign management
- Personalization and variable substitution
- Delivery status tracking
- HTML and plain text support
- Campaign logging and analytics

## Core Workflow

### 1. Campaign Preparation
- Define recipient list and segments
- Create or select email template
- Prepare personalization data
- Review content and subject lines

### 2. Email Sending
- Render templates with personalization
- Send emails via SendGrid API
- Track delivery status per recipient
- Handle errors gracefully
- Log all campaign activity

### 3. Monitoring & Delivery
- Record delivery status and message IDs
- Track success/failure rates
- Export campaign logs
- Report on campaign performance

## Usage

**Send Single Email:**
```python
from superskills.emailcampaigner.src import EmailCampaigner

emailer = EmailCampaigner(
    output_dir="output/emails",
    templates_dir="templates/email"
)

result = emailer.send_email(
    to_email="student@example.com",
    subject="Welcome to the Course!",
    content="<h1>Welcome!</h1><p>Thanks for joining...</p>",
    content_type="text/html"
)

print(f"Status: {result.status}")
print(f"Message ID: {result.message_id}")
```

**Send Campaign with Template:**
```python
recipients = [
    {"email": "student1@example.com", "name": "Alice"},
    {"email": "student2@example.com", "name": "Bob"}
]

for recipient in recipients:
    result = emailer.send_email(
        to_email=recipient["email"],
        subject=f"Hey {recipient['name']}, here's your course!",
        content="welcome_template.html",
        template_data={"name": recipient["name"]}
    )
```

**Batch Campaign:**
```python
campaign_results = emailer.send_campaign(
    recipient_list=["email1@example.com", "email2@example.com"],
    subject="New Training Available",
    template="campaign_template.html",
    template_data={"course_name": "AI Automation 101"}
)

success_count = sum(1 for r in campaign_results if r.status == "sent")
print(f"Successfully sent: {success_count}/{len(campaign_results)}")
```

## Environment Variables

```bash
# Required: SendGrid API key
SENDGRID_API_KEY=your_sendgrid_api_key

# Optional: Default sender email (must be verified in SendGrid)
SENDGRID_FROM_EMAIL=your@verified-email.com
```

**Setup Instructions:**
1. Create SendGrid account at sendgrid.com
2. Verify sender email address
3. Generate API key with "Mail Send" permissions
4. Add to `.env` file

## Quality Checklist

- [ ] SendGrid API key configured
- [ ] Sender email verified in SendGrid
- [ ] Email content tested (preview, spam check)
- [ ] Personalization variables working
- [ ] Unsubscribe link included (if marketing)
- [ ] Delivery status logged
- [ ] Error handling for bounces/failures

## Avoid

- **Unverified Senders**: Random email → Verified sender in SendGrid
- **No Personalization**: Generic emails → Use recipient name and context
- **Missing Unsubscribe**: Marketing spam → Include unsubscribe option
- **Ignoring Failures**: Assume sent → Check delivery status
- **Hard-coded Content**: Static text → Use templates with variables

## Escalate When

- SendGrid account suspended or limited
- High bounce rates or spam complaints
- Need advanced features (A/B testing, automation)
- Compliance issues (GDPR, CAN-SPAM)
- Large campaigns exceeding SendGrid limits

## Integration Examples

**With Craft (Draft Campaigns in Craft):**
```python
from superskills.craft.src import CraftClient
from superskills.emailcampaigner.src import EmailCampaigner

craft = CraftClient()
emailer = EmailCampaigner()

doc = craft.get_document("email_campaign_draft")

emailer.send_campaign(
    recipient_list=["student1@example.com", "student2@example.com"],
    subject=doc.title,
    content=doc.content
)
```

**With Author (Generate Email Content):**
```python
from superskills.author.src import ContentWriter
from superskills.emailcampaigner.src import EmailCampaigner

writer = ContentWriter()
email_content = writer.create_email_copy(
    topic="New Course Launch",
    tone="professional",
    length="short"
)

emailer = EmailCampaigner()
emailer.send_campaign(
    recipient_list=["list@example.com"],
    subject="Exciting News: New Course Available!",
    content=email_content
)
```

## Dependencies

```bash
pip install sendgrid jinja2
```
