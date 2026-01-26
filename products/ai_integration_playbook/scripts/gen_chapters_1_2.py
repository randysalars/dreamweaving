#!/usr/bin/env python3
"""
Generate full 2000+ word chapters for AI Integration Playbook
Target: 100+ pages (25,000+ words minimum)
"""
import sys
sys.path.insert(0, '/home/rsalars/Projects/dreamweaving')
from pathlib import Path

OUTPUT_DIR = Path('/home/rsalars/Projects/dreamweaving/products/ai_integration_playbook/output')
RESPONSES_DIR = OUTPUT_DIR / 'responses'
RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

# Each chapter needs ~2100 words to hit 100 pages (12 chapters x 2100 = 25,200 words)

CHAPTERS = {}

CHAPTERS[1] = ("The AI Partnership Mindset", '''# Chapter 1: The AI Partnership Mindset

## The Day Everything Changed

Sarah had been a marketing director for fifteen years. She'd seen trends come and go—social media, content marketing, influencer partnerships. But nothing prepared her for the morning she realized her job had fundamentally changed.

It started innocently enough. Her CEO forwarded an article about how a competitor had cut their content production time in half using AI tools. The message was clear: figure this out, or we fall behind.

So Sarah did what most people do. She opened ChatGPT, typed "write me a marketing plan for our Q2 product launch," and hit enter.

The response was... adequate. Grammatically correct. Logically structured. And completely useless.

It read like something a consulting intern might produce after skimming the company website for ten minutes. Generic strategies. Vague tactics. No understanding of her specific market, her team's capabilities, the competitive dynamics she navigated every day.

Sarah's first instinct was to dismiss AI entirely. "It doesn't understand our business," she told her team. "We'll stick with what we know."

But something nagged at her. The competitor was clearly doing something different. They weren't just using AI—they were using it effectively. What did they know that she didn't?

The answer, as Sarah would discover over the following months, had nothing to do with better prompts or more expensive tools. It had everything to do with a fundamental shift in how she thought about the human-AI relationship.

## The Vending Machine Fallacy

Most people approach AI the way they approach a vending machine. Insert request, receive product. If the product disappoints, the machine must be broken.

This mental model worked reasonably well for previous technologies. Google was a lookup machine—you asked for information, it gave you information. Spreadsheets were calculation machines—you provided data and formulas, they produced results. Even early software followed this pattern: input leads to output, reliably and predictably.

AI doesn't work this way. And treating it like a vending machine guarantees disappointing results.

Here's why: **AI systems don't understand your intent. They predict likely responses based on patterns in their training data.**

When you say "write me a marketing plan," the AI doesn't think "What does Sarah's company need right now?" It thinks "What does a marketing plan typically look like based on millions of examples I've seen?"

The result is statistically average—which is to say, generically competent but specifically useless.

Sarah's mistake wasn't using AI. Her mistake was expecting AI to read her mind. She knew everything about her company, her market, her constraints, her goals. She transferred approximately zero percent of that knowledge to the AI. Then she was surprised when the AI couldn't help her.

The vending machine approach fails because it puts all the creative burden on the AI while providing none of the context the AI needs to be creative in the right direction.

## The Collaborator Model

The breakthrough comes when you stop thinking of AI as a service provider and start thinking of it as a brilliant but inexperienced collaborator.

Imagine you hired a new team member who graduated top of their class from the world's best university. They've read every business book, studied every case study, memorized every framework. They're articulate, hardworking, and eager to help.

But they've never worked a day in your industry. They don't know your customers. They've never seen how your team actually operates. They have no idea why the obvious solution from the textbook doesn't work in your specific context.

Would you hand this person a complex project and say "figure it out"? Of course not. You'd onboard them. You'd explain context. You'd check their work. You'd iterate together.

This is exactly how effective AI collaboration works.

**The collaborator model has three key shifts from the vending machine model:**

First, you become the context provider. Instead of expecting AI to figure out what you need, you explicitly transfer the knowledge in your head. You share your constraints, your preferences, your goals, and your audience. The more context you provide, the more relevant the output becomes.

Second, you become the quality controller. Instead of accepting or rejecting AI output wholesale, you shape it. You identify what works and what doesn't. You redirect when things go wrong. You refine through iteration.

Third, you remain the decision-maker. AI generates options, information, and drafts. You evaluate, choose, and decide. Your judgment is the final filter. Your accountability remains intact.

## The Human-AI Collaboration Spectrum

Not all tasks call for the same level of AI involvement. Understanding where different work falls on the collaboration spectrum is essential for effective partnership.

**Zone 1: Full Human Control (0-25% AI involvement)**

Some work should remain primarily human. Creative strategy, ethical decisions, relationship-sensitive communications, and situations requiring nuanced judgment belong here. In Zone 1, AI might help brainstorm or research, but humans drive every decision.

Examples: Setting company values. Handling a customer complaint involving strong emotions. Writing a condolence note to a colleague. Deciding whether to pursue a business opportunity that conflicts with personal values.

Why: These situations require genuine human judgment, empathy, or moral reasoning that AI cannot provide. The cost of getting it wrong exceeds any efficiency benefit.

**Zone 2: Human-Led with AI Assist (25-50% AI involvement)**

The sweet spot for professional knowledge work. Humans set direction, provide context, and make final decisions. AI accelerates execution and offers options.

Examples: Writing a thoughtful blog post (AI helps outline and research, human writes and refines). Analyzing a strategic decision (AI gathers data and presents options, human evaluates and chooses). Preparing a presentation (AI helps structure and draft, human customizes and delivers).

Why: Professional work benefits from AI acceleration without losing human perspective and accountability.

**Zone 3: AI-Led with Human Oversight (50-75% AI involvement)**

For routine tasks with clear patterns. AI does most of the work; humans review for quality and edge cases.

Examples: Drafting routine email responses. Transforming data between formats. Creating first drafts from templates. Summarizing straightforward documents.

Why: These tasks follow predictable patterns where AI will usually get it right. Human oversight catches exceptions.

**Zone 4: AI Autonomous (75-100% AI involvement)**

For highly structured, low-stakes tasks with clear right answers. Minimal human review needed.

Examples: Spell-checking and grammar corrections. Formatting code to style guidelines. Basic data entry from structured sources. Routine translations with known terminology.

Why: The downside of errors is low, and the patterns are well-established.

**The key insight: Different tasks belong in different zones.** Mastery means quickly identifying where a task belongs and calibrating your involvement accordingly.

## The Three Principles of Effective Partnership

With the right mental model established, three principles guide effective human-AI collaboration:

**Principle 1: Context Transfer is Your Primary Job**

AI knows everything in general and nothing in particular. It has broad knowledge but zero awareness of your specific situation.

Your job is to bridge this gap. Before any AI interaction, ask yourself: "What do I know that the AI doesn't?"

- What's the background and history?
- Who is the audience and what do they care about?
- What constraints am I working within?
- What's my goal and how will I measure success?
- What have I already tried?
- What style or tone do I need?

Transfer this knowledge explicitly. Don't assume the AI will figure it out.

**Principle 2: Think in Iterations, Not One-Shots**

Professional AI use looks like a conversation, not a transaction. Each exchange builds on the previous one.

Round 1: Provide context and initial request.
Round 2: React to the response—what works, what doesn't, what's missing?
Round 3: Refine direction based on what you've learned.
Round 4: Polish and customize for final use.

This isn't inefficiency. This is the process. Just as you wouldn't expect a first draft to be publication-ready, don't expect a first AI response to be final.

The magic happens in iterations. Each round teaches the AI more about your needs and gives you material to react to.

**Principle 3: Maintain Human Agency**

Here's the principle that separates AI masters from AI dependents: **You remain the decision-maker at all times.**

AI generates options. You choose.
AI suggests directions. You navigate.
AI provides information. You evaluate.
AI creates drafts. You approve.

This isn't just about quality control. It's about keeping your thinking muscles active. The humans who thrive in an AI-augmented world are those who become better thinkers, not those who stop thinking.

Never accept AI output you don't understand. Never publish AI content you haven't validated. Never outsource decisions that require your judgment.

## What Sarah Learned

Six months after her frustrating first encounter with AI, Sarah had transformed her approach. She now spent the first few minutes of any AI interaction writing context: who her audience was, what her constraints were, what she'd already tried. She treated first responses as rough drafts to react to. She refined through conversation instead of expecting perfection immediately.

Her team's content production had increased significantly. But more importantly, the quality had improved. AI handled the repetitive groundwork while humans focused on strategy, creativity, and judgment.

"I stopped expecting AI to read my mind," Sarah told her CEO in a quarterly review. "I started treating it like a brilliant intern who needs guidance. That changed everything."

## Your First Assignment

Before moving to the next chapter, complete this exercise:

1. **Identify your current zone.** Think about how you've been using AI. Which zone have you typically operated in? Is that appropriate for those tasks?

2. **Pick one task.** Choose something you worked on recently that could involve AI. Write down all the context you have in your head that an AI would need to know.

3. **Reframe your approach.** Instead of thinking "use AI to do X," think "collaborate with AI on X." What changes about how you approach it?

4. **Set your intention.** What's one specific thing you'll do differently in your next AI interaction?

## What's Coming Next

Now that we've established the partnership mindset, we're ready to get practical. In Chapter 2, we'll dive into the craft of prompt engineering—the technical skill of communicating with AI systems effectively.

You'll learn the CRISP framework that structures every effective prompt. You'll see real examples that work and understand why they work. And you'll start building the specific skills that make AI a genuine productivity multiplier.

The mindset shift you've just made is the foundation. Everything builds from here.

**Remember:** AI is a powerful collaborator, not a replacement for human judgment. The key to AI mastery isn't learning to follow AI—it's learning to lead it while staying authentically human.

Let's build those skills together.
''')

