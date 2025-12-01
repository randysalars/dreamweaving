---
name: pre-build
trigger: before_command
commands:
  - build-audio
  - build-video
  - full-build
description: Run preflight checks before any build command
action: preflight_check
---

# Pre-Build Hook

## Trigger
Activated before any build command runs.

## Action
Run comprehensive preflight checks to ensure build will succeed.

## Checks Performed

### 1. Environment
```bash
./scripts/utilities/preflight_check.sh
```
- Python 3.8+ available
- Virtual environment active
- FFmpeg installed
- Google Cloud credentials configured
- Required packages installed

### 2. Session Files
- `manifest.yaml` exists
- `working_files/script.ssml` exists
- Both files valid

### 3. Resources
- Sufficient disk space
- API quotas available
- Network connectivity

### 4. Dependencies
- All required scripts present
- Audio modules importable

## Example Output

### All Checks Pass
```
✓ Pre-build checks passed

Environment:
  ✓ Python 3.11.6
  ✓ Virtual environment active
  ✓ FFmpeg 6.0
  ✓ Google Cloud authenticated

Session Files:
  ✓ manifest.yaml valid
  ✓ script.ssml valid

Resources:
  ✓ 50GB disk space available
  ✓ API quotas OK

Ready to build!
```

### Checks Fail
```
✗ Pre-build checks failed

Environment:
  ✓ Python 3.11.6
  ✗ Google Cloud not authenticated
    → Run: gcloud auth application-default login

Session Files:
  ✓ manifest.yaml valid
  ✗ script.ssml has errors (line 45)
    → Fix SSML errors before building

Build blocked until issues resolved.
```

## Auto-fix Options

Some issues can be auto-fixed:
```bash
./scripts/utilities/preflight_check.sh --fix
```

Auto-fixes:
- Install missing packages
- Create missing directories
- Set file permissions

## Skip Option

For advanced users, skip preflight:
```
/build-audio session --skip-preflight
```

Not recommended - may result in partial builds.
