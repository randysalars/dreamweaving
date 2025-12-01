# Binaural Frequency Guide

A comprehensive reference for implementing binaural beats in hypnotic sessions.

## Brainwave States Overview

| State | Frequency Range | Mental State | Use Case |
|-------|----------------|--------------|----------|
| **Delta** | 0.5-4 Hz | Deep sleep, healing, regeneration | Sleep sessions, deep healing |
| **Theta** | 4-8 Hz | Deep meditation, vivid imagery, neuroplasticity | Hypnotic journeys, visualization |
| **Alpha** | 8-14 Hz | Relaxed alertness, light meditation | Induction, awakening, integration |
| **Beta** | 14-30 Hz | Active thinking, focus | Pre-talk, full awakening |
| **Gamma** | 30-100 Hz | Peak insight, integration | Insight moments, integration pulses |

---

## Detailed Frequency Reference

### Delta (0.5-4 Hz) - Deep Sleep & Healing

| Frequency | Effect | Best For |
|-----------|--------|----------|
| 0.5 Hz | Epsilon state, profound stillness | Advanced practitioners only |
| 1 Hz | Deep dreamless sleep | Sleep maintenance |
| 1.5 Hz | Healing frequency | Physical healing sessions |
| 2 Hz | Deep sleep induction | Insomnia help |
| 3 Hz | Delta-theta border | Deep relaxation |
| 4 Hz | Gateway to theta | Transition frequency |

**Implementation Notes:**
- Delta requires very slow transitions (30+ seconds per Hz)
- Carrier frequency should be low (100-150 Hz)
- Keep volume subtle (-22 to -28 dB)

### Theta (4-8 Hz) - Deep Meditation & Visualization

| Frequency | Effect | Best For |
|-----------|--------|----------|
| 4 Hz | Deep theta, profound meditation | Experienced meditators |
| 5 Hz | Problem-solving, creativity | Creative visualization |
| 6 Hz | **Optimal visualization**, neuroplastic window | Most hypnotic journeys |
| 7 Hz | Vivid imagery, dream-like state | Guided imagery, journeys |
| 7.83 Hz | Schumann resonance | Grounding, earth connection |
| 8 Hz | Alpha-theta border, gateway state | Transition moments |

**Implementation Notes:**
- This is the "sweet spot" for hypnotic sessions
- Micro-modulation (±0.3 Hz at 0.05 Hz) enhances depth
- Carrier frequency 180-220 Hz works well

### Alpha (8-14 Hz) - Relaxed Awareness

| Frequency | Effect | Best For |
|-----------|--------|----------|
| 8 Hz | Low alpha, relaxed focus | Post-journey integration |
| 9 Hz | Light relaxation | Gentle induction |
| 10 Hz | **Classic alpha**, calm alertness | Integration, awakening |
| 11 Hz | Alert relaxation | Pre-talk closing |
| 12 Hz | **Engaged relaxation**, receptive | Session opening |
| 13-14 Hz | Alpha-beta border | Full awakening |

**Implementation Notes:**
- Alpha is perfect for transitions
- Faster transitions acceptable (10-15 seconds per Hz)
- Carrier frequency 180-250 Hz

### Beta (14-30 Hz) - Active Focus

| Frequency | Effect | Best For |
|-----------|--------|----------|
| 14 Hz | Low beta, focused attention | Focused meditation |
| 16 Hz | Active concentration | Study/focus sessions |
| 18-20 Hz | High concentration | Peak performance |
| 20+ Hz | High alertness | Not recommended for hypnosis |

**Implementation Notes:**
- Use sparingly in hypnotic sessions
- Only for pre-talk or final awakening
- Short exposure only

### Gamma (30-100 Hz) - Insight & Integration

| Frequency | Effect | Best For |
|-----------|--------|----------|
| 32 Hz | Low gamma | Enhanced cognition |
| **40 Hz** | **Classic gamma**, binding, insight | Integration bursts |
| 50 Hz | High gamma | Brief awareness peaks |

**Implementation Notes:**
- Use as SHORT BURSTS only (2-5 seconds)
- Must synchronize with script "insight moments"
- Fade in/out quickly (0.2-0.5 seconds)
- Boost volume slightly (+2 dB) during burst

---

## Standard Session Progressions

### 1. Standard Hypnotic Session (25-35 min)

```
TIME    FREQUENCY   STATE         SECTION
────────────────────────────────────────────
0:00    12 Hz       Alpha         Pre-talk
3:00    12→8 Hz     Transition    Induction begins
6:00    8→6 Hz      Deepening     Main induction
9:00    6 Hz        Theta         Journey begins
20:00   6→8 Hz      Transition    Integration
25:00   8→10 Hz     Alpha         Consolidation
30:00   10→12 Hz    Alpha         Awakening
```

### 2. Neuroplasticity Session (Neural Network Navigator style)

```
TIME    FREQUENCY   STATE              SECTION
────────────────────────────────────────────────────
0:00    12 Hz       Alpha              Pre-talk
2:30    12→8 Hz     Alpha→Theta        Induction Part 1
4:30    8→7 Hz      Theta Gateway      Induction Part 2
7:00    7 Hz*       Theta (modulated)  Neural Garden
11:30   7→6 Hz      Deep Theta         Pathfinder
16:00   6 Hz + 40Hz GAMMA BURST        Weaver Integration
16:03   →7 Hz       Return to Theta    Post-insight
20:30   7→10 Hz     Theta→Alpha        Consolidation
24:00   10 Hz       Alpha              Return & Awakening

* With ±0.3 Hz micro-modulation at 0.05 Hz (20-second cycle)
```

