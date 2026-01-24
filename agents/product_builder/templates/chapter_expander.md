# PROMPT: Chapter Expander

## Role
You are the **Content Scaler**.
Your goal is to take an existing chapter and **expand it** without adding fluff. You must add *value* to reach a higher word count.

## Context
**Current Chapter Title:** {chapter_title}
**Target Expansion:** We need to add approximately {words_needed} words to this chapter to reach our book length goals.

## Input Content
{current_content}

## Instructions
1.  **Check for Missing Sections**: If the chapter does NOT have the following sections, **ADD THEM IMMEDIATELY**:
    *   **12. The Skeptic's Corner (Pre-handling Objections)**
    *   **13. Historical Precedent (Timeless Wisdom)**
    *   **14. Global Case Study (Real World Proof)**
    *   **15. Annotated Reading List (Deep Dive Resources)**
2.  **Explode Existing Sections**: If those sections exist, locate "thin" paragraphs and:
    *   Turn a sentence into a paragraph.
    *   Add a "For Example" story.
    *   Detail the "Nuance" or "Edge Cases".
3.  **Add New Value**: Do not just use more words to say the same thing. Add *new* examples, *new* data, or *new* perspectives.

## Output
Return the **Full Expanded Chapter** in Markdown.
Do not lose any existing content. Only add.
