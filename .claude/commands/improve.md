---
description: Run manual improvement cycle for recursive agents
arguments:
  - name: agent_type
    description: Agent type to improve (dreamweaver, rag, website, all)
    required: false
    default: "all"
---

# Recursive Improvement Cycle

Run the recursive improvement cycle for specified agent type(s).

## Usage

```bash
/improve              # Run all agents
/improve dreamweaver  # Run only dreamweaver agent
/improve rag          # Run only RAG agent
/improve website      # Run only website agent
/improve all          # Run all agents
```

## What This Does

### Dreamweaver Agent
1. Retrieves outcome records for sessions with YouTube data
2. Correlates applied lessons with actual performance
3. Updates lesson effectiveness scores
4. Promotes/demotes lesson confidence levels
5. Detects new patterns from successful sessions

### RAG Agent
1. Reviews query effectiveness data
2. Updates successful query patterns
3. Refreshes semantic query cache
4. Identifies knowledge gaps

### Website Agent
1. Fetches latest Google Analytics data
2. Tracks page performance trends
3. Extracts success patterns from top performers
4. Generates improvement suggestions for underperformers
5. Updates SEO recommendations

## Execution

Run the improvement cycle for agent type: $ARGUMENTS

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))

agent_type = "$ARGUMENTS" or "all"

results = {}

if agent_type in ["all", "dreamweaver"]:
    try:
        from scripts.ai.agents import DreamweaverRecursiveAgent
        agent = DreamweaverRecursiveAgent()
        results['dreamweaver'] = agent.run_improvement_cycle()
        print("Dreamweaver improvement cycle complete")
    except Exception as e:
        results['dreamweaver'] = {'error': str(e)}
        print(f"Dreamweaver error: {e}")

if agent_type in ["all", "rag"]:
    try:
        from scripts.ai.agents import create_rag_recursive_agent
        agent = create_rag_recursive_agent()
        results['rag'] = agent.get_statistics()
        print("RAG statistics retrieved")
    except Exception as e:
        results['rag'] = {'error': str(e)}
        print(f"RAG error: {e}")

if agent_type in ["all", "website"]:
    try:
        from scripts.ai.website import create_website_recursive_agent
        agent = create_website_recursive_agent()
        results['website'] = agent.run_improvement_cycle()
        print("Website improvement cycle complete")
    except Exception as e:
        results['website'] = {'error': str(e)}
        print(f"Website error: {e}")

# Display summary
print("\n## Improvement Cycle Results\n")
for agent_name, result in results.items():
    print(f"### {agent_name.title()} Agent")
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        for key, value in result.items():
            print(f"- {key}: {value}")
    print()
```

## Output

Returns a summary of:
- Sessions processed
- Lessons updated
- Patterns detected
- Rankings changed
- Suggestions generated

## See Also

- `/show-effectiveness` - View lesson effectiveness rankings
- `/recalculate-rankings` - Force re-rank all lessons
- `/show-lessons` - View all lessons
