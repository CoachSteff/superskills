---
name: risk-manager
description: Identify, assess, and manage business risks using ISO 31000 framework. Use when conducting risk assessments, developing mitigation plans, or establishing risk management processes.
version: 1.0.0
---

# Risk Manager

> **Note**: Review [PROFILE.md](PROFILE.md) in this skill folder for user-specific risk context, business operations, and risk appetite.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Apply ISO 31000 risk management principles to identify, assess, treat, and monitor risks across business operations.

## Core Workflow

### 1. Risk Identification
- Review business context (see PROFILE.md)
- Identify internal and external risk sources
- Brainstorm potential risk events
- Categorize risks by domain (strategic, operational, financial, compliance, reputational)

### 2. Risk Analysis
- Assess likelihood (1-5 scale: rare to almost certain)
- Evaluate impact (1-5 scale: negligible to catastrophic)
- Calculate risk level (likelihood × impact)
- Consider existing controls and their effectiveness
- Document assumptions and uncertainties

### 3. Risk Evaluation
- Compare risk levels against risk appetite (see PROFILE.md)
- Prioritize risks requiring treatment
- Determine risk response strategy (avoid, reduce, transfer, accept)
- Identify quick wins vs. long-term initiatives

### 4. Risk Treatment
- Design mitigation controls and actions
- Assign ownership and accountability
- Set implementation timeline
- Define success criteria and monitoring approach
- Document residual risk after treatment

### 5. Monitoring & Review
- Track risk indicators and triggers
- Review effectiveness of controls
- Update risk assessment for changes
- Report to stakeholders
- Continuously improve risk management

## Quality Checklist

- [ ] Risks clearly described with potential impact scenarios
- [ ] Likelihood and impact assessments justified
- [ ] Existing controls documented and assessed
- [ ] Risk treatment aligned with risk appetite (see PROFILE.md)
- [ ] Ownership assigned for each risk
- [ ] Monitoring approach defined
- [ ] Residual risk acceptable or escalated
- [ ] Documentation follows ISO 31000 principles

## ISO 31000 Risk Assessment

### Risk Rating Matrix

**Likelihood Scale:**
1. Rare (< 10% probability in 12 months)
2. Unlikely (10-30%)
3. Possible (30-50%)
4. Likely (50-80%)
5. Almost Certain (> 80%)

**Impact Scale:**
1. Negligible (minimal business impact)
2. Minor (small financial loss, temporary disruption)
3. Moderate (noticeable impact, recoverable)
4. Major (significant impact, difficult recovery)
5. Catastrophic (existential threat, business failure)

**Risk Level = Likelihood × Impact**
- **Critical** (20-25): Immediate action required
- **High** (12-16): Priority treatment needed
- **Medium** (6-10): Monitor and plan treatment
- **Low** (1-5): Accept or minor controls

### Risk Treatment Strategies

**See PROFILE.md for risk appetite guidance.**

**Avoid**: Eliminate the activity causing the risk
**Reduce**: Implement controls to lower likelihood or impact
**Transfer**: Insurance, contracts, outsourcing
**Accept**: Acknowledge risk within appetite, monitor

## Risk Register Template

### Risk Entry
**Risk ID**: [Unique identifier]  
**Category**: [Strategic / Operational / Financial / Compliance / Reputational]  
**Description**: [What could go wrong]  
**Cause**: [Why it might happen]  
**Impact**: [Consequences if it occurs]

### Assessment
**Likelihood**: [1-5 with justification]  
**Impact**: [1-5 with justification]  
**Risk Level**: [L×I score and rating]  
**Current Controls**: [What's in place now]  
**Control Effectiveness**: [How well controls work]

### Treatment
**Strategy**: [Avoid / Reduce / Transfer / Accept]  
**Actions**: [Specific mitigation steps]  
**Owner**: [Who is responsible]  
**Timeline**: [When actions will be completed]  
**Resources**: [Budget, tools, people needed]  
**Residual Risk**: [Expected risk after treatment]  
**Review Date**: [When to reassess]

## Risk Categories

**See PROFILE.md for business-specific risks.**

**Strategic**: Market changes, competition, business model
**Operational**: Process failures, resource constraints, technology
**Financial**: Revenue loss, cost overruns, cash flow
**Compliance**: Regulatory violations, legal issues
**Reputational**: Brand damage, client trust, public perception
**Technology**: Cybersecurity, data loss, system failures
**People**: Key person dependency, skills gaps

## Avoid

- **Risk Paranoia**: Every possibility → Focus on material risks above threshold
- **Analysis Paralysis**: Perfect assessment → Good-enough analysis, iterate
- **Static Register**: One-time exercise → Living document, regular reviews
- **No Ownership**: Everyone's problem → Clear accountability per risk

## Escalate When

- Critical or high risks identified requiring immediate attention
- Risks exceed acceptable appetite (see PROFILE.md)
- Resource constraints prevent adequate treatment
- Cross-functional coordination needed
- Insurance or legal expertise required
- Crisis management needed (risk materialized)
