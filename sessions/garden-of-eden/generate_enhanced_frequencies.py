#!/usr/bin/env python3
"""
Enhanced Multi-Layer Frequency Generator for Garden of Eden
Combines: Binaural Beats + Isochronic Tones + Multi-frequency Layering
For deep altered-state consciousness induction
"""

import numpy as np
from scipy.io import wavfile
import sys

# Constants
SAMPLE_RATE = 48000
AMPLITUDE = 0.3  # 30% for mixing with voice

# Section durations (in seconds)
DURATIONS = {
    'pretalk': 150,        # 2:30 - Silence
    'induction': 270,      # 4:30 - Descending into Theta
    'meadow': 300,         # 5:00 - Deep Theta + Synesthesia
    'serpent': 210,        # 3:30 - Theta + Gamma bursts
    'tree': 210,           # 3:30 - Full chakra activation
    'divine': 150,         # 2:30 - Mystical unity (Gamma dominant)
    'return': 90,          # 1:30 - Ascending back to Alpha
    'anchors': 240         # 4:00 - Integration
}

def generate_tone(frequency, duration, sample_rate=SAMPLE_RATE):
    """Generate a pure sine wave tone"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * frequency * t)
    return tone

def generate_binaural_beat(base_freq, beat_freq, duration, sample_rate=SAMPLE_RATE):
    """Generate stereo binaural beat"""
    left_freq = base_freq
    right_freq = base_freq + beat_freq

    left_channel = generate_tone(left_freq, duration, sample_rate)
    right_channel = generate_tone(right_freq, duration, sample_rate)

    stereo = np.stack([left_channel, right_channel], axis=1)
    return stereo

def generate_isochronic_tone(carrier_freq, pulse_freq, duration, sample_rate=SAMPLE_RATE):
    """Generate isochronic (pulsing) tone - more effective than binaural"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Carrier wave
    carrier = np.sin(2 * np.pi * carrier_freq * t)

    # Amplitude modulation (pulse)
    pulse = (np.sin(2 * np.pi * pulse_freq * t) + 1) / 2  # 0 to 1

    # Apply modulation
    isochronic = carrier * pulse

    # Stereo (same on both channels)
    stereo = np.stack([isochronic, isochronic], axis=1)
    return stereo

