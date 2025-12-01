---
name: review-code
description: Review and improve codebase quality
arguments: []
agent: learning-agent
---

# /review-code Command

Review recent code changes, identify improvements, and track code quality over time.

## Usage
```
/review-code
```

## Process

1. **Scan for changes**
   - Check git status for modified files
   - Review recent commits
   - Identify new code

2. **Code quality analysis**
   - Error handling review
   - Documentation check
   - Best practices compliance
   - Performance considerations

3. **Identify improvements**
   - Bug risks
   - Optimization opportunities
   - Missing tests
   - Documentation gaps

4. **Generate recommendations**
   - Prioritized fixes
   - Enhancement suggestions
   - Refactoring opportunities

5. **Track improvements**
   - Log changes to `knowledge/code_improvements/`
   - Update improvement history

## Review Areas

### Error Handling
- Try/except blocks
- API error handling
- File operation safety
- Graceful degradation

### Code Quality
- Function complexity
- Code duplication
- Variable naming
- Type hints

### Documentation
- Docstrings present
- README updates
- Inline comments
- Usage examples

### Performance
- Loop efficiency
- Memory usage
- I/O operations
- API call batching

## Output Format

```markdown
# Code Review Report - 2025-12-01

## Files Reviewed
- scripts/core/audio/mixer.py (modified)
- scripts/ai/script_generator.py (new)
- scripts/utilities/validation.py (modified)

## Findings

### Critical
None

### Improvements Needed
1. **mixer.py:145** - Missing error handling for file read
   - Suggestion: Add try/except with meaningful error
   - Priority: Medium

2. **script_generator.py:78** - No retry logic for API calls
   - Suggestion: Add exponential backoff
   - Priority: High

### Enhancements
1. **validation.py** - Could benefit from type hints
2. **mixer.py** - Consider extracting ducking logic to separate function

### Documentation
- [ ] Update README for new script_generator
- [ ] Add docstrings to new functions

## Recommendations
1. Add retry logic to API calls (HIGH)
2. Add error handling for file operations (MEDIUM)
3. Add type hints incrementally (LOW)
```

## Improvement Tracking

Store in `knowledge/code_improvements/improvements.yaml`:
```yaml
improvements:
  - date: 2025-12-01
    file: scripts/core/audio/mixer.py
    type: error_handling
    description: "Added try/except for file operations"
    status: completed

  - date: 2025-12-01
    file: scripts/ai/script_generator.py
    type: reliability
    description: "Added retry logic for API calls"
    status: pending
```

## Automated Checks

The review runs these checks:
- [ ] All Python files have docstrings
- [ ] No hardcoded paths
- [ ] Error handling present
- [ ] No TODO comments left
- [ ] Type hints for public functions

## Preventing Regressions

Track quality metrics:
```yaml
quality_metrics:
  - date: 2025-12-01
    files_with_docstrings: 85%
    functions_with_type_hints: 60%
    error_handling_coverage: 75%
```
