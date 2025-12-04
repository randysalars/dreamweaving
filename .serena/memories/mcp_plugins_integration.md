# MCP Servers & Plugins Integration Guide

## Quick Reference

### Installed Plugins

| Plugin | Location | Purpose |
|--------|----------|---------|
| **media-processing** | `~/.claude/skills/media-processing/` | FFmpeg/ImageMagick for A/V processing |

### Installed MCP Servers

| Server | Location | Status |
|--------|----------|--------|
| **image-gen-mcp** | `/home/rsalars/Projects/image-gen-mcp/` | ✅ Installed |
| **mcp-server-stability-ai** | `/home/rsalars/Projects/mcp-server-stability-ai/` | ✅ Installed (needs API key) |
| **elevenlabs-mcp** | via `uvx elevenlabs-mcp` | ✅ Installed (needs API key) |

### Configuration Files

- **Project Config:** `config/mcp_servers.json`
- **Claude Desktop Config:** `~/.config/claude/claude_desktop_config.json`

---

## Starting MCP Servers

### Start SD WebUI (Required for Local Image Generation)
```bash
./scripts/utilities/start_sd_webui.sh --background
```

### Verify SD WebUI is Running
```bash
curl http://127.0.0.1:7860/sdapi/v1/sd-models
```

---

## How to Use Media-Processing Skill

### Invoking the Skill

The media-processing skill is automatically available. Use `/media-processing` or describe the task naturally:

```
"Convert the session_mixed.wav to MP3 at 320kbps"
"Extract audio from the final video"
"Resize all thumbnails to 1280x720"
```

### Common Commands

**Audio Conversion:**
```bash
# WAV to MP3
ffmpeg -i input.wav -codec:a libmp3lame -b:a 320k output.mp3

# Extract audio from video
ffmpeg -i video.mp4 -vn -acodec copy output.aac
```

**Video Processing:**
```bash
# Encode for YouTube
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k output.mp4

# Create HLS stream
ffmpeg -i input.mp4 -hls_time 10 -hls_list_size 0 output.m3u8
```

**Image Operations:**
```bash
# Batch resize
mogrify -resize 1920x1080 -path output/ *.png

# Add watermark
composite -gravity southeast watermark.png input.png output.png
```

---

## MCP Server Installation Commands

### Stable Diffusion MCP (Recommended)

**Prerequisites:**
1. Stable Diffusion WebUI installed
2. WebUI running with `--api` flag
3. Node.js v16+

**Install:**
```bash
git clone https://github.com/tadasant/stable-diffusion-mcp.git
cd stable-diffusion-mcp
npm install && npm run build
```

**Configure Claude:**
```json
// Add to ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "stable-diffusion": {
      "command": "node",
      "args": ["/path/to/stable-diffusion-mcp/dist/index.js"]
    }
  }
}
```

### ElevenLabs MCP

**Install:**
```bash
pip install uv
```

**Configure Claude:**
```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "uvx",
      "args": ["elevenlabs-mcp"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Get API Key:** https://elevenlabs.io (free tier: 10k credits/month)

---

## Context Window Management Strategy

### Problem
Each MCP tool definition uses ~400-500 tokens. 50 tools = 20,000-25,000 tokens consumed.

### Solution: Stage-Based Tool Loading

| Workflow Stage | Load These Tools |
|----------------|------------------|
| 1-2: Script Writing | Core only |
| 3-5: Audio Production | Core + Audio MCP |
| 5.5: Scene Images | Core + Image MCP |
| 6-7: Video/YouTube | Core + Media-Processing |

### How to Implement

1. **Start sessions with minimal tools**
2. **@-mention MCP servers** to toggle them on/off
3. **Use subagents** for isolated tool-heavy tasks
4. **Clear context** (`/clear`) between major stages if needed

---

## Integration with Dreamweavings Workflow

### Current Workflow (Without MCP Image Gen)

```
Stage 5.5: Generate Midjourney prompts → User creates images manually → Upload to images/uploaded/
```

### Enhanced Workflow (With SD MCP)

```
Stage 5.5: Claude invokes SD MCP → Images generated directly to images/uploaded/
```

### Example Prompts for SD MCP

```
"Generate a scene image for the neural-network-navigator session, scene 3:
ethereal blue neural pathways with glowing nodes, cosmic background,
16:9 aspect ratio, cinematic lighting, 8k detail"
```

---

## Cost Comparison

| Configuration | Image Gen | Voice Gen | Cost/Session |
|---------------|-----------|-----------|--------------|
| **Budget** | Local SD | Google TTS | ~$2-5 |
| **Standard** | SD + MJ thumbnails | Google TTS | ~$5-8 |
| **Premium** | All Midjourney | ElevenLabs | ~$15-25 |

**Recommendation:** Use "Standard" configuration for production.

---

## Troubleshooting

### "MCP server not found"
```bash
# Verify config location
cat ~/.config/claude/claude_desktop_config.json

# Check server process
ps aux | grep mcp
```

### "Tool not available"
```bash
# List installed skills
ls ~/.claude/skills/

# Reinstall if needed
npx claude-plugins skills install @mrgoonie/claudekit-skills/media-processing --force
```

### "Context window exceeded"
1. Use `/context` to check usage
2. Disable unused MCP servers
3. Use subagents for tool-heavy tasks
4. Clear with `/clear` between stages

---

## References

- Full documentation: `docs/MCP_PLUGINS_GUIDE.md`
- Claude Plugins: https://claude-plugins.dev/
- MCP Specification: https://modelcontextprotocol.io/
