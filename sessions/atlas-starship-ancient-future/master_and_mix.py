#!/usr/bin/env python3
"""
ATLAS STARSHIP ANCIENT FUTURE - Voice Mastering and Final Mix

Applies hypnotic voice enhancements from manifest.yaml:
- Tape saturation warmth
- De-essing
- Whisper overlay (ethereal high layer)
- Subharmonic (warm bass layer)
- Phase-shifted double-voicing
- Room tone
- Cuddle waves (gentle amplitude modulation)

Then mixes with 7 sound layers at specified LUFS levels:
- Voice: -16 LUFS
- Binaural: -26 LUFS
- Textures: -30 LUFS

Final mastering to -14 LUFS integrated with -1.5 dBTP true peak.
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
import subprocess
import os

# Constants
SAMPLE_RATE = 48000
DURATION = 1597

# Paths
SESSION_DIR = "/home/rsalars/Projects/dreamweaving/sessions/atlas-starship-ancient-future"
VOICE_INPUT = f"{SESSION_DIR}/output/voice.mp3"
STEMS_DIR = f"{SESSION_DIR}/working_files/stems"
OUTPUT_DIR = f"{SESSION_DIR}/output"

# Mixing levels from manifest (LUFS)
VOICE_LUFS = -16
BINAURAL_LUFS = -26
TEXTURE_LUFS = -30

# Voice enhancement settings from manifest
WARMTH_DRIVE = 0.25
WHISPER_DB = -22
SUBHARMONIC_DB = -12
DOUBLE_DB = -14
DOUBLE_DELAY_MS = 8
ROOM_AMOUNT = 0.03
CUDDLE_FREQUENCY = 0.05  # Hz
CUDDLE_DEPTH_DB = 1.5

def db_to_linear(db):
    """Convert dB to linear amplitude"""
    return 10 ** (db / 20)

def linear_to_db(linear):
    """Convert linear amplitude to dB"""
    return 20 * np.log10(np.maximum(linear, 1e-10))

def calculate_rms(audio):
    """Calculate RMS level of audio"""
    return np.sqrt(np.mean(audio ** 2))

def normalize_to_lufs_approx(audio, target_lufs):
    """
    Approximate LUFS normalization using RMS
    LUFS ≈ RMS dB - 0.691 for typical speech
    """
    rms = calculate_rms(audio)
    current_db = linear_to_db(rms)
    # Approximate LUFS from RMS (simplified)
    current_lufs_approx = current_db - 3  # Rough approximation
    gain_db = target_lufs - current_lufs_approx
    gain_linear = db_to_linear(gain_db)
    return audio * gain_linear

def load_voice():
    """Load and convert voice to 48kHz stereo"""
    print("\n📥 Loading voice audio...")

    # Convert MP3 to WAV at 48kHz stereo
    temp_wav = f"{SESSION_DIR}/working_files/voice_temp.wav"
    subprocess.run([
        'ffmpeg', '-y', '-i', VOICE_INPUT,
        '-ar', '48000', '-ac', '2',
        '-acodec', 'pcm_s16le',
        temp_wav
    ], capture_output=True)

    rate, audio = wavfile.read(temp_wav)
    audio = audio.astype(np.float32) / 32767.0

    # Ensure stereo
    if len(audio.shape) == 1:
        audio = np.stack([audio, audio], axis=1)

    # Pad to match duration
    target_samples = int(SAMPLE_RATE * DURATION)
    if len(audio) < target_samples:
        padding = np.zeros((target_samples - len(audio), 2), dtype=np.float32)
        audio = np.vstack([audio, padding])
    elif len(audio) > target_samples:
        audio = audio[:target_samples]

    os.remove(temp_wav)
    print(f"  ✓ Loaded voice: {len(audio)/SAMPLE_RATE:.1f}s at {SAMPLE_RATE}Hz stereo")

    return audio

def apply_warmth(audio, drive=0.25):
    """Apply tape saturation warmth (soft clipping)"""
    print("  🔥 Applying tape warmth...")

    # Soft saturation using tanh
    # More drive = more saturation
    gain = 1 + drive * 2
    saturated = np.tanh(audio * gain) / np.tanh(gain)

    # Blend with original
    blend = 0.3 + drive * 0.4  # 30-70% wet based on drive
    output = audio * (1 - blend) + saturated * blend

    return output

def apply_deessing(audio):
    """Reduce harsh sibilants (2-8 kHz)"""
    print("  🎤 Applying de-essing...")

    # Design bandpass for sibilance detection (4-8 kHz)
    nyq = SAMPLE_RATE / 2
    b_detect, a_detect = signal.butter(2, [4000/nyq, 8000/nyq], btype='band')

    # Detect sibilance energy
    sibilance = signal.filtfilt(b_detect, a_detect, audio[:, 0])
    sibilance_env = np.abs(signal.hilbert(sibilance))

    # Smooth envelope
    smooth_samples = int(0.01 * SAMPLE_RATE)  # 10ms
    sibilance_env = np.convolve(sibilance_env, np.ones(smooth_samples)/smooth_samples, mode='same')

    # Calculate gain reduction (threshold-based)
    threshold = np.percentile(sibilance_env, 90) * 0.5
    gain_reduction = np.where(sibilance_env > threshold,
                              threshold / (sibilance_env + 1e-10),
                              1.0)
    gain_reduction = np.clip(gain_reduction, 0.3, 1.0)  # Max 10dB reduction

    # Apply to sibilant frequencies only
    b_cut, a_cut = signal.butter(2, [3000/nyq, 10000/nyq], btype='band')

    output = np.zeros_like(audio)
    for ch in range(2):
        sibilant_band = signal.filtfilt(b_cut, a_cut, audio[:, ch])
        other_bands = audio[:, ch] - sibilant_band
        output[:, ch] = other_bands + sibilant_band * gain_reduction

    return output

def create_whisper_layer(audio, level_db=-22):
    """Create ethereal high-frequency whisper layer"""
    print("  👻 Creating whisper overlay...")

    # High-pass filter (above 2kHz)
    nyq = SAMPLE_RATE / 2
    b_hp, a_hp = signal.butter(3, 2000/nyq, btype='high')

    whisper = np.zeros_like(audio)
    for ch in range(2):
        whisper[:, ch] = signal.filtfilt(b_hp, a_hp, audio[:, ch])

    # Add reverb-like diffusion
    reverb_length = int(0.8 * SAMPLE_RATE)
    decay = np.exp(-np.linspace(0, 4, reverb_length))
    ir = np.random.randn(reverb_length) * decay * 0.1

    for ch in range(2):
        whisper[:, ch] = signal.fftconvolve(whisper[:, ch], ir, mode='same')

    # Apply level
    whisper *= db_to_linear(level_db)

    return whisper

def create_subharmonic_layer(audio, level_db=-12):
    """Create warm bass foundation layer"""
    print("  🔊 Creating subharmonic layer...")

    # Low-pass filter (below 400 Hz)
    nyq = SAMPLE_RATE / 2
    b_lp, a_lp = signal.butter(3, 400/nyq, btype='low')

    sub = np.zeros_like(audio)
    for ch in range(2):
        sub[:, ch] = signal.filtfilt(b_lp, a_lp, audio[:, ch])

    # Add slight delay (creates warmth)
    delay_samples = int(0.015 * SAMPLE_RATE)  # 15ms
    sub = np.roll(sub, delay_samples, axis=0)
    sub[:delay_samples] = 0

    # Apply level
    sub *= db_to_linear(level_db)

    return sub

def create_double_voice(audio, level_db=-14, delay_ms=8):
    """Create phase-shifted subliminal double"""
    print("  🎭 Creating double voice layer...")

    delay_samples = int(delay_ms * SAMPLE_RATE / 1000)

    # Delay and slightly pitch-shift feeling via allpass
    double = np.roll(audio, delay_samples, axis=0)
    double[:delay_samples] = 0

    # Slight stereo offset for width
    double[:, 0] = np.roll(double[:, 0], 5)
    double[:, 1] = np.roll(double[:, 1], -5)

    # Apply level
    double *= db_to_linear(level_db)

    return double

def add_room_tone(audio, amount=0.03):
    """Add subtle room impulse response"""
    print("  🏠 Adding room tone...")

    # Simple room IR (small room simulation)
    room_length = int(0.3 * SAMPLE_RATE)  # 300ms room
    t = np.linspace(0, 0.3, room_length)

    # Early reflections + tail
    ir = np.zeros(room_length)
    # Early reflections
    ir[int(0.01 * SAMPLE_RATE)] = 0.5
    ir[int(0.02 * SAMPLE_RATE)] = 0.3
    ir[int(0.035 * SAMPLE_RATE)] = 0.2
    # Diffuse tail
    ir += np.random.randn(room_length) * np.exp(-t * 10) * 0.1

    room = np.zeros_like(audio)
    for ch in range(2):
        room[:, ch] = signal.fftconvolve(audio[:, ch], ir, mode='same')

    # Blend
    output = audio * (1 - amount) + room * amount

    return output

def apply_cuddle_waves(audio, freq=0.05, depth_db=1.5):
    """Apply gentle amplitude modulation for 'rocking' sensation"""
    print("  🌊 Applying cuddle waves...")

    t = np.linspace(0, DURATION, len(audio), False)

    # Very slow sine modulation
    modulation = 1 + (db_to_linear(depth_db) - 1) * np.sin(2 * np.pi * freq * t)

    output = audio * modulation[:, np.newaxis]

    return output

def master_voice(audio):
    """Apply all voice enhancements"""
    print("\n✨ VOICE MASTERING")
    print("=" * 50)

    # 1. Warmth (tape saturation)
    audio = apply_warmth(audio, WARMTH_DRIVE)

    # 2. De-essing
    audio = apply_deessing(audio)

    # 3. Create enhancement layers
    whisper = create_whisper_layer(audio, WHISPER_DB)
    subharmonic = create_subharmonic_layer(audio, SUBHARMONIC_DB)
    double = create_double_voice(audio, DOUBLE_DB, DOUBLE_DELAY_MS)

    # 4. Combine layers
    print("  🎚️ Combining voice layers...")
    enhanced = audio + whisper + subharmonic + double

    # 5. Room tone
    enhanced = add_room_tone(enhanced, ROOM_AMOUNT)

    # 6. Cuddle waves
    enhanced = apply_cuddle_waves(enhanced, CUDDLE_FREQUENCY, CUDDLE_DEPTH_DB)

    # 7. Normalize to target LUFS
    print(f"  📊 Normalizing to {VOICE_LUFS} LUFS...")
    enhanced = normalize_to_lufs_approx(enhanced, VOICE_LUFS)

    print("  ✓ Voice mastering complete")

    return enhanced

def load_stem(filename):
    """Load a stem WAV file"""
    path = f"{STEMS_DIR}/{filename}"
    rate, audio = wavfile.read(path)
    audio = audio.astype(np.float32) / 32767.0
    return audio

def mix_stems(voice):
    """Mix voice with all 7 sound layers"""
    print("\n🎛️ MIXING STEMS")
    print("=" * 50)

    # Layer categories for LUFS targeting
    binaural_layers = ['01_theta_gateway.wav']
    texture_layers = [
        '02_delta_drift.wav',
        '03_xenolinguistic.wav',
        '04_harmonic_drone.wav',
        '05_sub_bass.wav',
        '06_hyperspace_wind.wav',
        '07_ship_memory.wav'
    ]

    # Start with voice
    mix = voice.copy()

    # Add binaural layer
    print(f"\n  📡 Binaural layers (target: {BINAURAL_LUFS} LUFS):")
    for layer in binaural_layers:
        print(f"    Loading {layer}...")
        stem = load_stem(layer)
        stem = normalize_to_lufs_approx(stem, BINAURAL_LUFS)
        mix += stem
        print(f"    ✓ Added {layer}")

    # Add texture layers
    print(f"\n  🌌 Texture layers (target: {TEXTURE_LUFS} LUFS):")
    for layer in texture_layers:
        print(f"    Loading {layer}...")
        stem = load_stem(layer)
        stem = normalize_to_lufs_approx(stem, TEXTURE_LUFS)
        mix += stem
        print(f"    ✓ Added {layer}")

    return mix

def apply_sidechain_ducking(mix, voice):
    """Apply sidechain compression - duck music when voice is present"""
    print("\n  🔗 Applying sidechain ducking...")

    # Get voice envelope
    voice_mono = np.mean(np.abs(voice), axis=1)

    # Smooth envelope
    smooth_samples = int(0.1 * SAMPLE_RATE)  # 100ms
    voice_env = np.convolve(voice_mono, np.ones(smooth_samples)/smooth_samples, mode='same')

    # Normalize envelope
    voice_env = voice_env / (np.max(voice_env) + 1e-10)

    # Calculate ducking amount (more voice = more ducking)
    duck_amount = 0.3  # Max 70% reduction
    ducking = 1 - (voice_env * duck_amount)

    # Apply ducking to non-voice content
    # Separate voice from mix, duck the rest
    non_voice = mix - voice
    non_voice *= ducking[:, np.newaxis]

    return voice + non_voice

def final_master(audio):
    """Apply final mastering chain"""
    print("\n🎚️ FINAL MASTERING")
    print("=" * 50)

    # 1. Soft limiting (prevent clipping)
    print("  🔒 Applying soft limiter...")
    threshold = 0.9
    audio = np.tanh(audio / threshold) * threshold

    # 2. Final normalization to target LUFS
    print(f"  📊 Normalizing to -14 LUFS...")
    audio = normalize_to_lufs_approx(audio, -14)

    # 3. True peak limiting at -1.5 dBTP
    print("  📈 Applying true peak limiting (-1.5 dBTP)...")
    true_peak_linear = db_to_linear(-1.5)
    peak = np.max(np.abs(audio))
    if peak > true_peak_linear:
        audio = audio * (true_peak_linear / peak)

    # 4. Final soft clip for safety
    audio = np.clip(audio, -0.99, 0.99)

    print("  ✓ Final mastering complete")

    return audio

def save_output(audio, filename):
    """Save output as WAV and MP3"""
    wav_path = f"{OUTPUT_DIR}/{filename}.wav"
    mp3_path = f"{OUTPUT_DIR}/{filename}.mp3"

    # Save WAV (24-bit)
    print(f"\n💾 Saving {wav_path}...")
    audio_24bit = (audio * 8388607).astype(np.int32)
    # scipy doesn't support 24-bit, so save as 16-bit then convert
    audio_16bit = (audio * 32767).astype(np.int16)
    wavfile.write(wav_path, SAMPLE_RATE, audio_16bit)

    # Convert to 24-bit and also create MP3
    print(f"💾 Creating 24-bit WAV and MP3...")
    temp_wav = wav_path.replace('.wav', '_temp.wav')
    os.rename(wav_path, temp_wav)

    # 24-bit WAV
    subprocess.run([
        'ffmpeg', '-y', '-i', temp_wav,
        '-acodec', 'pcm_s24le', '-ar', '48000',
        wav_path
    ], capture_output=True)

    # MP3 (320kbps)
    subprocess.run([
        'ffmpeg', '-y', '-i', temp_wav,
        '-acodec', 'libmp3lame', '-b:a', '320k',
        mp3_path
    ], capture_output=True)

    os.remove(temp_wav)

    wav_size = os.path.getsize(wav_path) / (1024 * 1024)
    mp3_size = os.path.getsize(mp3_path) / (1024 * 1024)

    print(f"  ✓ {wav_path} ({wav_size:.1f} MB)")
    print(f"  ✓ {mp3_path} ({mp3_size:.1f} MB)")

def main():
    print("=" * 70)
    print("ATLAS STARSHIP ANCIENT FUTURE")
    print("Voice Mastering & Final Mix")
    print("=" * 70)

    # 1. Load and master voice
    voice = load_voice()
    voice_mastered = master_voice(voice)

    # Save mastered voice stem
    print("\n💾 Saving mastered voice stem...")
    voice_stem_path = f"{STEMS_DIR}/00_voice_mastered.wav"
    voice_16bit = (voice_mastered * 32767).astype(np.int16)
    wavfile.write(voice_stem_path, SAMPLE_RATE, voice_16bit)
    print(f"  ✓ Saved: {voice_stem_path}")

    # 2. Mix with sound layers
    mix = mix_stems(voice_mastered)

    # 3. Apply sidechain ducking
    mix = apply_sidechain_ducking(mix, voice_mastered)

    # 4. Final mastering
    final = final_master(mix)

    # 5. Save outputs
    save_output(final, "atlas_starship_final")

    # Summary
    duration_min = DURATION / 60
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print(f"\n📋 Output Summary:")
    print(f"   Duration: {duration_min:.1f} minutes")
    print(f"   Sample rate: {SAMPLE_RATE} Hz")
    print(f"   Format: 24-bit WAV + 320kbps MP3")
    print(f"\n🎧 Files:")
    print(f"   {OUTPUT_DIR}/atlas_starship_final.wav")
    print(f"   {OUTPUT_DIR}/atlas_starship_final.mp3")
    print(f"\n🎚️ Levels:")
    print(f"   Voice: {VOICE_LUFS} LUFS")
    print(f"   Binaural: {BINAURAL_LUFS} LUFS")
    print(f"   Textures: {TEXTURE_LUFS} LUFS")
    print(f"   Master: -14 LUFS / -1.5 dBTP")

if __name__ == "__main__":
    main()
