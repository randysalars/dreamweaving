---
name: generate-script
description: Generate SSML hypnotic script for a session
arguments:
  - name: session
    required: true
    description: Session name or path
agent: script-writer
---

# /generate-script Command

Generate a complete SSML hypnotic script using AI and the master prompt.

## Usage
```
/generate-script <session>
```

## Example
```
/generate-script inner-child-healing
```

## Process

1. **Load session context**
   - Read `manifest.yaml` for parameters
   - Check `knowledge/lessons_learned.yaml` for relevant insights

2. **Apply master prompt**
   - Use `prompts/hypnotic_dreamweaving_instructions.md`
   - Include topic, duration, style from manifest

3. **Generate script**
   - Create all 5 mandatory sections
   - Apply proper SSML formatting
   - Include appropriate break tags
   - Use prosody for hypnotic delivery

4. **Validate output**
   - Run SSML validation
   - Check section structure
   - Verify duration estimate

5. **Save script**
   - Write to `sessions/{session}/working_files/script.ssml`
   - Report generation complete

## Script Sections Generated

1. **Pre-talk** (2-3 min)
   - Welcome and introduction
   - Safety information
   - Set expectations

2. **Induction** (3-5 min)
   - Progressive relaxation
   - Breathing focus
   - Deepening techniques

3. **Journey** (10-20 min)
   - Main hypnotic experience
   - Symbolic narrative
   - Sensory engagement

4. **Integration** (2-3 min)
   - Process experiences
   - Anchor positive states

5. **Awakening** (1-2 min)
   - Gentle return
   - Post-hypnotic suggestions

## Quality Checks

- [ ] All sections present
- [ ] SSML validates
- [ ] Duration matches manifest
- [ ] Break tags appropriate
- [ ] Prosody applied correctly

## Dependencies

- Requires `manifest.yaml` to exist
- Uses master prompt from `prompts/`
- Applies lessons from `knowledge/`
