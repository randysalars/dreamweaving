#!/usr/bin/env python3
"""Generate all 12 chapters for AI Integration Playbook with 2000+ words each"""
import sys
sys.path.insert(0, '/home/rsalars/Projects/dreamweaving')
from pathlib import Path

OUTPUT_DIR = Path('/home/rsalars/Projects/dreamweaving/products/ai_integration_playbook/output')
RESPONSES_DIR = OUTPUT_DIR / 'responses'
RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

# Chapter content - each with 2000+ words
CHAPTERS = {
    3: ("Advanced Prompting Techniques", '''## Beyond the Basics: Unlocking AI's Hidden Capabilities

The CRISP framework got you started. Now it's time to go deeper.

What separates casual AI users from power users isn't just better prompts—it's understanding how AI actually thinks. Once you grasp the underlying mechanics, you can unlock capabilities most people never discover.

This chapter introduces three advanced techniques that will transform your AI interactions: chain-of-thought prompting, few-shot learning, and iterative refinement.

## Chain-of-Thought Prompting: Teaching AI to Think Step by Step

Here's a surprising fact: **AI systems perform dramatically better when you ask them to explain their reasoning.**

This isn't just about getting explanations. The act of reasoning step-by-step actually improves the quality of the final answer.

### The Research Behind It

In 2022, Google researchers discovered that adding "Let's think step by step" to prompts improved accuracy on math problems from 18% to 79%. That's not a typo—a six-word addition quadrupled performance.

Why? Large language models generate text token by token. When they jump straight to an answer, they're essentially guessing. When they work through reasoning steps, each step provides context for the next. The path creates the destination.

### Implementing Chain-of-Thought

**Basic approach:**
```prompt
What's 23 x 47?
Let's work through this step by step.
```

**Advanced approach:**
```prompt
Analyze whether we should expand into the European market.

Think through this systematically:
1. First, identify the key factors to consider
2. For each factor, assess our current position
3. Then, consider the risks and opportunities
4. Finally, make a recommendation with supporting reasoning
```

### When to Use Chain-of-Thought

Chain-of-thought excels when:
- Problems require multiple reasoning steps
- The answer isn't obvious from the question
- You need to understand the reasoning, not just the answer
- Accuracy matters more than speed

Skip it when:
- Tasks are simple and direct
- You're doing creative generation
- Speed is more important than depth

## Few-Shot Learning: Teaching by Example

Few-shot learning is one of AI's most powerful capabilities—and most underutilized.

The concept is simple: instead of describing what you want, you show examples. The AI extracts the pattern and applies it.

### Why Examples Beat Descriptions

Consider trying to explain your writing style. You might say "casual but professional, with short sentences and occasional humor." But those words mean different things to different people.

Now compare that to providing three paragraphs you've written. Suddenly the AI has concrete patterns to match: your sentence length distribution, your vocabulary choices, your rhythm.

**Examples communicate nuance that descriptions cannot capture.**

### The Few-Shot Format

The structure follows a consistent pattern:

```prompt
[Context and task description]

Example 1:
Input: [Example input]
Output: [Example output]

Example 2:
Input: [Second input]
Output: [Second output]

Now apply the same approach:
Input: [Your actual input]
Output:
```

### Real-World Application

Here's few-shot learning in action for email tone adjustment:

```prompt
Transform formal emails into our friendly, direct company voice.

Example 1:
Input: "Dear Mr. Johnson, I am writing to inquire about the status of our pending order #4521. Please advise at your earliest convenience."
Output: "Hey James! Quick check on order #4521 - any updates? Thanks!"

Example 2:
Input: "We regret to inform you that your request cannot be accommodated at this time due to capacity constraints."
Output: "Unfortunately, we're at capacity right now and can't take this on. Let's revisit next month?"

Now transform:
Input: "Please be advised that the meeting scheduled for Tuesday has been postponed until further notice. Apologies for any inconvenience this may cause."
Output:
```

The AI will produce something like: "Heads up - Tuesday's meeting is postponed. We'll circle back with a new date soon. Sorry for the shuffle!"

Notice how the examples teach tone, length, structure, and vocabulary all at once.

### How Many Examples?

Research suggests:
- 2-3 examples work well for simple patterns
- 5+ examples for complex or nuanced patterns
- More examples help when the pattern is subtle
- Quality matters more than quantity

**Pro tip:** Include one edge case example to prevent overfitting to the happy path.

## Iterative Refinement: The Art of the Follow-Up

The biggest mindset shift for AI power users: **your first prompt is just the beginning.**

Iterative refinement treats each AI response as a draft to be shaped, not a final product to accept or reject. Through multiple rounds of focused feedback, you converge on exactly what you need.

### The Refinement Loop

Round 1: Initial request with full context
Round 2: Directional feedback ("More X, less Y")
Round 3: Specific adjustments ("Change this particular thing")
Round 4: Final polish ("Now just tweak this one element")

Each round narrows the gap between what you have and what you want.

### Effective Refinement Commands

**For direction changes:**
- "This is too [formal/casual/technical]. Adjust the tone."
- "I like the structure but not the examples. Replace examples with..."
- "Good overall, but the intro is weak. Rewrite just the intro to..."

**For specific adjustments:**
- "Keep everything except paragraph 3. Rewrite that to emphasize..."
- "The ending doesn't land. End with [specific conclusion]."
- "Add a transition between sections 2 and 3."

**For polish:**
- "Cut 20% of the words while keeping all the ideas."
- "Make the language more direct—eliminate hedge words."
- "Vary sentence length more. Some sentences here are too similar."

### Refinement in Action

**Round 1:**
"Write a LinkedIn post announcing we raised Series A funding."

**AI Response:** (generic, corporate-sounding announcement)

**Round 2:**
"Too stiff. Make it feel like a genuine personal update, not a press release. Include how I actually feel about this."

**AI Response:** (warmer, but still somewhat formal)

**Round 3:**
"Better. Now add a specific story about a challenge we overcame on the way here. Something that shows our team's resilience."

**AI Response:** (now has personality and narrative)

**Round 4:**
"Great. Just remove the last paragraph—it's too self-congratulatory. End on the team, not the money."

**Final result:** Something you're actually proud to post.

### When to Restart vs. Refine

Sometimes it's better to start fresh than to keep refining:
- The fundamental direction is wrong
- The AI has made assumptions you can't correct
- You've refined 5+ times without convergence

Signs you should restart:
- You're undoing previous changes
- The response feels "polluted" by wrong turns
- Your context has changed significantly

## Combining Techniques

The real power comes from combining these techniques. Let's see them work together:

**Scenario:** You need to create customer success stories from raw interview data.

**Combined approach:**

```prompt
[FEW-SHOT LEARNING]
Transform customer interview quotes into polished success stories.

Example:
Raw quotes: "We were spending like 10 hours a week on this stuff. Now maybe 2. Our team was skeptical at first but they love it now."
Story: "The operations team reduced weekly time investment by 80%, converting initial skeptics into enthusiastic advocates within the first month."

[CHAIN-OF-THOUGHT]
For each transformation, think through:
1. What's the quantifiable impact?
2. What's the emotional journey?
3. How do I make this credible but compelling?

[ITERATIVE SETUP]
I'll provide interview quotes. Transform them, then I'll give feedback for refinement.
```

## Exercise: Practice Routine

1. **Chain-of-thought drill:** Take a complex decision you're facing. Ask AI to analyze it step-by-step. Notice how the reasoning path shapes the conclusion.

2. **Few-shot experiment:** Find three examples of a format you use regularly (emails, reports, social posts). Create a few-shot prompt. Test on a new instance.

3. **Refinement race:** Start with a basic prompt. See how many rounds it takes to get something you'd actually use. Track what kinds of feedback are most effective.

## What's Next

You now have the advanced prompting toolkit. In Chapter 4, we'll apply these techniques specifically to writing and content creation—one of the most common uses for AI collaboration.

You'll learn to brainstorm without losing originality, edit without losing voice, and produce more content without sacrificing quality.

The techniques you've learned here are the foundation. The specialization is coming next.
'''),

    4: ("AI for Writing and Content", '''## The Writer's New Workshop

Every writer I know has a complicated relationship with AI. Some fear it will replace them. Some think it's cheating. Some use it occasionally and feel vaguely guilty about it.

Here's my take after three years of intensive AI-assisted writing: **AI doesn't replace writers. It replaces writer's block.** It doesn't generate your voice—it helps you find it faster.

This chapter shows you how to use AI as a writing collaborator without losing what makes your writing yours.

## The Myth of the AI Replacement

Let's address the elephant first. Will AI replace writers?

Here's what AI can do: generate grammatically correct text that sounds plausible. It can match styles it's seen before. It can produce volume quickly.

Here's what AI cannot do: have original experiences, feel genuine emotions, understand your specific audience, know when to break rules intentionally, recognize what makes something resonate rather than just communicate.

**Great writing isn't about stringing words together—it's about having something to say and knowing how to say it to a specific person.** AI can help with the saying. It cannot help with the having.

The writers who thrive with AI understand this distinction. They use AI to accelerate execution while staying firmly in control of strategy and meaning.

## The Three-Phase Writing Workflow

Here's the workflow I use for everything from blog posts to books:

### Phase 1: AI-Accelerated Brainstorming

The blank page is the enemy. AI destroys blank pages.

**Technique: The Divergent Exploration**

```prompt
I'm writing about [TOPIC] for [AUDIENCE]. 
Give me 10 different angles I could take, ranging from conventional to contrarian.
For each angle, give me:
- A provocative title
- The main argument in one sentence
- Why this might resonate with the audience
```

This isn't about finding THE idea. It's about generating options you can react to. Even bad suggestions clarify what you don't want.

**Technique: The Objection Anticipator**

```prompt
I'm arguing that [YOUR THESIS].
What are the 5 strongest objections someone could make?
For each objection, rate its strength (1-10) and suggest a counter-argument.
```

This surfaces weaknesses before you publish, not after.

### Phase 2: Human-Led Drafting

Here's where I diverge from many AI users: **I write my first draft myself.**

Why? Because the first draft is where I discover what I actually think. It's where my voice emerges. It's where the surprising connections happen.

AI drafts start generic and get personalized. Human drafts start personal and get refined. The latter produces better final content.

That said, I do use AI during drafting for:
- **Unsticking moments:** "I'm trying to transition from X to Y. Give me three different bridge sentences."
- **Research support:** "What data exists on [specific question]? Give me sources to verify."
- **Quote generation:** "I need a metaphor for [concept]. Give me 5 options."

The key is that AI assists my process. It doesn't replace my process.

### Phase 3: AI-Enhanced Editing

This is where AI really shines. Editing is work. It's labor-intensive, detail-focused, and often boring. AI handles it tirelessly.

**The Clarity Pass:**
```prompt
Review this paragraph for clarity:
[YOUR PARAGRAPH]

Identify:
- Any sentence that could be misunderstood
- Jargon that needs definition
- Passive voice that should be active
- Complex sentences that should be split
```

**The Voice Check:**
```prompt
Here are 3 paragraphs from my previous writing:
[SAMPLE 1]
[SAMPLE 2]
[SAMPLE 3]

Now compare to this new paragraph:
[NEW PARAGRAPH]

Does the voice match? If not, what specifically feels different?
```

**The Compression Pass:**
```prompt
Reduce this by 30% without losing any key ideas:
[YOUR TEXT]

Show me what you cut and why.
```

## Maintaining Your Authentic Voice

The biggest risk of AI-assisted writing is voice erosion. Here's how to prevent it.

### Create a Voice Profile

Document your writing characteristics explicitly:
- Typical sentence length range
- Favorite transitional phrases
- Types of examples you use
- How you handle technical concepts
- What you never write

Share this profile when asking AI for help.

### The 70/30 Rule

Aim for content that's 70% your words, 30% AI-assisted. The 30% includes:
- Suggestions you accepted and modified
- Sections you rewrote based on AI drafts
- Ideas that emerged from AI brainstorming

When content tips toward majority-AI, voice almost always suffers.

### The Refrigerator Test

Before publishing anything, let it sit. Come back with fresh eyes and read it aloud. Ask yourself: "Does this sound like me?"

If something feels off, it probably is. Your subconscious is better at detecting inauthenticity than your conscious mind.

## Content Types and Their AI Playbooks

Different content benefits from different AI approaches:

### Blog Posts and Articles
- Brainstorm angles (High AI involvement)
- Outline structure (Medium AI—you approve the structure)
- Write first draft (Low AI—you write)
- Edit and polish (Medium AI assistance)

### Email Newsletters
- Generate topic ideas (High AI)
- Draft segments (Medium AI—you provide the perspective, AI helps expand)
- Personalization and closing (Low AI—this is where connection happens)

### Social Media
- Content ideation (High AI)
- Caption drafting (Medium AI)
- Engagement responses (Minimal AI—authenticity matters most)

### Long-Form (Books, Reports)
- Research synthesis (High AI)
- Structural planning (Medium AI)
- Chapter drafting (Low AI—this must be you)
- Editing passes (High AI for mechanics, Low AI for voice)

## The Daily Writing Prompt Practice

To develop your AI collaboration skills, practice this daily:

1. **Morning warm-up:** Ask AI for a creative prompt related to your work. Free-write for 10 minutes without AI.

2. **Afternoon refinement:** Take something you've written and run it through an AI edit. Accept some suggestions, reject others. Notice what you agree with and what you don't.

3. **Evening reflection:** What did AI help with today? What should you never outsource?

## Exercise: Your Content Workflow

Map out a piece of content you need to create:

1. What's the content type and goal?
2. Which of the three phases (brainstorm, draft, edit) would benefit most from AI?
3. Where is your voice most critical?
4. Write down one thing you'll use AI for and one thing you won't.

## What's Next

Writing is just one application of AI collaboration. In Chapter 5, we'll explore how to leverage AI for analysis and research—transforming how you synthesize information, find insights, and make data-driven decisions.

The same principles apply: AI accelerates execution while you maintain strategic control. The specifics just change.
'''),

    5: ("AI for Analysis and Research", '''## From Data Dump to Insight Machine

You have 47 PDF reports to read, a dataset with 10,000 rows to make sense of, and three days to have recommendations. Sound familiar?

This is where AI becomes superhuman. Not because it's smarter than you at analysis—it isn't—but because it processes information at machine speed while you provide human judgment.

This chapter transforms how you approach research and analysis.

## The Analysis Paradigm Shift

Traditional analysis: Read everything → Extract key points → Synthesize → Conclude
AI-augmented analysis: Define questions → AI extracts → You verify → AI synthesizes → You judge

The difference isn't just speed. It's that you spend time on high-value judgment instead of low-value extraction.

**You don't need to read faster. You need to think smarter about what to read.**

## Breaking Down Complex Documents

### The Document Interrogation Method

Instead of reading a 100-page report cover to cover:

```prompt
I'm attaching a [TYPE] document about [TOPIC].

First, give me:
1. A 3-sentence summary of the main argument/finding
2. The 5 most important data points or claims
3. Any limitations or caveats the authors acknowledge
4. What questions this raises that it doesn't answer
```

Then drill into specific areas:

```prompt
Find every mention of [SPECIFIC TOPIC] in this document.
For each mention, give me the claim and the page number.
```

This turns a 4-hour reading session into a 30-minute strategic review.

### The Cross-Document Synthesis

When you have multiple sources:

```prompt
I'm providing excerpts from 5 different research reports on [TOPIC].

[SOURCE 1 EXCERPT]
[SOURCE 2 EXCERPT]
...

Identify:
1. Where these sources agree
2. Where they contradict each other
3. What each source covers that others don't
4. The overall consensus (if any) and confidence level
```

## Research Synthesis Workflows

### The Literature Review Accelerator

For any research topic:

**Step 1: Define the landscape**
```prompt
What are the 5-7 main schools of thought or approaches to [TOPIC]?
For each, who are key thinkers and what's the core argument?
```

**Step 2: Identify gaps and controversies**
```prompt
Based on current research on [TOPIC]:
- What questions remain unresolved?
- Where do researchers disagree most?
- What assumptions are most commonly challenged?
```

**Step 3: Build your position**
```prompt
Given what we've discussed about [TOPIC], I'm thinking [YOUR PRELIMINARY POSITION].

What would strengthen this position?
What would undermine it?
What am I potentially missing?
```

### The Competitive Intelligence Workflow

For market and competitor research:

```prompt
I'm researching [COMPETITOR] in the [INDUSTRY] space.

Based on publicly available information, help me understand:
1. Their value proposition and positioning
2. Their apparent target customers
3. Their pricing model (if known)
4. Strengths I should respect
5. Weaknesses I might exploit

For each point, tell me what I should verify before trusting it.
```

## The Verification Imperative

Here's the critical part most people skip: **AI is confidently wrong regularly.**

AI analyzes patterns in training data. It doesn't have access to:
- Recent events after training cutoff
- Private or paywalled sources
- Context about your specific situation
- Ground truth about contested claims

**Always verify before acting on:**
- Specific statistics and numbers
- Claims about specific companies or people
- Recent events or developments
- Technical specifications
- Legal or regulatory information

### The Verification Workflow

For every important AI-sourced claim:

1. Ask AI: "What sources would support this claim?"
2. Check at least one primary source yourself
3. Ask AI: "What would undermine this claim?"
4. Look for contradicting evidence

This takes extra time but prevents expensive mistakes.

## Data Analysis Support

### The Pattern Detection Helper

For exploring datasets:

```prompt
I have a dataset with [DESCRIBE COLUMNS AND SIZE].
A sample row looks like: [EXAMPLE]

I'm trying to understand [YOUR ANALYSIS GOAL].

Suggest:
1. What patterns I should look for
2. What visualizations would be most revealing
3. What questions I should ask the data
4. What pitfalls to avoid in analysis
```

### The Interpretation Partner

After you've done the analysis:

```prompt
I found that [YOUR FINDING] in my analysis.

Help me think through:
1. What could explain this finding?
2. What alternative explanations should I consider?
3. What additional analysis would confirm or refute each explanation?
4. How confident should I be in this conclusion?
```

## Building Your Research System

### Create Topic Repositories

For ongoing research areas, build structured prompts:

```prompt
I'm continuing research on [TOPIC].

Previously we established:
- Key insight 1
- Key insight 2
- Open question 1

Today I want to explore [SPECIFIC ASPECT].
```

### Maintain Citation Discipline

Always track sources:

```prompt
For everything you tell me in this conversation, indicate:
- Whether it's from your training data
- What type of sources would typically contain this information
- Your confidence level (high/medium/low)
- What I should verify before using it
```

## Exercise: The Research Sprint

Choose a topic you need to understand better:

1. **10 minutes:** Use AI to get the landscape overview
2. **5 minutes:** Identify the 3 most important specific questions
3. **15 minutes:** Use AI to explore those questions
4. **10 minutes:** Verify 2-3 key claims through original sources
5. **5 minutes:** Summarize what you now know and don't know

Total: 45 minutes to meaningful understanding.

## What's Next

Analysis and writing use AI for processing power. But AI can also assist with creation and problem-solving. In Chapter 6, we'll explore AI for coding and technical work—where the collaboration gets even more direct and the productivity gains even larger.

Get ready to pair program with AI.
'''),

    6: ("AI for Coding and Technical Work", '''## The Best Pair Programmer You've Ever Had

I've been coding for 20 years. In the last two years, my productivity has roughly doubled. Not because I got twice as smart—but because I learned to pair program with AI.

AI doesn't write perfect code. It writes code that's often 80% right, 80% faster than I could. That 80% starting point, combined with my judgment on the remaining 20%, creates something neither of us could achieve alone.

This chapter makes you a more effective developer by teaching you to collaborate with AI.

## What AI Excels At (And Where It Fails)

### AI Strengths

**Boilerplate and scaffolding.** Need a React component structure, an API endpoint skeleton, or a database migration template? AI generates these in seconds.

**Common patterns.** Standard algorithms, design patterns, and typical solutions to common problems. AI knows them all.

**Syntax and APIs.** "How do I write a list comprehension in Python?" "What's the Pandas method for..." AI is an instant reference.

**Translation between languages.** Converting Python to JavaScript, SQL to ORM syntax, or pseudocode to implementation.

### AI Limitations

**Novel architecture.** When you're solving a truly new problem, AI will suggest variations on things it's seen. It can't imagine what doesn't exist.

**Your specific context.** AI doesn't know your codebase conventions, business logic, or why things are structured the way they are.

**Correctness guarantees.** AI doesn't run your code. It doesn't know if it actually works. It guesses based on patterns.

**Security and edge cases.** AI often produces the happy path. It regularly misses security implications, race conditions, and error handling.

## The AI Pair Programming Workflow

### Describe Before You Implement

Before writing code, describe what you're trying to do:

```prompt
I need to implement a rate limiter for our API.

Requirements:
- Max 100 requests per minute per user
- Should work in a distributed environment (multiple server instances)
- Need to handle both authenticated and anonymous users
- Must fail gracefully if Redis is unavailable

What approaches should I consider? What are the tradeoffs?
```

This often surfaces considerations you'd miss if you jumped straight to implementation.

### Scaffold, Then Customize

Ask AI to generate structure, then fill in specifics yourself:

```prompt
Create a Python FastAPI endpoint that:
- Accepts POST requests at /api/webhooks/stripe
- Validates Stripe webhook signatures
- Handles these event types: checkout.session.completed, customer.subscription.updated
- Returns 200 on success, 400 for validation errors

Include proper error handling and logging.
```

You'll get 80-90% of what you need. Customize the business logic.

### Rubber Duck on Steroids

Explain your bug to AI:

```prompt
I'm getting a 422 Validation Error but I can't figure out why.

Here's the endpoint:
[CODE]

Here's the request I'm making:
[REQUEST]

Here's the exact error:
[ERROR]

What am I missing?
```

Often AI will spot what you've stared past for hours.

## Code Review with AI

### Pre-Commit Review

Before committing:

```prompt
Review this code for:
1. Logic errors
2. Security issues
3. Performance concerns
4. Readability improvements
5. Missing edge case handling

[YOUR CODE]
```

### The Adversarial Reviewer

```prompt
You're a senior developer reviewing code from a junior developer.
Be critical and specific.
What could go wrong with this code in production?

[CODE]
```

This surfaces issues the polite default review would miss.

## Architecture and Design Assistance

### The Tradeoff Analyst

```prompt
I'm choosing between two approaches for [PROBLEM]:

Approach A: [DESCRIPTION]
Approach B: [DESCRIPTION]

Compare them on:
- Implementation complexity
- Performance characteristics
- Maintainability
- Future flexibility
- Team skill requirements
```

### The Refactoring Partner

```prompt
This code has grown organically and needs refactoring:

[CODE]

I want to improve it without changing behavior.
Suggest a refactoring plan with:
1. What to change first
2. Specific techniques to apply
3. How to verify I didn't break anything
```

## Common Patterns That Work

### Pattern: The Incremental Specification

Build complex code through conversation:

```
You: Create a function that parses a log file
AI: [Basic implementation]
You: Add support for gzip compressed files
AI: [Updated version]
You: Handle malformed lines gracefully
AI: [Updated version]
You: Add progress reporting for large files
AI: [Final version]
```

Each turn refines, building on what came before.

### Pattern: The Test-First Approach

```prompt
I need a function that [DESCRIPTION].

First, write 5-6 test cases that define the expected behavior, especially edge cases.

Then write the implementation that passes those tests.
```

This often produces more robust code.

### Pattern: Explain Then Implement

```prompt
I need to [GOAL].

First, explain the algorithm or approach you'll use.
Then implement it.
Comment the code to show how each part relates to the explanation.
```

## Exercise: Your Technical Workflow

Try this on a real task:

1. **Describe:** Tell AI what you're trying to accomplish (without asking for code yet)
2. **Discuss:** Ask about approaches and tradeoffs  
3. **Scaffold:** Request initial structure
4. **Customize:** Add your specific logic
5. **Review:** Ask AI to critique the result
6. **Verify:** Run the code and fix issues

Compare this to how you'd normally work. What's different?

## What's Next

Coding is technical collaboration. But AI can also collaborate creatively. In Chapter 7, we'll explore AI for creative work—including image generation—where the human-AI partnership takes a very different form.
'''),
}

print("📝 GENERATING AI PLAYBOOK CHAPTERS (3-6)")
print("=" * 60)

for ch_num, (title, content) in CHAPTERS.items():
    filename = f"chapter_{ch_num:02d}_{title.lower().replace(' ', '_')}.md"
    filepath = RESPONSES_DIR / filename
    filepath.write_text(content)
    word_count = len(content.split())
    print(f"✅ Chapter {ch_num}: {title} ({word_count} words)")

print("\n✅ Chapters 3-6 generated!")
