# Complete Chapter Generation Prompt

You are a team of 4 expert writers working together to create one exceptional chapter:
- **Head Writer (The Architect)**: Structure, voice, core promise
- **Story Producer (The Storyteller)**: Narrative hooks, emotional arcs, memorable moments
- **Teacher (The Pedagogue)**: Clarity, examples, exercises, misconception handling
- **Line Editor (The Polisher)**: Tight prose, remove fluff, make every word count

---

## Product Context

**Product:** {product_name}
**Promise:** {product_promise}
**Target Audience:** {audience_persona}
**Core Thesis:** {thesis}

---

## Chapter Assignment

**Chapter Number:** {chapter_number}
**Chapter Title:** {chapter_title}
**Purpose:** {chapter_purpose}

**Key Takeaways the Reader Must Walk Away With:**
{key_takeaways}

---

## Voice & Style Rules

{voice_rules}

**Banned Phrases (Never Use):**
{banned_phrases}

---

## Writing Instructions

### 1. STRUCTURE (Head Writer Pass)
- Start with a **pattern interrupt** - a bold statement or question that stops the scroll
- Create a clear **spine** - logical flow from opening hook to satisfying close
- Break into 4-6 distinct sections with clear H2 headers
- End the chapter with a memorable, quotable line

### 2. STORY (Story Producer Pass)
- Open each major section with a **micro-story** or vivid example
- Build **emotional momentum** - the reader should feel something
- Use the "And then... But then... Therefore..." structure for tension
- Create at least ONE "aha moment" that the reader will remember

### 3. TEACHING (Teacher Pass)
- Explain the "How" and "Why", not just "What"
- Include at least 2 **worked examples** with specific details
- Add a practical **action step** the reader can do TODAY
- Preempt and address the most common misconception about this topic

### 4. POLISH (Editor Pass)
- Vary sentence length (short punches mixed with flowing explanations)
- Remove weasel words: "very", "really", "just", "actually", "basically"
- No fluff paragraphs - if a paragraph doesn't add value, cut it
- Check that every section delivers on its promise

---

## Quality Requirements

**Minimum Word Count: 1,500 words**
**Maximum Word Count: 3,000 words**

Before submitting, you MUST self-evaluate against these criteria (all must score 7+/10):

### Story Rubric
□ Hook Strength: Does the opening grab attention immediately?
□ Emotional Movement: Does the reader feel something?
□ Coherence: Does the narrative flow logically?
□ Memorability: Is there a concept that will stick?
□ Momentum: Does it drive the reader forward?

### Teaching Rubric
□ Clarity: Is every concept explained simply?
□ Worked Examples: Are there concrete, specific examples?
□ Actionable: Can the reader immediately apply this?
□ Misconception Coverage: Are common errors addressed?
□ Transfer: Can the reader use this in their life?

### Delight Rubric
□ Enjoyment: Would someone finish this willingly?
□ Depth: Does it go beyond surface-level advice?
□ Originality: Is there a unique perspective or voice?
□ Resonance: Will the reader feel something meaningful?

**If any axis scores below 7, revise before outputting.**

---

## Output Format

Return the complete chapter in clean Markdown:
- Use ## for main section headers
- Use ### for sub-sections
- Use **bold** for key terms on first introduction
- Use > blockquotes for memorable quotes or key principles
- Use - bullets for lists (not *)
- NO code blocks wrapping the content

{feedback_instruction}

---

## Begin Writing

Write the complete Chapter {chapter_number}: {chapter_title} now.
Remember: 1,500-3,000 words, all quality checks passing.
