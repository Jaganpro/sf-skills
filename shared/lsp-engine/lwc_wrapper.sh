#!/bin/bash
# LWC Language Server wrapper for Claude Code LSP integration
# Discovers and launches the LWC Language Server bundled with VS Code Salesforce Extension

set -e

# Find VS Code extensions directory
VSCODE_EXTENSIONS="$HOME/.vscode/extensions"

if [ ! -d "$VSCODE_EXTENSIONS" ]; then
    echo "Error: VS Code extensions directory not found at $VSCODE_EXTENSIONS" >&2
    echo "Install VS Code with Salesforce Extension Pack first." >&2
    exit 1
fi

# Find the LWC extension (get the latest version)
LWC_EXT=$(find "$VSCODE_EXTENSIONS" -maxdepth 1 -type d -name "salesforce.salesforcedx-vscode-lwc-*" | sort -V | tail -1)

if [ -z "$LWC_EXT" ]; then
    echo "Error: Salesforce LWC extension not found." >&2
    echo "Install 'Salesforce Extension Pack' from VS Code Marketplace." >&2
    exit 1
fi

# Find the LWC language server
LWC_SERVER="$LWC_EXT/node_modules/@salesforce/lwc-language-server/bin/lwc-language-server.js"

if [ ! -f "$LWC_SERVER" ]; then
    echo "Error: LWC language server not found at $LWC_SERVER" >&2
    exit 1
fi

# Find Node.js
if [ -n "$NODE_PATH" ]; then
    NODE_BIN="$NODE_PATH"
elif command -v node &> /dev/null; then
    NODE_BIN=$(command -v node)
else
    # Try common locations
    for path in /opt/homebrew/bin/node /usr/local/bin/node /usr/bin/node; do
        if [ -x "$path" ]; then
            NODE_BIN="$path"
            break
        fi
    done
fi

if [ -z "$NODE_BIN" ]; then
    echo "Error: Node.js not found." >&2
    echo "Install Node.js 18+ (brew install node)" >&2
    exit 1
fi

# Check Node.js version (require 18+)
NODE_VERSION=$("$NODE_BIN" --version | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Error: Node.js 18+ required, found v$NODE_VERSION" >&2
    exit 1
fi

# Log file for debugging (optional)
LOG_FILE="${LSP_LOG_FILE:-/dev/null}"

# Launch the LWC language server with stdio transport
exec "$NODE_BIN" "$LWC_SERVER" --stdio 2>>"$LOG_FILE"
