---
name: developer-tester
description: Design and execute comprehensive testing strategies for software quality. Use when creating test plans, writing test cases, performing testing, or ensuring production readiness.
version: 1.0.0
license: MIT
---

# Developer Tester

> **Note**: Review [PROFILE.md](PROFILE.md) in this skill folder for user-specific testing scope, tech stack, and quality standards.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Plan, design, and execute testing to ensure software quality, reliability, and user satisfaction before production deployment.

## Core Workflow

### 1. Test Planning
- Review requirements and acceptance criteria
- Identify test scope and coverage areas
- Define test strategy (unit, integration, E2E, UAT)
- Estimate effort and timeline

### 2. Test Case Design
- Write detailed test cases with steps
- Cover happy paths, edge cases, error conditions
- Prioritize by risk and user impact
- Document expected vs. actual results

### 3. Test Execution
- Execute test cases systematically
- Document defects with reproduction steps
- Assign severity and priority
- Verify fixes and perform regression testing

### 4. Reporting & Sign-off
- Report test coverage and results
- Assess production readiness
- Document known issues and risks
- Recommend go/no-go decision

## Quality Checklist

- [ ] Test plan covers all critical user flows
- [ ] Edge cases and error conditions tested
- [ ] Defects documented with clear reproduction steps
- [ ] Severity appropriately assigned (critical, high, medium, low)
- [ ] Regression testing completed after fixes
- [ ] Performance and security considerations addressed
- [ ] User acceptance criteria met
- [ ] Production readiness report provided

## Testing Frameworks

**See PROFILE.md for:**
- Tech stack and testing tools
- Quality bar and acceptance criteria
- Testing environments

**Test Types:**
- **Unit Tests**: Individual functions/components
- **Integration Tests**: Component interactions
- **E2E Tests**: Complete user workflows
- **UAT**: Real user validation
- **Performance**: Load, stress, scalability
- **Security**: Vulnerabilities, data protection

## Bug Report Template

**Bug ID**: [Unique identifier]  
**Title**: [Brief description]  
**Severity**: [Critical / High / Medium / Low]  
**Priority**: [P0 / P1 / P2 / P3]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]  
**Actual Result**: [What actually happened]  
**Environment**: [Browser, OS, version]  
**Screenshots/Logs**: [Attach evidence]

## Test Case Template

```
TC-[ID]: [Test Case Name]

Preconditions:
- [Required setup or state]

Test Steps:
1. [Action 1]
2. [Action 2]
3. [Action 3]

Expected Results:
1. [Expected outcome for step 1]
2. [Expected outcome for step 2]
3. [Expected outcome for step 3]

Test Data: [Any specific data needed]
Priority: [High / Medium / Low]
Type: [Functional / UI / Performance / Security]
```

## Avoid

- **Happy Path Only**: Test ideal scenario → Cover edge cases, errors, validation
- **Vague Bug Reports**: "It doesn't work" → Specific steps, expected vs. actual
- **Test Once**: Initial test only → Regression test after fixes
- **Skip UAT**: Developer testing only → Real user validation before launch
- **No Automation**: Manual only → Automate repetitive critical tests
- **Ignore Performance**: Functional only → Load test critical flows

## Escalate When

- Critical bugs block release
- Unclear requirements prevent testing
- Test environment issues delay testing
- Security vulnerabilities discovered
- Performance issues under load
- Insufficient time for adequate testing
- Need for specialized testing expertise
