# MCP Server Setup for Enhanced Code Generation

## What Was Configured

I've set up Model Context Protocol (MCP) servers in your Claude Code configuration to provide enhanced coding capabilities whenever you code with Claude.

## Configured MCP Servers

### 1. Filesystem Server
**Purpose:** Enhanced file operations and code analysis
- Read/write files with better context
- Analyze project structure
- Search across codebase

**Status:** ✅ Ready (no API key needed)

### 2. GitHub Server  
**Purpose:** Access code examples and documentation from GitHub
- Search GitHub repositories
- Read code from public repos
- Find implementation patterns

**Status:** ⚠️ Needs setup (see below)

### 3. Brave Search Server
**Purpose:** Search for code examples and documentation online
- Find tutorials and guides
- Search Stack Overflow
- Discover best practices

**Status:** ⚠️ Needs setup (see below)

## Setup Required (Optional)

### GitHub Token (Recommended)
If you want GitHub integration:

1. Go to https://github.com/settings/tokens
2. Generate a new token (classic) with `repo` scope
3. Add to your environment:
```bash
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### Brave Search API (Optional)
If you want web search for code examples:

1. Get API key from https://brave.com/search/api/
2. Add to your environment:
```bash
echo 'export BRAVE_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## How to Use

The MCP servers are **automatically available** when you use Claude Code. You don't need to do anything special - I can now access these tools automatically when they're helpful.

### Example Use Cases

**With Filesystem Server:**
- "Analyze the structure of my audio library code"
- "Find all Python files that use the audio generation functions"
- "Refactor this code across multiple files"

**With GitHub Server (once configured):**
- "Find examples of YAML parsing in popular Python projects"
- "Show me how other projects handle audio caching"
- "What's the best practice for MCP server configuration?"

**With Brave Search (once configured):**
- "Search for Python audio processing best practices"
- "Find tutorials on ffmpeg audio mixing"
- "Look up SSML specification documentation"

## Configuration File Location

`~/.config/claude-code/settings.json`

## Testing

To verify the servers are working:

```bash
# Check if config is valid JSON
cat ~/.config/claude-code/settings.json | python3 -m json.tool

# Test filesystem server manually
npx -y @modelcontextprotocol/server-filesystem /home/rsalars/Projects/dreamweaving
```

## Restart Required

**Important:** You need to restart your Claude Code session (close and reopen) for the MCP servers to be loaded.

## Benefits

✅ **Better code generation** - Access to more context and examples
✅ **Faster development** - Find solutions and patterns quickly  
✅ **Enhanced analysis** - Better understanding of your codebase
✅ **Automatic integration** - Works seamlessly in the background

## Troubleshooting

### Servers not loading?
1. Check JSON syntax: `python3 -m json.tool ~/.config/claude-code/settings.json`
2. Restart Claude Code completely
3. Check Node.js is installed: `node --version`

### GitHub/Brave not working?
- Make sure environment variables are set
- Restart your terminal/shell after setting variables
- Check with: `echo $GITHUB_TOKEN` or `echo $BRAVE_API_KEY`

### Need to disable a server?
Comment it out in the config:
```json
"mcpServers": {
  "_disabled_github": {
    ...
  }
}
```

## Next Steps

1. **Restart Claude Code** to load the MCP servers
2. **Optional:** Set up GitHub token for enhanced capabilities
3. **Optional:** Set up Brave API key for web search
4. **Start coding!** The servers work automatically

## More Information

- MCP Documentation: https://modelcontextprotocol.io/
- Available Servers: https://github.com/modelcontextprotocol/servers
- Claude Code Docs: https://docs.anthropic.com/claude-code
