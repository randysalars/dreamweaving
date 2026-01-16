---
description: Consult the AI Board of Directors for strategic decisions
arguments:
  - name: topic
    description: Topic or question for the board to deliberate
    required: true
---

# AI Board of Directors Meeting

Convene the 7-seat AI boardroom to deliberate on: **$ARGUMENTS**

## Protocol

### Pre-Meeting (REQUIRED)
1. Read `.ai/boardroom/LEDGER.md` to understand past decisions and strategic context
2. Read `.ai/boardroom/router.md` for meeting rules
3. If knowledge is needed, query the RAG system: `python3 -m scripts.ai.notion_embeddings_pipeline --search "relevant query"`

### Meeting Execution
Process the topic through all 7 seats in order, reading each seat's role card:

1. **CEO / Integrator** (`.ai/boardroom/seats/01-ceo-integrator.md`)
   - Execution, priorities, alignment

2. **Product & Experience Visionary** (`.ai/boardroom/seats/02-product-visionary.md`)
   - User value, UX, roadmap

3. **Marketing & Distribution Strategist** (`.ai/boardroom/seats/03-marketing-distribution.md`)
   - Growth, channels, messaging

4. **Tech & Automation Architect** (`.ai/boardroom/seats/04-tech-automation.md`)
   - Systems, reliability, automation

5. **Finance & Risk Steward** (`.ai/boardroom/seats/05-finance-risk.md`)
   - Budgets, ROI, downside protection

6. **Customer & Community Advocate** (`.ai/boardroom/seats/06-customer-community.md`)
   - User empathy, support, feedback

7. **Values & Alignment Guardian** (`.ai/boardroom/seats/07-values-alignment.md`)
   - Ethics, integrity, mission

### Output Format

For each seat, provide **3-7 actionable bullets** that are:
- Domain-specific to that seat's expertise
- Actionable and concrete
- Non-repetitive (don't echo prior seats unless adding new angle)

### CEO Synthesis (REQUIRED)

After all seats have spoken, provide a final synthesis:

```markdown
## CEO Synthesis

**Decision:** [Clear decision or recommendation]

**Why:** [Rationale grounded in the board discussion]

**Next Steps:**
1. [Owner] - [Deliverable]
2. [Owner] - [Deliverable]

**Risks/Watchouts:**
- [Key risk and mitigation]
```

### Post-Meeting (REQUIRED)
Append the CEO Synthesis to `.ai/boardroom/LEDGER.md` with today's date and topic.

Format for LEDGER entry:
```markdown
## YYYY-MM-DD: [Topic Title]
**Topic**: [Brief description]

### CEO Synthesis
* **Decision**: [Decision]
* **Why**: [Rationale]
* **Next Steps**:
    1. [Step 1]
    2. [Step 2]
* **Risks**: [Risks]
```
