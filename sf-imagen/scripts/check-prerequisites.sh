#!/bin/bash
# check-prerequisites.sh - Verify sf-imagen requirements before use
# Returns 0 if all checks pass, 1 if any fail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  📸 SF-IMAGEN PREREQUISITES CHECK${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check 1: Ghostty Terminal
echo -n "  Checking terminal (Ghostty required)... "
if [[ "$TERM_PROGRAM" == "ghostty" ]] || [[ -n "$GHOSTTY_RESOURCES_DIR" ]]; then
    echo -e "${GREEN}✓ Ghostty detected${NC}"
else
    echo -e "${RED}✗ Not Ghostty${NC}"
    echo -e "    ${YELLOW}→ sf-imagen requires Ghostty for Kitty graphics protocol${NC}"
    echo -e "    ${YELLOW}→ Current terminal: ${TERM_PROGRAM:-unknown}${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: Gemini API Key
echo -n "  Checking GEMINI_API_KEY... "
if [[ -n "$GEMINI_API_KEY" ]]; then
    # Mask the key for display
    MASKED_KEY="${GEMINI_API_KEY:0:10}...${GEMINI_API_KEY: -4}"
    echo -e "${GREEN}✓ Set ($MASKED_KEY)${NC}"
else
    echo -e "${RED}✗ Not set${NC}"
    echo -e "    ${YELLOW}→ Nano Banana Pro requires a personal API key${NC}"
    echo -e "    ${YELLOW}→ Get one at: https://aistudio.google.com/apikey${NC}"
    echo -e "    ${YELLOW}→ Add to ~/.zshrc: export GEMINI_API_KEY=\"your-key\"${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: Gemini CLI
echo -n "  Checking Gemini CLI... "
if command -v gemini &> /dev/null; then
    GEMINI_VERSION=$(gemini +version 2>/dev/null | head -1 || echo "installed")
    echo -e "${GREEN}✓ $GEMINI_VERSION${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    echo -e "    ${YELLOW}→ Install: npm install -g @anthropic-ai/gemini-cli${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Nano Banana Extension
echo -n "  Checking Nano Banana extension... "
if gemini extensions list 2>/dev/null | grep -q "nanobanana"; then
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    echo -e "    ${YELLOW}→ Install: gemini extensions install nanobanana${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: timg
echo -n "  Checking timg (image display)... "
if command -v timg &> /dev/null; then
    TIMG_VERSION=$(timg --version 2>&1 | head -1)
    echo -e "${GREEN}✓ $TIMG_VERSION${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    echo -e "    ${YELLOW}→ Install: brew install timg${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "  ${GREEN}✅ All prerequisites met! sf-imagen is ready to use.${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    exit 0
else
    echo -e "  ${RED}❌ $ERRORS prerequisite(s) missing. Please fix before using sf-imagen.${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    exit 1
fi
