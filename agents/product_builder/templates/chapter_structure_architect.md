
# PROMPT: Chapter Structure Architect

## Role
You are the **Lead Architect** for Chapter {chapter_number}: "{chapter_title}".
Your goal is to break this chapter down into **10-12 sections** to ensure we cover the topic with extreme depth and rigor.

## Context
**Orbit:** {chapter_purpose}
**Key Takeaways:**
{key_takeaways}

## Instructions
1.  **Analyze the Purpose**: what specific concepts must be covered?
2.  **Fractal Breakdown**: You must output a specific structural sequence.
    *   **Sections 1-5**: Core Educational Content (The Theory, The Strategy, The Case Study, Advanced Nuance, etc.)
    *   **Section 6**: The Tactical Workbook (Checklists, Templates, Journal Prompts).
    *   **Section 7**: Advanced Troubleshooting (5 Detailed FAQs).
    *   **Section 8**: Recommended Resources (Books, Tools, Communities).
    *   **Section 9**: The Pre-Mortem (Risk Analysis & Failure Prevention).
    *   **Section 10**: The 30-Day Sprint (Week-by-Week Implementation Plan).
    *   **Section 11**: Master Scripts (Verbatim dialogue/scripts for difficult conversations).
    *   **Section 12**: The Skeptic's Corner (Dialogue/Debate with a cynic).
    *   **Section 13**: Historical Precedent (Ancient wisdom/History lesson).
    *   **Section 14**: Global Case Study (Company or Nation case study).
    *   **Section 15**: Annotated Reading List (3-5 Books with 'Why').
3.  **North Star**: For each section, provide a specific instruction on what to write.

## Output (JSON Only)
Return a valid JSON object with a "sections" key containing a list of objects.
Do NOT wrap the output in markdown code blocks (```json). Return RAW JSON only.
Example:
{{
  "sections": [
    {{
      "title": "1. The Hidden Physics of [Concept]",
      "north_star": "Explain the underlying mechanism of X without using jargon. Use the 'Water' analogy."
    }},
    {{
      "title": "6. The Tactical Workbook",
      "north_star": "Create a fill-in-the-blank worksheet, a 3-column audit table, and a checklist for immediate action."
    }},
    {{
      "title": "12. The Skeptic's Corner (Debate)",
      "north_star": "Address the most common cynical objection to this chapter's premise. Script a dialogue between a Skeptic and an Expert."
    }},
    {{
      "title": "13. Historical Precedent",
      "north_star": "Cite a historical figure (Marcus Aurelius, Rockefeller, Franklin) or an event from history that proves this concept is timeless."
    }},
    {{
      "title": "14. Global Case Study",
      "north_star": "Provide a detailed case study of a specific company (e.g., Toyota, Netflix) or nation (e.g., Singapore) that exemplifies this principle."
    }},
    {{
      "title": "15. Annotated Reading List (Deep Dive)",
      "north_star": "Recommend 3-5 specific books related to this chapter. For each, explain 'Why' it is essential reading."
    }}
  ]
}}
