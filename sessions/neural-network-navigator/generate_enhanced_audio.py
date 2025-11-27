#!/usr/bin/env python3
"""
Generate Enhanced Audio Mix with Sound Effects
Combines voice, binaural beats, and atmospheric sound effects
"""

import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
import json
import os

SAMPLE_RATE = 48000

def load_audio_file(filepath):
    """Load audio file (WAV or MP3) and convert to numpy array"""
    print(f"  Loading: {filepath}")

    if filepath.endswith('.mp3'):
        audio = AudioSegment.from_mp3(filepath)
        # Convert to stereo if mono
        if audio.channels == 1:
            audio = audio.set_channels(2)
        # Resample to target rate
        audio = audio.set_frame_rate(SAMPLE_RATE)
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())
        # Reshape to stereo
        samples = samples.reshape((-1, 2))
        # Normalize to -1.0 to 1.0
        samples = samples.astype(np.float32) / 32768.0
        return samples, len(audio)
    elif filepath.endswith('.wav'):
        rate, data = wavfile.read(filepath)
        # Convert to stereo if mono
        if len(data.shape) == 1:
            data = np.stack([data, data], axis=1)
        # Resample if needed (simplified - assumes matching rate)
        if rate != SAMPLE_RATE:
            print(f"    Warning: Sample rate mismatch ({rate} vs {SAMPLE_RATE})")
        # Normalize to -1.0 to 1.0
        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        duration_ms = len(data) * 1000 / rate
        return data, duration_ms
    else:
        raise ValueError(f"Unsupported file format: {filepath}")

def generate_bell_chime(frequency=432, duration=2.0, decay=3.0):
    """Generate a bell chime sound with harmonic overtones"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Fundamental and harmonics
    fundamental = np.sin(2 * np.pi * frequency * t)
    harmonic2 = 0.6 * np.sin(2 * np.pi * frequency * 2.0 * t)
    harmonic3 = 0.4 * np.sin(2 * np.pi * frequency * 3.0 * t)
    harmonic4 = 0.3 * np.sin(2 * np.pi * frequency * 4.5 * t)

    # Combine harmonics
    bell = fundamental + harmonic2 + harmonic3 + harmonic4

    # Exponential decay envelope
    envelope = np.exp(-t * decay)
    bell = bell * envelope

    # Normalize
    bell = bell / np.max(np.abs(bell)) * 0.15

    # Stereo with slight phase offset for width
    left = bell
    right = np.roll(bell, int(SAMPLE_RATE * 0.001))  # 1ms delay

    return np.stack([left, right], axis=1)

def generate_crystal_resonance(duration=3.0):
    """Generate crystal-like resonance for 'sudden light' moment"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # High frequency crystal tones
    crystal = (
        0.3 * np.sin(2 * np.pi * 1000 * t) +
        0.25 * np.sin(2 * np.pi * 1500 * t) +
        0.2 * np.sin(2 * np.pi * 2000 * t) +
        0.15 * np.sin(2 * np.pi * 2500 * t) +
        0.1 * np.sin(2 * np.pi * 3000 * t)
    )

    # Fade in and out
    fade_in = int(0.5 * SAMPLE_RATE)
    fade_out = int(1.5 * SAMPLE_RATE)
    envelope = np.ones(len(t))
    envelope[:fade_in] = np.linspace(0, 1, fade_in)
    envelope[-fade_out:] = np.linspace(1, 0, fade_out)

    crystal = crystal * envelope * 0.1

    # Wide stereo
    left = crystal
    right = np.roll(crystal, int(SAMPLE_RATE * 0.002))

    return np.stack([left, right], axis=1)

