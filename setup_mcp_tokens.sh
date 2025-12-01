#!/bin/bash
# Quick setup script for MCP server API tokens

echo "=================================="
echo "MCP Server Token Setup"
echo "=================================="
echo ""

# Check if tokens already exist
HAS_GITHUB=false
HAS_BRAVE=false

if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GitHub token already configured"
    HAS_GITHUB=true
else
    echo "⚠️  GitHub token not found"
fi

if [ -n "$BRAVE_API_KEY" ]; then
    echo "✅ Brave API key already configured"
    HAS_BRAVE=true
else
    echo "⚠️  Brave API key not found"
fi

echo ""
echo "=================================="
echo "Setup Options"
echo "=================================="
echo ""

if [ "$HAS_GITHUB" = false ]; then
    echo "GitHub Token Setup:"
    echo "1. Visit: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Select 'repo' scope"
    echo "4. Copy the token"
    echo ""
    read -p "Paste your GitHub token (or press Enter to skip): " github_token
    
    if [ -n "$github_token" ]; then
        echo "export GITHUB_TOKEN=\"$github_token\"" >> ~/.bashrc
        export GITHUB_TOKEN="$github_token"
        echo "✅ GitHub token added to ~/.bashrc"
    else
        echo "⏭️  Skipped GitHub setup"
    fi
    echo ""
fi

if [ "$HAS_BRAVE" = false ]; then
    echo "Brave Search API Setup:"
    echo "1. Visit: https://brave.com/search/api/"
    echo "2. Sign up for API access"
    echo "3. Copy your API key"
    echo ""
    read -p "Paste your Brave API key (or press Enter to skip): " brave_key
    
    if [ -n "$brave_key" ]; then
        echo "export BRAVE_API_KEY=\"$brave_key\"" >> ~/.bashrc
        export BRAVE_API_KEY="$brave_key"
        echo "✅ Brave API key added to ~/.bashrc"
    else
        echo "⏭️  Skipped Brave setup"
    fi
    echo ""
fi

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Restart your terminal: source ~/.bashrc"
echo "2. Restart Claude Code completely"
echo "3. Start coding with enhanced capabilities!"
echo ""
echo "The MCP servers will now be available automatically."
