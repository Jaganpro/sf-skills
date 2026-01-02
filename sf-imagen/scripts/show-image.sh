#!/bin/bash
# show-image.sh - Display images inline using Kitty graphics protocol
# Part of sf-imagen skill for Claude Code
# Author: Jag Valaiyapathy

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DEFAULT_WIDTH="${COLUMNS:-80}"
NANOBANANA_OUTPUT_DIR="${HOME}/nanobanana-output"
GEMINI_IMAGES_DIR="${NANOBANANA_OUTPUT_DIR}"  # Nano Banana saves to ~/nanobanana-output/

show_help() {
    echo "Usage: show-image [OPTIONS] <image-path>"
    echo ""
    echo "Display images inline in terminal using Kitty graphics protocol"
    echo ""
    echo "Options:"
    echo "  -w, --width WIDTH    Set display width in columns"
    echo "  -l, --latest         Show most recent image from ~/gemini-images/"
    echo "  -a, --all            Show all images from ~/gemini-images/"
    echo "  -h, --help           Show this help message"
}

check_dependencies() {
    if ! command -v timg &> /dev/null; then
        echo -e "${RED}Error: timg is not installed${NC}"
        echo "Install it with: brew install timg"
        exit 1
    fi
}

show_image() {
    local image_path="$1"
    local width="${2:-$DEFAULT_WIDTH}"
    local height="${3:-20}"

    if [[ ! -f "$image_path" ]]; then
        echo -e "${RED}Error: File not found: $image_path${NC}"
        exit 1
    fi

    echo -e "${GREEN}Displaying: ${image_path}${NC}"
    # Use Kitty graphics protocol (-pk) for crisp images in Ghostty/Kitty/iTerm2
    # Falls back to quarter blocks if Kitty protocol not supported
    timg -g "${width}x${height}" -pk "$image_path" 2>/dev/null || timg -g "${width}x${height}" -pq "$image_path"
    echo -e "${YELLOW}Saved at: ${image_path}${NC}"
}

show_latest() {
    if [[ ! -d "$GEMINI_IMAGES_DIR" ]]; then
        echo -e "${RED}Error: Directory not found: $GEMINI_IMAGES_DIR${NC}"
        exit 1
    fi

    local latest
    latest=$(find "$GEMINI_IMAGES_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)

    if [[ -z "$latest" ]]; then
        echo -e "${YELLOW}No images found in $GEMINI_IMAGES_DIR${NC}"
        exit 0
    fi

    show_image "$latest"
}

# Main
check_dependencies

WIDTH="$DEFAULT_WIDTH"

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--width) WIDTH="$2"; shift 2 ;;
        -l|--latest) show_latest; exit 0 ;;
        -a|--all)
            find "$GEMINI_IMAGES_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) -print0 2>/dev/null | while IFS= read -r -d '' img; do
                show_image "$img" 40
            done
            exit 0 ;;
        -h|--help) show_help; exit 0 ;;
        -*) echo -e "${RED}Unknown option: $1${NC}"; show_help; exit 1 ;;
        *) show_image "$1" "$WIDTH"; exit 0 ;;
    esac
done

show_help