### 3. Deep Sleep Session (45-60 min)

```
TIME    FREQUENCY   STATE         SECTION
────────────────────────────────────────────
0:00    10 Hz       Alpha         Relaxation intro
5:00    10→6 Hz     Transition    Body scan
15:00   6→4 Hz      Theta→Delta   Deepening
25:00   4→2 Hz      Delta         Sleep transition
35:00   2→1.5 Hz    Deep Delta    Deep sleep
45:00   1.5 Hz      Delta hold    Sleep maintenance
```

### 4. Confidence/Activation Session (20-25 min)

```
TIME    FREQUENCY   STATE         SECTION
────────────────────────────────────────────
0:00    14 Hz       Low Beta      Energized intro
2:00    14→10 Hz    Transition    Light relaxation
5:00    10→7 Hz     Theta         Visualization
15:00   7→10 Hz     Alpha         Integration
18:00   10→14 Hz    Beta          Activation
22:00   14 Hz       Low Beta      Empowered awakening
```

---

## Implementation Guide

### Manifest Configuration

```yaml
audio:
  binaural:
    enabled: true
    base_frequency: 200  # Carrier frequency

    # Option 1: Simple static frequency
    beat_frequency: 6    # Single frequency

    # Option 2: Dynamic progression (recommended)
    progression:
      - timestamp: 0
        frequency: 12
        transition: hold
      - timestamp: 180
        frequency: 8
        transition: linear
        duration: 60
      - timestamp: 420
        frequency: 6
        transition: smooth
        duration: 120
        modulation:
          enabled: true
          range: 0.3
          rate: 0.05
      - timestamp: 960
        frequency: 40
        transition: burst
        duration: 3
        fade_in: 0.2
        fade_out: 0.5
      - timestamp: 963
        frequency: 7
        transition: smooth
        duration: 30
```

### Frequency Map JSON Structure

For complex sessions, use a dedicated frequency map:

```json
{
  "session": "session_name",
  "duration_seconds": 1800,
  "base_carrier_frequency": 200,
  "frequency_events": [
    {
      "timestamp": 0,
      "duration": 180,
      "frequency_start": 12,
      "frequency_end": 12,
      "state": "alpha",
      "transition_type": "hold",
      "sync_points": [
        {"time": 0, "event": "session_start", "note": "Opening"}
      ]
    }
  ]
}
```

---

## Technical Specifications

### Carrier Frequency Selection

| Session Type | Recommended Carrier | Rationale |
|--------------|---------------------|-----------|
| Standard | 200 Hz | Balanced, pleasant tone |
| Deep/Sleep | 150-180 Hz | Lower, more grounding |
| Activation | 220-250 Hz | Brighter, more alert |
| Spiritual | 200-220 Hz | Mid-range, ethereal |

### Volume Guidelines

| Component | Level (dB) | Notes |
|-----------|------------|-------|
| Voice (reference) | 0 dB | Voice is master |
| Binaural | -10 to -15 dB | Audible but not distracting |
| During gamma burst | -8 to -13 dB | Slight boost for impact |
| Pink noise | -15 to -20 dB | Background filler |

### Quality Settings

- Sample rate: 48000 Hz (minimum)
- Bit depth: 24-bit for production, 16-bit for final
- Stereo separation: Full (L=-1.0, R=+1.0)
- Fade in: 3-5 seconds
- Fade out: 5-10 seconds

---

## Synchronization Best Practices

### Script-Audio Sync Points

For maximum effectiveness, synchronize frequency changes with script moments:

| Script Event | Suggested Frequency Change |
|--------------|---------------------------|
| "Close your eyes" | Begin alpha→theta descent |
| "Drifting deeper" | Accelerate descent |
| "Imagine/visualize" | Arrive at theta (6-7 Hz) |
| "Realize/understand" | Consider gamma burst |
| "Returning now" | Begin theta→alpha ascent |
| "Eyes opening" | Arrive at alpha (10-12 Hz) |

### Gamma Burst Timing

The gamma burst should synchronize with:
1. A moment of insight in the script
2. Visual flash/pulse in video (if applicable)
3. A brief pause before and after

```
Script: "...and suddenly, you UNDERSTAND..."
Audio:  [0.2s fade-in] [3s @ 40Hz] [0.5s fade-out]
Visual: [bright flash synchronized with burst peak]
```

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Harsh/buzzy sound | Carrier too high | Lower to 180-200 Hz |
| Too subtle | Beat freq too low | Ensure at least 4 Hz |
| Uncomfortable | Beat freq too high | Stay under 14 Hz for journey |
| Phase issues | Poor stereo separation | Ensure full L/R separation |
| Clipping | Volume too high | Reduce binaural to -12 dB |

---

## References

- Neuroscience of brainwave entrainment
- Monroe Institute research on binaural beats
- EEG studies on meditation states

---

*Last updated: 2024-12-01*
*Part of the Dreamweaving self-learning knowledge base*
