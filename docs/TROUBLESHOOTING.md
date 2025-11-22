# 🔧 Troubleshooting Guide

Common issues and solutions for dreamweaving audio generation.

---

## Virtual Environment Issues

### Problem: `venv` not activating

**Symptoms:**
- `source venv/bin/activate` doesn't work
- No `(venv)` prefix in terminal

**Solutions:**
```bash
# Linux/Mac
source venv/bin/activate

# If that doesn't work, recreate venv:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Import errors after activation

**Symptoms:**
```
ModuleNotFoundError: No module named 'google.cloud'
```

**Solution:**
```bash
# Ensure venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt

# Verify installation
pip list | grep google-cloud-texttospeech
```

---

## Audio Generation Issues

### Problem: "Chunk too large" error

**Symptoms:**
```
Error: Chunk exceeds 5000 byte limit (5234 bytes)
```

**Solution:**
Add more `<break>` tags in your SSML to create natural split points:

```xml
<!-- Before (too long) -->
<speak>
Long paragraph with no breaks that goes on and on...
</speak>

<!-- After (properly chunked) -->
<speak>
Shorter sentence.<break time="1s"/>
Another sentence.<break time="1s"/>
Third sentence.<break time="2s"/>
</speak>
```

**Alternative:** Reduce `max_bytes` in the script:
```python
# In scripts/core/generate_audio_chunked.py, line ~42
chunks = split_ssml_into_chunks(ssml_content, max_bytes=4000)  # Lower from 4500
```

### Problem: FFmpeg not found

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Problem: Audio generation is very slow

**Possible Causes:**
- Network latency to Google Cloud
- Very large SSML file
- Too many chunks

**Solutions:**
1. Check your internet connection
2. Split large sessions into multiple files
3. Use `scripts/core/generate_audio.py` for small files instead of chunked version

---

## Authentication Issues

### Problem: Google Cloud authentication failed

**Symptoms:**
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**Solution:**
```bash
# Login with application default credentials
gcloud auth application-default login

# Follow the browser prompts to authenticate

# Verify authentication
gcloud auth application-default print-access-token
```

### Problem: API not enabled

**Symptoms:**
```
google.api_core.exceptions.PermissionDenied: Cloud Text-to-Speech API has not been used
```

**Solution:**
```bash
# Enable the Text-to-Speech API
gcloud services enable texttospeech.googleapis.com

# Verify API is enabled
gcloud services list --enabled | grep texttospeech
```

### Problem: Billing account not set up

**Symptoms:**
```
This API method requires billing to be enabled
```

**Solution:**
1. Go to: https://console.cloud.google.com/billing
2. Create or select a billing account
3. Enable billing for your project
4. Note: Free tier includes 1M characters/month

---

## SSML Issues

### Problem: Word mispronounced

**Solution:**
Use the `<phoneme>` tag with IPA pronunciation:

```xml
<!-- Example: "path-working" -->
<phoneme alphabet="ipa" ph="pæθ ˈwɝkɪŋ">path-working</phoneme>

<!-- Example: "chakra" -->
<phoneme alphabet="ipa" ph="ˈtʃʌkrə">chakra</phoneme>
```

Find IPA pronunciation: https://tophonetics.com/

### Problem: Pauses too short/long

**Solution:**
Adjust `<break>` time values:

```xml
<!-- Too short -->
<break time="500ms"/>

<!-- Better for hypnosis -->
<break time="2s"/>

<!-- Very long pause (for deep work) -->
<break time="5s"/>
```

### Problem: Voice too fast/slow

**Solution:**
Adjust `<prosody rate>`:

```xml
<!-- Too fast -->
<prosody rate="medium">

<!-- Better for hypnosis -->
<prosody rate="slow">

<!-- Very slow for deep trance -->
<prosody rate="x-slow">
```

### Problem: SSML validation errors

**Symptoms:**
```
XML parsing error
Invalid SSML syntax
```

**Solution:**
```bash
# Validate your SSML
python scripts/utilities/validate_ssml.py sessions/my-session/script.ssml

# Common fixes:
# 1. Ensure all tags are closed
# 2. Escape special characters: & < > " '
# 3. Check for unmatched <speak> tags
```

---

## Voice Issues

### Problem: Can't find voice name

**Solution:**
Check available voices:
```bash
# View voice profiles
cat config/voice_profiles.json

# Or list all Google voices
python -c "from google.cloud import texttospeech; client = texttospeech.TextToSpeechClient(); voices = client.list_voices(); print([v.name for v in voices.voices if 'en-US' in v.name])"
```

### Problem: Voice sounds wrong for hypnosis

**Recommended voices for hypnosis:**

**Female (warm, calming):**
- `en-US-Neural2-A` ⭐ Default
- `en-US-Neural2-C` - Softer
- `en-US-Neural2-F` - Clear and serene

**Male (deep, resonant):**
- `en-US-Neural2-D` - Deep
- `en-US-Neural2-I` - Warm
- `en-US-Neural2-J` - Rich, mature

**Change voice:**
```bash
python scripts/core/generate_audio_chunked.py \
    input.ssml output.mp3 en-US-Neural2-D