def generate_wind_chime_cascade(duration=4.0):
    """Generate cascading wind chime effect"""
    total_samples = int(SAMPLE_RATE * duration)
    chimes = np.zeros((total_samples, 2))

    # Multiple chimes at different frequencies
    chime_freqs = [432, 486, 540, 607, 675]

    for i, freq in enumerate(chime_freqs):
        # Stagger the chimes
        delay = i * 0.15
        delay_samples = int(delay * SAMPLE_RATE)

        # Generate individual chime
        chime = generate_bell_chime(freq, duration - delay, decay=4.0)

        # Add to cascade
        if delay_samples + len(chime) <= total_samples:
            chimes[delay_samples:delay_samples + len(chime)] += chime
        else:
            remaining = total_samples - delay_samples
            chimes[delay_samples:] += chime[:remaining]

    # Normalize
    max_val = np.max(np.abs(chimes))
    if max_val > 0:
        chimes = chimes / max_val * 0.12

    return chimes

def generate_singing_bowl(frequency=256, duration=5.0):
    """Generate singing bowl resonance"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Rich harmonic content
    bowl = (
        1.0 * np.sin(2 * np.pi * frequency * t) +
        0.7 * np.sin(2 * np.pi * frequency * 2.0 * t) +
        0.5 * np.sin(2 * np.pi * frequency * 3.0 * t) +
        0.3 * np.sin(2 * np.pi * frequency * 4.0 * t) +
        0.2 * np.sin(2 * np.pi * frequency * 5.5 * t)
    )

    # Slow fade in and very slow fade out
    fade_in = int(1.0 * SAMPLE_RATE)
    fade_out = int(3.0 * SAMPLE_RATE)
    envelope = np.ones(len(t))
    envelope[:fade_in] = np.linspace(0, 1, fade_in) ** 2
    envelope[-fade_out:] = np.linspace(1, 0, fade_out) ** 0.5

    bowl = bowl * envelope * 0.08

    # Stereo with phase
    left = bowl
    right = np.roll(bowl, int(SAMPLE_RATE * 0.0015))

    return np.stack([left, right], axis=1)

def add_sound_effect(track, effect, timestamp_seconds, volume=1.0):
    """Add a sound effect to the track at specified timestamp"""
    start_sample = int(timestamp_seconds * SAMPLE_RATE)
    effect_samples = len(effect)

    # Scale effect by volume
    effect = effect * volume

    # Add to track (with bounds checking)
    end_sample = min(start_sample + effect_samples, len(track))
    effect_end = end_sample - start_sample

    track[start_sample:end_sample] += effect[:effect_end]

    return track

def create_enhanced_audio_mix():
    """Create the complete enhanced audio mix"""
    print("=" * 70)
    print("   Neural Network Navigator: Enhanced Audio Mix")
    print("   Voice + Binaural + Sound Effects")
    print("=" * 70)
    print()

    # Load voice track
    print("📖 Loading audio files...")
    voice_file = "working_files/voice_neural_navigator_enhanced.mp3"
    binaural_file = "working_files/binaural_beats_neural_navigator.wav"

    if not os.path.exists(voice_file):
        print(f"❌ Error: Voice file not found: {voice_file}")
        print("   Please run generate_enhanced_voice.py first")
        return 1

    if not os.path.exists(binaural_file):
        print(f"❌ Error: Binaural file not found: {binaural_file}")
        print("   Please run generate_binaural_neural.py first")
        return 1

    voice, voice_duration_ms = load_audio_file(voice_file)
    binaural, binaural_duration_ms = load_audio_file(binaural_file)

    print(f"  ✓ Voice: {voice_duration_ms/1000:.1f}s ({len(voice)} samples)")
    print(f"  ✓ Binaural: {binaural_duration_ms/1000:.1f}s ({len(binaural)} samples)")

    # Use longer duration
    target_duration = max(len(voice), len(binaural))

    # Initialize mix
    print(f"\n🎚️  Initializing mix (duration: {target_duration/SAMPLE_RATE:.1f}s)")
    mix = np.zeros((target_duration, 2))

    # Add voice (centered)
    print("  Adding voice track (volume: 100%)")
    mix[:len(voice)] += voice * 1.0

    # Add binaural (subtle background)
    print("  Adding binaural beats (volume: 40%)")
    mix[:len(binaural)] += binaural * 0.4

    # Generate and add sound effects
    print("\n🔔 Generating and adding sound effects...")

    # Key moments for sound effects (in seconds)
    effects_timeline = [
        # Pathfinder entrance - crystal bells (around 11:30 = 690s)
        {"time": 690, "effect": "bell_cascade", "volume": 0.8, "desc": "Pathfinder entrance"},

        # Pathfinder demonstration - single bell (around 12:00 = 720s)
        {"time": 720, "effect": "crystal_bell", "volume": 0.6, "desc": "Neural connection 'ping'"},

        # Weaver entrance - singing bowl (around 16:00 = 960s)
        {"time": 960, "effect": "singing_bowl", "volume": 0.7, "desc": "Weaver entrance"},

        # Gamma burst moment - crystal resonance (18:45 = 1125s)
        {"time": 1125, "effect": "crystal_flash", "volume": 0.9, "desc": "FLASH - Sudden illumination"},

        # Return journey - gentle chime (around 24:00 = 1440s)
        {"time": 1440, "effect": "crystal_bell", "volume": 0.5, "desc": "Return ascent"},
    ]

    for event in effects_timeline:
        timestamp = event["time"]
        effect_type = event["effect"]
        volume = event["volume"]
        desc = event["desc"]

        print(f"  {timestamp}s - {desc}")

        # Generate appropriate effect
        if effect_type == "bell_cascade":
            effect = generate_wind_chime_cascade(duration=4.0)
        elif effect_type == "crystal_bell":
            effect = generate_bell_chime(frequency=432, duration=2.5)
        elif effect_type == "crystal_flash":
            effect = generate_crystal_resonance(duration=3.0)
        elif effect_type == "singing_bowl":
            effect = generate_singing_bowl(frequency=256, duration=5.0)
        else:
            continue

        # Add to mix
        mix = add_sound_effect(mix, effect, timestamp, volume)

    # Normalize mix
    print("\n🎛️  Normalizing audio...")
    max_amplitude = np.max(np.abs(mix))
    if max_amplitude > 0:
        # Leave headroom
        target_level = 0.85
        mix = mix * (target_level / max_amplitude)

    # Apply subtle fade in/out
    print("  Applying fade in/out...")
    fade_in_samples = int(5 * SAMPLE_RATE)
    fade_out_samples = int(8 * SAMPLE_RATE)

    fade_in_curve = np.linspace(0, 1, fade_in_samples)
    mix[:fade_in_samples, 0] *= fade_in_curve
    mix[:fade_in_samples, 1] *= fade_in_curve

    fade_out_curve = np.linspace(1, 0, fade_out_samples)
    mix[-fade_out_samples:, 0] *= fade_out_curve
    mix[-fade_out_samples:, 1] *= fade_out_curve

    # Convert to 16-bit PCM
    print("\n💾 Converting to 16-bit PCM...")
    mix_int16 = (mix * 32767).astype(np.int16)

    # Save output
    output_file = "working_files/neural_navigator_complete_enhanced.wav"
    print(f"  Saving to: {output_file}")
    wavfile.write(output_file, SAMPLE_RATE, mix_int16)

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    duration_min = len(mix) / SAMPLE_RATE / 60

    print()
    print("=" * 70)
    print("✅ SUCCESS! Enhanced audio mix complete!")
    print("=" * 70)
    print(f"📁 Output: {output_file}")
    print(f"📊 Size: {file_size_mb:.1f} MB")
    print(f"⏱️  Duration: {duration_min:.1f} minutes")
    print()
    print("✨ Enhancement features:")
    print("   • Removed script metadata from narration")
    print("   • Extended pauses on transition phrases")
    print("   • Added bell chimes at key moments")
    print("   • Crystal resonance for 'flash of insight'")
    print("   • Singing bowl for Weaver entrance")
    print("   • Wind chime cascade for Pathfinder")
    print("   • Synchronized with binaural gamma burst")
    print()
    print("🎧 Ready for final export or further processing!")
    print()

    return 0

if __name__ == "__main__":
    exit(create_enhanced_audio_mix())