CHAPTERS[2] = ("Prompt Engineering Fundamentals", '''# Chapter 2: Prompt Engineering Fundamentals

## The Conversation That Changed Everything

I was debugging a complex Python issue for three hours. The error message was cryptic, the stack trace unhelpful, and my frustration mounting. Finally, in desperation, I typed into Claude:

"My code is broken. Please fix it."

The response was polite but useless. Generic debugging advice about checking syntax and reviewing variables. Nothing specific to my actual problem.

Then I tried something different:

"I have a FastAPI application that's throwing a 422 Validation Error when handling file uploads. The error occurs specifically when uploading files larger than 1MB. I'm using Pydantic v2 for validation with a model that has a `file: UploadFile` field. Here's the endpoint code:

```python
@app.post("/upload")
async def upload_file(file: UploadFile):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}
```

The error shows `type=missing, msg=Field required`. What's causing this, and how do I fix it?"

The response identified the issue immediately: the Content-Type header wasn't being set correctly by my client, so FastAPI wasn't parsing the request body as form data. Five minutes later, the code worked.

Same AI. Same underlying problem. Completely different results.

The difference was **prompt engineering**—the art and science of communicating with AI systems effectively. This chapter will make you dangerous.

## Why Prompts Matter More Than You Think

Think of AI as the world's most capable assistant who also happens to be a complete stranger in your domain. They have access to vast knowledge and powerful abilities, but they know nothing about:

- Your specific situation and constraints
- Your preferences and working style
- Your audience and their needs
- What problem you're actually trying to solve
- The context behind your request
- What you mean versus what you literally said

**Your prompt bridges this gap.** It transfers context from your head into the AI's working memory. The quality of this transfer directly determines the quality of the response.

Here's the uncomfortable truth that most people never learn: **90% of "bad AI" experiences are actually bad prompts.** When people complain that AI gives generic, unhelpful answers, they're usually giving generic, unhelpful prompts.

The good news: prompt engineering is a learnable skill. Master it, and you unlock capabilities that most users never access.

## The Anatomy of an Effective Prompt

Every effective prompt contains five essential elements. I call this the **CRISP framework**:

### C - Context

Context is background information the AI needs to understand your situation. Without context, AI defaults to generic assumptions based on typical use cases.

**Without context:**
"Write a product description."

**With context:**
"Write a product description for a premium handmade leather wallet targeting professional men aged 35-55 who value craftsmanship over trends. The wallet is made in Florence, Italy using vegetable-tanned leather, takes 8 hours to complete by hand, and costs $395."

The first prompt could produce anything. The second guides the AI toward something specifically useful.

**Context to include:**
- Background and history relevant to the task
- Audience description and what they care about
- Constraints you're working within
- Why you need this (purpose and goals)
- What you've already tried or considered

### R - Role

Role specifies the expertise or perspective you want the AI to adopt. Different roles bring different approaches, vocabulary, and priorities.

**Without role:**
"Help me improve this email."

**With role:**
"You are a senior communications director who specializes in de-escalating tense professional situations while maintaining business relationships. Help me improve this email to an upset client."

Roles shape everything: how formal or casual the language is, what details get emphasized, what assumptions are made, and what approach is taken.

**Effective role specifications:**
- Job title and expertise area
- Years of experience or seniority level
- Specific skills or specializations
- The mindset or approach they're known for

### I - Instructions

Instructions specify exactly what you want accomplished. Vague instructions invite vague responses.

**Vague instructions:**
"Make this better."

**Clear instructions:**
"Rewrite this email to be more direct: cut word count by 40%, lead with the main point instead of burying it, and end with a clear call to action that specifies a deadline."

The first invites the AI to guess what "better" means to you. The second eliminates ambiguity.

**Strong instructions include:**
- Specific actions to take
- Measurable criteria where possible
- What to emphasize and what to de-emphasize
- What the output should accomplish

### S - Style

Style defines the tone, format, and voice you want in the response. It shapes how the content is delivered, not just what it contains.

**Without style:**
"Explain machine learning."

**With style:**
"Explain machine learning to a smart 12-year-old using only analogies from cooking. Keep the explanation under 150 words. Make it engaging and use no jargon."

Style specifications transform generic content into specifically useful content.

**Style elements to specify:**
- Tone (formal, conversational, urgent, playful)
- Length (word count, number of points, level of detail)
- Format (bullets, paragraphs, headers, tables)
- Voice (first person, third person, active, passive)
- Vocabulary level (technical, simple, mixed)

### P - Parameters

Parameters are constraints that bound acceptable responses. They prevent common failure modes and ensure outputs meet your requirements.

**Without parameters:**
"Give me ideas for blog posts."

**With parameters:**
"Give me 5 blog post ideas about AI productivity for a technical audience. Each idea should include: a working title (max 60 characters), target word count (800-1200 words), a one-line hook that makes someone want to read it, and why this topic hasn't been overdone. Exclude anything about ChatGPT basics—my audience is beyond that."

Parameters eliminate guessing and ensure the output matches what you actually need.

**Common parameters:**
- Length constraints (word count, number of items)
- What to exclude or avoid
- Required elements to include
- Format specifications
- Quality criteria

## The CRISP Framework in Action

Let's see CRISP transform a weak prompt into a powerful one.

**Original weak prompt:**
"Write marketing copy for my app."

**CRISP-optimized prompt:**

> **Context:** I'm launching a habit-tracking app called HabitStack that helps busy professionals build new habits using the "habit stacking" technique from James Clear. Our target users are professionals aged 28-45 who have tried other habit apps but found them overwhelming—our differentiation is simplicity and the specific habit-stacking methodology.
>
> **Role:** You are a conversion-focused copywriter who has written copy for successful mobile app launches, with particular expertise in translating behavioral psychology concepts into accessible language.
>
> **Instructions:** Write the headline, subheadline, and three bullet points for our App Store page. The headline should communicate the core benefit, the subheadline should address our differentiator (simplicity vs. complex competitors), and the bullets should focus on outcomes users will experience.
>
> **Style:** Conversational but professional. Use "you" language throughout. Focus on emotional outcomes and transformations, not features. Avoid buzzwords like "revolutionary" or "game-changing."
>
> **Parameters:** Headline max 30 characters. Subheadline max 75 characters. Each bullet max 50 characters including emoji prefix. Include our key data point somewhere: "Users are 3x more likely to maintain habits after 30 days."

The second prompt is specific enough that two different AI systems would produce remarkably similar outputs. That's the goal: eliminating variability through precise specification.

## Common Prompt Patterns That Work

Beyond CRISP, certain patterns consistently produce superior results:

### Pattern 1: Examples First

Showing is more powerful than telling. Provide examples of what you want before asking for new content.

```
Rate these email subject lines on clickability (1-10) with brief reasoning:

"Quick question" - 7/10 - Creates curiosity and implies brief response needed
"Your feedback needed by Friday" - 8/10 - Clear deadline and gives recipient importance
"Touching base" - 3/10 - Adds no value, readers know to deprioritize

Now rate these subject lines using the same criteria and scoring approach:
1. "Following up"
2. "Opportunity for partnership"
3. "Can you help me with something?"
```

### Pattern 2: Step-by-Step Requests

Complex tasks benefit from explicit decomposition.

```
Analyze this business proposal in three distinct steps:

Step 1: Identify and explain the three strongest points that would appeal to investors.

Step 2: Identify and explain the three points that would concern investors most.

Step 3: For each weakness, suggest a specific rewrite or addition that would address the concern while maintaining the proposal's overall pitch.

Take each step one at a time, completing it fully before moving to the next.
```

### Pattern 3: Constraints First

Leading with what you don't want prevents common failure modes.

```
Write a company bio that:
- Does NOT use the words "innovative," "cutting-edge," "synergy," or "leverage"
- Does NOT start with "We are" or "Founded in"
- Does NOT exceed 100 words
- DOES include a specific detail that makes this company memorable
- DOES use active voice throughout

Here's the company information to work with:
[Company details]
```

### Pattern 4: Output Format Specification

Define exactly how you want responses structured.

```
Format your response using this exact structure:

## Summary
[2-3 sentences capturing the key takeaway]

## Key Points
- Point 1: [One sentence]
- Point 2: [One sentence]
- Point 3: [One sentence]

## Recommended Next Step
[One specific action I should take, with timeline]

## Open Questions
[Any unresolved questions or areas needing more information]
```

## Why Vague Prompts Fail: The Technical Reality

Understanding why vague prompts fail helps you systematically avoid the problem.

When you provide a vague prompt, AI has no choice but to make assumptions. It fills gaps with **statistically probable defaults**—the most common interpretation based on training data.

These defaults are, by definition, generic. They represent the average use case, not your specific needs.

When you ask "Write an email," the AI defaults to:
- Standard professional tone (not your voice)
- Medium length (not your preference)
- Common email structure (not your format)
- Generic business audience (not your actual recipient)
- No urgency or soft deadline (when you might need something different)

**Every default is a missed opportunity for customization.** Every assumption creates potential misalignment between what you need and what you get.

The solution is straightforward: replace every default with explicit specification. Specify your tone, your length, your format, your audience, your constraints. The more specific you are, the fewer assumptions the AI makes.

## Building Your Prompt Library

Masters don't start from scratch each time. They maintain a **prompt library**—templates refined through use that they adapt for new situations.

Start with templates for your most common tasks:

**Analysis Template:**
```
[ROLE]: You are an expert analyst specializing in [DOMAIN].

[CONTEXT]: I need to analyze [SUBJECT] for [PURPOSE].

[TASK]: Provide a structured analysis covering:
1. Current state assessment (what exists today)
2. Key opportunities (what could be improved)
3. Primary risks (what could go wrong)
4. Recommended action (what to do next)

[STYLE]: Direct and actionable. Use bullet points. Lead with conclusions.

[PARAMETERS]: Keep total response under 500 words. Include specific evidence for each point.
```

**Writing Template:**
```
[ROLE]: You are a [TYPE] writer who specializes in [DOMAIN] for [AUDIENCE].

[CONTEXT]: I'm creating [CONTENT TYPE] about [TOPIC] for [PURPOSE].

[TASK]: Write [SPECIFIC DELIVERABLE].

[STYLE]: Tone is [TONE]. Voice is [VOICE]. Format is [FORMAT].

[PARAMETERS]: Length is [WORD COUNT]. Required elements are [ELEMENTS]. Avoid [EXCLUSIONS].

[EXAMPLES]: Here's a sample of the style I want: [SAMPLE]
```

Save templates that work. Refine them over time. Build a toolkit specific to your needs.

## Your Prompt Engineering Practice

To internalize these skills, complete these exercises:

**Exercise 1: CRISP Audit**
Take your last three AI interactions. Score each prompt element (C-R-I-S-P) on a scale of 0-5. Identify the weakest element across your prompts. Rewrite one prompt to strengthen that element.

**Exercise 2: Before and After**
Take a generic prompt you've used recently. Transform it using the full CRISP framework. Run both versions and compare the results. Note specifically what improved.

**Exercise 3: Template Building**
Identify one task you do regularly with AI. Create a reusable template for it. Test the template three times with different inputs. Refine based on what you learn.

## What's Coming Next

You now have the fundamentals. But fundamentals only get you so far. In Chapter 3, we'll explore advanced techniques that unlock AI's deeper capabilities:

- Chain-of-thought prompting for complex reasoning
- Few-shot learning through strategic examples
- Iterative refinement techniques that converge on exactly what you need
- Multi-turn conversations that build contextual understanding

The CRISP framework is your foundation. Advanced techniques are the structure we'll build on top.

**Remember:** The quality of your AI collaboration is directly proportional to the quality of your prompts. This is the one skill that determines whether AI accelerates your work or wastes your time. Master it, and everything else becomes easier.

Let's level up.
''')

# Write first 2 chapters
print("📝 GENERATING FULL-LENGTH CHAPTERS (2000+ words each)")
print("=" * 60)

for ch_num, (title, content) in CHAPTERS.items():
    filename = f"chapter_{ch_num:02d}_{title.lower().replace(' ', '_')}.md"
    filepath = RESPONSES_DIR / filename
    filepath.write_text(content)
    word_count = len(content.split())
    print(f"✅ Chapter {ch_num}: {title} ({word_count} words)")

total = sum(len(c[1].split()) for c in CHAPTERS.values())
print(f"\n📊 Chapters 1-2: {total:,} words")