def generate_frequency_ramp(start_freq, end_freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a frequency that smoothly transitions from start to end"""
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)

    # Logarithmic frequency ramp
    freq_ramp = np.logspace(np.log10(start_freq), np.log10(end_freq), num_samples)

    # Generate tone with changing frequency
    phase = 2 * np.pi * np.cumsum(freq_ramp) / sample_rate
    tone = np.sin(phase)

    stereo = np.stack([tone, tone], axis=1)
    return stereo

def add_gamma_bursts(audio, burst_freq=40, burst_duration=2, interval=30, carrier_freq=432):
    """Add periodic gamma frequency bursts (40 Hz) for mystical moments"""
    sample_rate = SAMPLE_RATE
    total_samples = len(audio)
    total_duration = total_samples / sample_rate

    # Create gamma burst pattern
    burst_samples = int(burst_duration * sample_rate)
    interval_samples = int(interval * sample_rate)

    gamma_track = np.zeros_like(audio)

    position = interval_samples  # Start after initial interval
    while position + burst_samples < total_samples:
        # Generate gamma binaural burst
        burst_left = generate_tone(carrier_freq, burst_duration, sample_rate)
        burst_right = generate_tone(carrier_freq + burst_freq, burst_duration, sample_rate)

        # Fade in/out to avoid clicks
        fade_samples = int(0.1 * sample_rate)  # 100ms fade
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)

        burst_left[:fade_samples] *= fade_in
        burst_left[-fade_samples:] *= fade_out
        burst_right[:fade_samples] *= fade_in
        burst_right[-fade_samples:] *= fade_out

        # Add to track
        gamma_track[position:position+burst_samples, 0] += burst_left * 0.3
        gamma_track[position:position+burst_samples, 1] += burst_right * 0.3

        position += interval_samples

    return audio + gamma_track

def generate_section_pretalk():
    """Section 1: Silence (allows listener to settle)"""
    duration = DURATIONS['pretalk']
    silence = np.zeros((int(SAMPLE_RATE * duration), 2))
    print(f"🔇 Section 1: Pre-Talk ({duration//60}:{duration%60:02d}) - Silence")
    return silence

def generate_section_induction():
    """Section 2: Descending into Theta (12 Hz → 6 Hz ramp)"""
    duration = DURATIONS['induction']

    # Binaural: 12 Hz → 6 Hz ramp on 174 Hz carrier (Solfeggio - releasing fear)
    binaural_ramp = generate_frequency_ramp(12, 6, duration)
    binaural = binaural_ramp * 0.5

    # Isochronic: Same 12→6 Hz ramp on 174 Hz carrier (stronger entrainment)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    carrier = np.sin(2 * np.pi * 174 * t)

    # Ramping pulse frequency
    num_samples = len(t)
    pulse_freq_ramp = np.linspace(12, 6, num_samples)
    pulse = (np.sin(2 * np.pi * np.cumsum(pulse_freq_ramp) / SAMPLE_RATE) + 1) / 2

    isochronic_mono = carrier * pulse
    isochronic = np.stack([isochronic_mono, isochronic_mono], axis=1) * 0.4

    # Combine
    combined = binaural + isochronic

    print(f"🌀 Section 2: Induction ({duration//60}:{duration%60:02d}) - 12→6 Hz ramp, 174 Hz carrier (binaural + isochronic)")
    return combined

def generate_section_meadow():
    """Section 3a: Meadow - Deep Theta (6 Hz) for synesthetic visionary state"""
    duration = DURATIONS['meadow']

    # Binaural: 6 Hz on 396 Hz carrier (Solfeggio - releasing shame/guilt)
    binaural = generate_binaural_beat(396, 6, duration) * 0.5

    # Isochronic: 6 Hz on 396 Hz carrier
    isochronic = generate_isochronic_tone(396, 6, duration) * 0.5

    # Delta undertone: 2 Hz subliminal layer for deep trance
    delta = generate_isochronic_tone(100, 2, duration) * 0.2

    combined = binaural + isochronic + delta

    print(f"🦌 Section 3a: Meadow ({duration//60}:{duration%60:02d}) - 6 Hz theta + 2 Hz delta, 396 Hz carrier")
    return combined

def generate_section_serpent():
    """Section 3b: Serpent - Mid Theta (7.5 Hz) with Gamma bursts for insight"""
    duration = DURATIONS['serpent']

    # Binaural: 7.5 Hz on 528 Hz carrier (Solfeggio - transformation/DNA repair)
    binaural = generate_binaural_beat(528, 7.5, duration) * 0.5

    # Isochronic: 7.5 Hz on 528 Hz carrier
    isochronic = generate_isochronic_tone(528, 7.5, duration) * 0.5

    combined = binaural + isochronic

    # Add periodic 40 Hz gamma bursts for "aha" moments of wisdom
    combined = add_gamma_bursts(combined, burst_freq=40, burst_duration=3, interval=45, carrier_freq=528)

    print(f"🐍 Section 3b: Serpent ({duration//60}:{duration%60:02d}) - 7.5 Hz theta + 40 Hz gamma bursts, 528 Hz carrier")
    return combined

def generate_section_tree():
    """Section 3c: Tree of Life - Schumann Resonance (7.83 Hz) with chakra frequencies"""
    duration = DURATIONS['tree']

    # Binaural: 7.83 Hz (Schumann Resonance - Earth's frequency) on 639 Hz carrier (heart chakra)
    binaural = generate_binaural_beat(639, 7.83, duration) * 0.5

    # Isochronic: 7.83 Hz on 639 Hz carrier
    isochronic = generate_isochronic_tone(639, 7.83, duration) * 0.5

    # Add subtle harmonics for chakra activation
    # 528 Hz (solar plexus), 639 Hz (heart), 741 Hz (throat)
    harmonics = (generate_tone(528, duration) * 0.1 +
                 generate_tone(639, duration) * 0.15 +
                 generate_tone(741, duration) * 0.1)
    harmonics_stereo = np.stack([harmonics, harmonics], axis=1)

    combined = binaural + isochronic + harmonics_stereo

    print(f"🌳 Section 3c: Tree ({duration//60}:{duration%60:02d}) - 7.83 Hz Schumann + chakra harmonics, 639 Hz carrier")
    return combined

def generate_section_divine():
    """Section 3d: Divine Presence - High Theta (8 Hz) transitioning to Gamma (40 Hz) for unity"""
    duration = DURATIONS['divine']

    # First half: 8 Hz theta on 963 Hz carrier (crown chakra/divine connection)
    half = duration / 2
    theta = generate_binaural_beat(963, 8, half) * 0.4
    theta_iso = generate_isochronic_tone(963, 8, half) * 0.4

    # Second half: 40 Hz gamma for mystical unity experience
    gamma = generate_binaural_beat(963, 40, half) * 0.6
    gamma_iso = generate_isochronic_tone(963, 40, half) * 0.3

    first_half = theta + theta_iso
    second_half = gamma + gamma_iso

    combined = np.vstack([first_half, second_half])

    print(f"✨ Section 3d: Divine ({duration//60}:{duration%60:02d}) - 8 Hz → 40 Hz gamma transition, 963 Hz carrier")
    return combined

def generate_section_return():
    """Section 4: Return - Ascending Theta to Alpha (8 Hz → 12 Hz)"""
    duration = DURATIONS['return']

    # Binaural: 8 Hz → 12 Hz ramp on 432 Hz carrier (universal harmony)
    binaural_ramp = generate_frequency_ramp(8, 12, duration) * 0.5

    # Isochronic: Same ramp
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    carrier = np.sin(2 * np.pi * 432 * t)

    num_samples = len(t)
    pulse_freq_ramp = np.linspace(8, 12, num_samples)
    pulse = (np.sin(2 * np.pi * np.cumsum(pulse_freq_ramp) / SAMPLE_RATE) + 1) / 2

    isochronic_mono = carrier * pulse
    isochronic = np.stack([isochronic_mono, isochronic_mono], axis=1) * 0.4

    combined = binaural_ramp + isochronic

    print(f"🌅 Section 4: Return ({duration//60}:{duration%60:02d}) - 8→12 Hz ascent, 432 Hz carrier")
    return combined

def generate_section_anchors():
    """Section 5: Anchors - Alpha coherence (10 Hz) for integration"""
    duration = DURATIONS['anchors']

    # Binaural: 10 Hz on 432 Hz carrier (alpha for relaxed alertness)
    binaural = generate_binaural_beat(432, 10, duration) * 0.5

    # Isochronic: 10 Hz on 432 Hz carrier
    isochronic = generate_isochronic_tone(432, 10, duration) * 0.4

    combined = binaural + isochronic

    print(f"⚓ Section 5: Anchors ({duration//60}:{duration%60:02d}) - 10 Hz alpha, 432 Hz carrier")
    return combined

def normalize_audio(audio, target_amplitude=AMPLITUDE):
    """Normalize audio to target amplitude"""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        normalized = audio * (target_amplitude / max_val)
    else:
        normalized = audio
    return normalized

def main():
    print("=" * 70)
    print("   Enhanced Multi-Layer Frequency Generator")
    print("   Binaural Beats + Isochronic Tones + Gamma Bursts")
    print("=" * 70)
    print()

    # Generate all sections
    sections = [
        generate_section_pretalk(),
        generate_section_induction(),
        generate_section_meadow(),
        generate_section_serpent(),
        generate_section_tree(),
        generate_section_divine(),
        generate_section_return(),
        generate_section_anchors()
    ]

    print()
    print("🔗 Concatenating sections...")
    full_track = np.vstack(sections)

    print("📊 Normalizing to 30% amplitude...")
    full_track = normalize_audio(full_track, AMPLITUDE)

    # Convert to int16 for WAV file
    full_track_int16 = (full_track * 32767).astype(np.int16)

    output_file = "enhanced_frequencies.wav"
    print(f"💾 Saving to {output_file}...")
    wavfile.write(output_file, SAMPLE_RATE, full_track_int16)

    total_duration = sum(DURATIONS.values())
    file_size = len(full_track_int16.tobytes()) / (1024**2)

    print()
    print("=" * 70)
    print("✅ SUCCESS! Enhanced frequency track generated!")
    print("=" * 70)
    print(f"📁 Output file: {output_file}")
    print(f"📊 File size: {file_size:.2f} MB")
    print(f"⏱️  Duration: {total_duration//60:.0f}:{total_duration%60:02.0f} minutes")
    print(f"🎚️  Sample rate: {SAMPLE_RATE} Hz")
    print(f"🔊 Amplitude: {int(AMPLITUDE*100)}% (ready for mixing with voice)")
    print()
    print("🧬 Technologies used:")
    print("   • Binaural beats (stereo frequency difference)")
    print("   • Isochronic tones (amplitude modulation)")
    print("   • Frequency ramping (smooth transitions)")
    print("   • Gamma bursts (40 Hz for mystical moments)")
    print("   • Multi-layer compositing (Theta + Delta + Gamma)")
    print("   • Solfeggio frequencies (ancient healing tones)")
    print()
    print("🎧 Ready to mix with voice track!")
    print()

if __name__ == "__main__":
    main()
