---
name: n8n-workflow
description: Design and build n8n automation workflows. Use when creating automations, connecting APIs, optimizing workflows, or troubleshooting n8n implementations.
license: MIT
---

# n8n Workflow Specialist

> **Note**: Review `PROFILE.md` in this skill folder for user-specific use cases, common workflows, and integration preferences.

Design, build, and optimize n8n automation workflows that connect tools, automate processes, and eliminate repetitive tasks.

## Core Workflow

### 1. Requirements & Planning
- Understand automation goal and trigger conditions
- Identify systems and data to connect
- Map current manual process
- Define success criteria and error handling

### 2. Workflow Design
- Choose appropriate trigger (webhook, schedule, manual)
- Plan node sequence and logic flow
- Design data transformation steps
- Plan error handling and fallbacks

### 3. Node Configuration
- Configure each node with proper credentials
- Set up data mapping between nodes
- Implement conditional logic and routing
- Add error handling nodes

### 4. Testing & Optimization
- Test with real data
- Verify error handling works
- Optimize for performance
- Document workflow purpose and maintenance

## Quality Checklist

- [ ] Clear trigger conditions defined
- [ ] Error handling implemented
- [ ] Credentials properly configured
- [ ] Data validation at key steps
- [ ] Workflow documented with notes
- [ ] Tested with real data
- [ ] Performance optimized (minimize API calls)
- [ ] Monitoring/alerting configured

## n8n Fundamentals

**See PROFILE.md for:**
- Common workflow templates
- Integration preferences
- Use case examples

**Core Concepts:**

**Nodes:**
- **Trigger Nodes**: Start workflow (webhook, schedule, manual)
- **Regular Nodes**: Process data, call APIs, transform
- **Logic Nodes**: IF, Switch, Merge, Split
- **Output Nodes**: Send data to destinations

**Data Flow:**
- Each node receives input from previous node
- Nodes output data for next node
- Use expressions to reference previous node data: `{{ $json.fieldName }}`
- Multiple items can flow through workflow

**Credentials:**
- Store in n8n credentials manager
- Never hardcode API keys
- Use environment variables for sensitive data

## Common Node Types

### Triggers
- **Webhook**: Receive HTTP requests
- **Schedule**: Cron-based timing
- **Manual Trigger**: Button click
- **Email Trigger**: IMAP monitoring
- **RSS Feed**: Monitor feed for new items

### Data Processing
- **Set**: Add/modify data fields
- **Code**: JavaScript for custom logic
- **Function**: Transform data
- **Split In Batches**: Process large datasets
- **Merge**: Combine multiple inputs

### Integrations
- **HTTP Request**: Call any API
- **OpenAI**: GPT completions, embeddings
- **Anthropic**: Claude API
- **Airtable**: Database operations
- **Google Sheets**: Spreadsheet operations
- **Email**: Send via SMTP
- **Slack**: Post messages
- **Notion**: Database queries

### Logic & Control
- **IF**: Conditional branching
- **Switch**: Multiple conditions
- **Filter**: Remove items
- **Wait**: Delay execution
- **Error Trigger**: Catch workflow errors

## Workflow Templates

### API to Spreadsheet Logger
```
Trigger: Webhook
→ HTTP Request (fetch data from API)
→ Set (format data)
→ Google Sheets (append row)
→ Slack (send notification)
```

### Content Distribution Pipeline
```
Trigger: Manual or Webhook
→ OpenAI (generate variations)
→ IF (check content length)
  → True: Split content
  → False: Continue
→ Multiple paths:
  → LinkedIn (post)
  → Twitter (post)
  → Email (draft)
→ Airtable (log results)
```

### Lead Enrichment Workflow
```
Trigger: Webhook (new lead)
→ HTTP Request (enrich from Clearbit)
→ IF (score > threshold)
  → True: 
    → Slack (notify sales)
    → CRM (update record)
  → False:
    → Email (nurture sequence)
```

### Research Automation
```
Trigger: Schedule (daily)
→ RSS (fetch news)
→ OpenAI (summarize articles)
→ Filter (relevance check)
→ Notion (create page)
→ Email (send digest)
```

## Best Practices

### Error Handling
- Add **Error Trigger** node to catch failures
- Use **IF** nodes to validate data before processing
- Set **Retry on Fail** for API calls
- Send error notifications to Slack/email

### Performance
- Minimize API calls (batch when possible)
- Use **Split In Batches** for large datasets
- Cache frequently used data
- Avoid unnecessary data transformations

### Maintenance
- Use **Sticky Notes** to document complex logic
- Name nodes descriptively
- Version control workflow exports
- Test regularly with production data
- Monitor execution logs

### Security
- Never hardcode credentials
- Use environment variables
- Validate webhook signatures
- Sanitize user inputs
- Limit webhook exposure

## Debugging Tips

**Common Issues:**

**"No data" error:**
- Check previous node executed successfully
- Verify data path: `{{ $json.fieldName }}`
- Ensure node received input

**"Missing credentials" error:**
- Add credentials in Settings
- Select correct credential in node
- Test credential connection

**"Rate limit" error:**
- Add **Wait** node between requests
- Implement exponential backoff
- Use **Split In Batches** with delay

**"Workflow timeout" error:**
- Split into smaller workflows
- Use **Split In Batches**
- Optimize slow nodes

## Expression Examples

```javascript
// Access previous node data
{{ $json.email }}
{{ $json.user.name }}

// Current date/time
{{ $now.format('YYYY-MM-DD') }}
{{ $today.toISO() }}

// String manipulation
{{ $json.name.toLowerCase() }}
{{ $json.text.substring(0, 100) }}

// Conditional logic
{{ $json.score > 80 ? 'high' : 'low' }}

// Array operations
{{ $json.items.length }}
{{ $json.tags.join(', ') }}

// Math
{{ $json.price * 1.2 }}
{{ Math.round($json.value) }}
```

## Avoid

- **No Error Handling**: Assume success → Add error triggers and validation
- **Hardcoded Values**: API keys in nodes → Use credentials manager
- **No Testing**: Deploy untested → Test with real data first
- **Complex Single Workflow**: 50+ nodes → Break into sub-workflows
- **No Documentation**: Unclear purpose → Add sticky notes, descriptive names
- **Ignore Logs**: Don't check executions → Monitor for failures

## Escalate When

- Need custom node development
- Complex authentication (OAuth2, custom)
- Performance issues at scale
- Webhook security concerns
- Integration not available as node
- Workflow too complex (consider custom code)
