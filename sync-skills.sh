#!/bin/bash

# Sync Skills from Claude Code to Repository
# This script copies skills from the Claude Code skills directory to this repository

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
REPO_SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Syncing Claude Code Skills to Repository${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check if Claude skills directory exists
if [ ! -d "$CLAUDE_SKILLS_DIR" ]; then
    echo -e "${RED}✗ Claude skills directory not found: $CLAUDE_SKILLS_DIR${NC}"
    exit 1
fi

# Check if repo skills directory exists
if [ ! -d "$REPO_SKILLS_DIR" ]; then
    echo -e "${YELLOW}⚠ Creating skills directory: $REPO_SKILLS_DIR${NC}"
    mkdir -p "$REPO_SKILLS_DIR"
fi

echo -e "${BLUE}Source:${NC} $CLAUDE_SKILLS_DIR"
echo -e "${BLUE}Target:${NC} $REPO_SKILLS_DIR"
echo ""

# List of skills to sync (skill directory names)
SKILLS=(
    "skill-builder"
    "sf-flow-builder"
    "sf-deployment"
)

# Sync each skill
for skill in "${SKILLS[@]}"; do
    SOURCE_DIR="$CLAUDE_SKILLS_DIR/$skill"
    TARGET_DIR="$REPO_SKILLS_DIR/$skill"

    if [ ! -d "$SOURCE_DIR" ]; then
        echo -e "${YELLOW}⚠ Skill not found, skipping: $skill${NC}"
        continue
    fi

    echo -e "${GREEN}→ Syncing: $skill${NC}"

    # Create target directory if it doesn't exist
    mkdir -p "$TARGET_DIR"

    # Copy all files except for:
    # - .venv (Python virtual environments)
    # - __pycache__ (Python cache)
    # - .pytest_cache (pytest cache)
    # - node_modules (Node.js dependencies)
    # - .DS_Store (macOS metadata)
    rsync -av \
        --delete \
        --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='.pytest_cache' \
        --exclude='node_modules' \
        --exclude='.DS_Store' \
        --exclude='*.pyc' \
        "$SOURCE_DIR/" "$TARGET_DIR/"

    echo -e "  ${GREEN}✓ Synced $skill${NC}"
    echo ""
done

echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Sync Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Review the changes: ${YELLOW}git status${NC}"
echo -e "  2. Add changes: ${YELLOW}git add skills/${NC}"
echo -e "  3. Commit: ${YELLOW}git commit -m 'Update skills'${NC}"
echo -e "  4. Push: ${YELLOW}git push${NC}"
echo ""
