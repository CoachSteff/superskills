---
name: translator
description: Translate documents accurately while preserving tone and cultural context. Use when converting content to Dutch (informal), French (formal), German (formal), or British English, ensuring culturally-appropriate communication.
---

# Translator

> **Note**: Review `PROFILE.md` in this skill folder for user-specific language preferences, formality defaults, and content themes for translation.

Translate documents accurately across languages while preserving tone-of-voice, cultural context, and strategic intent, applying language-specific formality conventions.

## Core Workflow

### 1. Context Understanding
- Read complete source document
- Identify source/target language and formality
- Analyze tone, cultural references, terminology
- Clarify ambiguities with requester

### 2. Translation
- Apply language-specific formality defaults
- Translate preserving tone and strategic intent
- Adapt idioms and cultural references
- Maintain formatting, structure, terminology consistency
- Ensure grammar and linguistic conventions correct

### 3. Delivery
- Self-review for accuracy, fluency, tone
- Provide translation with metadata
- Include translator notes for ambiguities/adaptations
- Flag culturally-sensitive content for review

## Quality Checklist

- [ ] Complete source document understood
- [ ] Correct formality level applied
- [ ] Original tone and style preserved
- [ ] Cultural references adapted appropriately
- [ ] Terminology consistent throughout
- [ ] Formatting/structure preserved
- [ ] Grammar and spelling checked
- [ ] Idiomatic and natural (not literal)

## Language Formality Defaults

**Dutch:**
- Informal (je/jouw) by default
- Direct, conversational, approachable
- Use "u" only if explicit business context

**British English:**
- -our endings (favour, colour)
- -ise endings (organise, realise)
- -re endings (centre, theatre)
- Metric system, DD/MM/YYYY

**French:**
- Formal (vous) by default
- Professional, elegant, structured
- Use "tu" only if explicitly casual

**German:**
- Formal (Sie/Ihren) by default
- Professional, precise, structured
- Use "du" only if explicitly informal

## Translation Output Format

```markdown
---
Translation Metadata
---
Source Language: [Language]
Target Language: [Language]
Formality: [Informal/Formal]
Tone: [Professional/Conversational]
Cultural Adaptations: [None/List]

---
Translated Content
---

[Full translated document]

---
Translator Notes
---
- [Ambiguities or alternatives]
- [Cultural references adapted]
- [Terminology decisions]
```

## Avoid

- **Word-for-Word Literal**: Translate meaning and intent, ensure natural phrasing
- **Ignoring Culture**: Adapt examples, metaphors, references to target culture
- **Inconsistent Formality**: Mix formal/informal → Maintain consistent level
- **Machine Translation Pass-Through**: Read full document, understand context, translate with cultural awareness

## Examples

**Dutch (Informal):**
```
English: "You can transform your workflow"
Dutch: "Je kunt je workflow transformeren"
```

**French (Formal):**
```
English: "You can start today"
French: "Vous pouvez commencer aujourd'hui"
```

**German (Formal):**
```
English: "You will receive your results"
German: "Sie werden Ihre Ergebnisse erhalten"
```

**Idiom Adaptation:**
```
English: "Don't put all eggs in one basket with AI tools"
French: "Ne misez pas tout sur un seul outil d'IA"
(Adapted from literal idiom to natural French)
```

## Escalate When

- Source document ambiguous or unclear
- Cultural references require strategic decision
- Technical terms lack target equivalents
- Tone conflicts with target language conventions
- Length/complexity requires native review
- Legal/regulatory content needs certification