```

---

## File Path Issues

### Problem: File not found

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'sessions/my-session/script.ssml'
```

**Solution:**
```bash
# Verify the file exists
ls -la sessions/my-session/script.ssml

# Use absolute paths if needed
python scripts/core/generate_audio_chunked.py \
    ~/Projects/dreamweaving/sessions/my-session/script.ssml \
    ~/Projects/dreamweaving/sessions/my-session/output/audio.mp3

# Or ensure you're in the project root
cd ~/Projects/dreamweaving
```

### Problem: Permission denied

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/utilities/create_new_session.sh
chmod +x activate.sh

# Fix ownership if needed
sudo chown -R $USER:$USER ~/Projects/dreamweaving
```

---

## Output Issues

### Problem: Audio file is empty or corrupted

**Solution:**
```bash
# Check if file was created
ls -lh sessions/my-session/output/audio.mp3

# Try regenerating
rm sessions/my-session/output/audio.mp3
python scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3

# Verify audio metadata
ffprobe sessions/my-session/output/audio.mp3
```

### Problem: Audio cuts off or has gaps

**Possible Causes:**
- Chunking split mid-sentence
- Break times too long
- Merge failed

**Solutions:**
1. Adjust chunk splitting in SSML (add breaks at better locations)
2. Check that all chunks generated successfully
3. Verify FFmpeg is working: `ffmpeg -version`

---

## Performance Issues

### Problem: Generation taking too long

**Normal times:**
- 10-min session: 1-2 minutes
- 30-min session: 3-5 minutes
- 60-min session: 6-10 minutes

**If slower:**
1. Check internet connection
2. Verify not hitting API rate limits
3. Consider splitting into smaller sessions

### Problem: Out of free tier characters

**Solution:**
```bash
# Check usage in Google Cloud Console
# Go to: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/quotas

# To reduce character usage:
# 1. Shorten scripts
# 2. Remove unnecessary pauses/breaks
# 3. Use shorter descriptions in pre-talk
# 4. Wait for next month's free tier reset
```

---

## Development Issues

### Problem: Script modifications not taking effect

**Solution:**
```bash
# Ensure you saved the file
# Regenerate audio (scripts don't cache)

# If using VS Code, check for unsaved changes (dot in tab)
```

### Problem: Can't edit SSML in VS Code

**Solution:**
```bash
# Install XML extension
# In VS Code: Ctrl+P, then paste:
ext install redhat.vscode-xml

# Or edit in any text editor
nano sessions/my-session/script.ssml
```

---

## Session Creation Issues

### Problem: create_new_session.sh not found

**Solution:**
```bash
# Verify script exists
ls -la scripts/utilities/create_new_session.sh

# Make executable
chmod +x scripts/utilities/create_new_session.sh

# Run from project root
cd ~/Projects/dreamweaving
./scripts/utilities/create_new_session.sh "session-name"
```

### Problem: Session folder not created properly

**Solution:**
```bash
# Create manually
mkdir -p sessions/my-session/{output,variants}
cp templates/base/hypnosis_template.ssml sessions/my-session/script.ssml
touch sessions/my-session/notes.md
```

---

## System-Specific Issues

### Linux

**Problem: Audio playback not working**
```bash
# Install VLC or another player
sudo apt install vlc

# Play audio
vlc sessions/my-session/output/audio.mp3
```

### macOS

**Problem: FFmpeg not in PATH**
```bash
# Reinstall via Homebrew
brew reinstall ffmpeg

# Add to PATH
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Windows (WSL)

**Problem: Path issues with Windows/Linux**
```bash
# Use Linux paths within WSL
cd ~/Projects/dreamweaving

# Not Windows paths like C:\Users\...
```

---

## Getting More Help

### Check Documentation
1. [INDEX.md](INDEX.md) - Navigate all docs
2. [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Complete workflow
3. [SSML_REFERENCE.md](SSML_REFERENCE.md) - SSML formatting

### Check Script Outputs
```bash
# Run with verbose output
python -v scripts/core/generate_audio_chunked.py input.ssml output.mp3

# Check Python errors
python3 -c "import google.cloud.texttospeech; print('OK')"
```

### Verify System Requirements
```bash
# Python version (need 3.8+)
python3 --version

# FFmpeg
ffmpeg -version

# Google Cloud SDK
gcloud --version

# Virtual environment
which python  # Should show venv path
```

---

## Still Stuck?

1. **Check error messages carefully** - They usually point to the exact issue
2. **Review recent changes** - What did you change before it broke?
3. **Try a known-working example** - Use `sessions/garden-of-eden/` as a test
4. **Start fresh** - Create a minimal test case

**Test with minimal SSML:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<prosody rate="slow" pitch="-2st">
Test message.<break time="1s"/> This is a test.
</prosody>
</speak>
```

If this works, the issue is in your SSML content, not your setup.

---

[← Back to Index](INDEX.md)
