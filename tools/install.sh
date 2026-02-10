#!/bin/bash
# ============================================================================
# sf-skills Installer for Claude Code - Newbie-Friendly Edition
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.sh | bash
#
# Or download and run manually:
#   curl -O https://raw.githubusercontent.com/Jaganpro/sf-skills/main/tools/install.sh
#   chmod +x install.sh
#   ./install.sh
#
# ============================================================================
set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

# URLs
GITHUB_RAW="https://raw.githubusercontent.com/Jaganpro/sf-skills/main"
INSTALL_PY_URL="${GITHUB_RAW}/tools/install.py"
DOCS_URL="https://github.com/Jaganpro/sf-skills"

# Requirements
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=12
MIN_JAVA_VERSION=11
MIN_NODE_VERSION=18

# ============================================================================
# COLORS & OUTPUT HELPERS
# ============================================================================

# Colors (with fallback for basic terminals)
if [[ -t 1 ]] && [[ "${TERM:-}" != "dumb" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    DIM='\033[2m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' DIM='' NC=''
fi

print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║           sf-skills Installer for Claude Code                    ║
║                   Newbie-Friendly Edition                        ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
}

print_info() {
    echo -e "  ${CYAN}ℹ${NC} $1"
}

# Newbie-friendly explanations
explain() {
    echo -e "  ${DIM}💡 What's this?${NC} ${DIM}$1${NC}"
}

confirm() {
    local prompt="$1"
    local default="${2:-y}"

    if [[ "$default" == "y" ]]; then
        read -rp "$prompt [Y/n]: " response
        [[ -z "$response" || "$response" =~ ^[Yy] ]]
    else
        read -rp "$prompt [y/N]: " response
        [[ "$response" =~ ^[Yy] ]]
    fi
}

# ============================================================================
# OS & ARCHITECTURE DETECTION
# ============================================================================

detect_os() {
    case "$(uname -s)" in
        Darwin)  echo "macos" ;;
        Linux)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                echo "wsl"
            else
                echo "linux"
            fi
            ;;
        *)       echo "unknown" ;;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        arm64|aarch64) echo "arm64" ;;
        x86_64)        echo "x86_64" ;;
        *)             echo "unknown" ;;
    esac
}

detect_rosetta() {
    # Only relevant on macOS ARM
    if [[ "$(detect_os)" == "macos" && "$(detect_arch)" == "arm64" ]]; then
        # Check if current shell is running under Rosetta
        if [[ "$(sysctl -n sysctl.proc_translated 2>/dev/null)" == "1" ]]; then
            return 0  # Running under Rosetta
        fi
        # Check if python3 binary is x86_64
        local python_path
        python_path=$(which python3 2>/dev/null || true)
        if [[ -n "$python_path" ]] && file "$python_path" 2>/dev/null | grep -q "x86_64"; then
            return 0
        fi
    fi
    return 1
}

# ============================================================================
# TERMINAL DETECTION
# ============================================================================

detect_terminal() {
    # Check common terminal identifiers
    if [[ -n "${GHOSTTY_RESOURCES_DIR:-}" ]]; then
        echo "Ghostty"
    elif [[ "${TERM_PROGRAM:-}" == "iTerm.app" ]]; then
        echo "iTerm2"
    elif [[ "${TERM_PROGRAM:-}" == "Apple_Terminal" ]]; then
        echo "Terminal.app"
    elif [[ "${TERM_PROGRAM:-}" == "vscode" ]]; then
        echo "VS Code"
    elif [[ -n "${WARP_TERMINAL:-}" || "${TERM_PROGRAM:-}" == "WarpTerminal" ]]; then
        echo "Warp"
    elif [[ "${TERM:-}" == "alacritty" ]]; then
        echo "Alacritty"
    else
        echo "Unknown"
    fi
}

recommend_terminal() {
    local terminal
    terminal=$(detect_terminal)

    if [[ "$terminal" == "Terminal.app" ]]; then
        print_warning "You're using the basic macOS Terminal.app"
        print_info "For a better experience, consider Ghostty (free, fast, modern):"
        print_info "  https://ghostty.org"
        echo ""
    fi
}

# ============================================================================
# PROXY DETECTION
# ============================================================================

detect_proxy() {
    local has_proxy=false

    if [[ -n "${HTTP_PROXY:-}" || -n "${http_proxy:-}" ]]; then
        print_warning "HTTP proxy detected: ${HTTP_PROXY:-$http_proxy}"
        has_proxy=true
    fi

    if [[ -n "${HTTPS_PROXY:-}" || -n "${https_proxy:-}" ]]; then
        print_warning "HTTPS proxy detected: ${HTTPS_PROXY:-$https_proxy}"
        has_proxy=true
    fi

    if $has_proxy; then
        explain "Corporate proxies can sometimes cause SSL certificate issues."
        print_info "If installation fails, you may need to configure proxy certificates."
        echo ""
    fi
}

# ============================================================================
# REQUIRED DEPENDENCY CHECKS
# ============================================================================

check_homebrew() {
    print_step "Checking for Homebrew..."
    explain "Homebrew is a package manager for macOS - it helps install tools like Python."

    if command -v brew &>/dev/null; then
        local brew_version
        brew_version=$(brew --version 2>/dev/null | head -1)
        print_success "Homebrew found: $brew_version"
        return 0
    else
        print_warning "Homebrew not found"
        return 1
    fi
}

install_homebrew() {
    print_info "Installing Homebrew..."
    explain "This is the official Homebrew installer from brew.sh"

    if confirm "Install Homebrew now?"; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add to PATH for this session (M1/M2 Macs use /opt/homebrew)
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi

        print_success "Homebrew installed!"
        return 0
    else
        print_error "Homebrew is required on macOS. Please install it manually: https://brew.sh"
        return 1
    fi
}

check_python() {
    print_step "Checking for Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+..."
    explain "Python runs the sf-skills installer and hooks."

    if ! command -v python3 &>/dev/null; then
        print_warning "Python 3 not found"
        return 1
    fi

    local version major minor
    version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
    major=${version%%.*}
    minor=${version#*.}
    minor=${minor%%.*}

    if [[ "$major" -gt "$MIN_PYTHON_MAJOR" ]] || \
       [[ "$major" -eq "$MIN_PYTHON_MAJOR" && "$minor" -ge "$MIN_PYTHON_MINOR" ]]; then
        print_success "Python $version found"
        return 0
    else
        print_warning "Python $version found, but ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ required"
        return 1
    fi
}

install_python() {
    local os
    os=$(detect_os)

    print_info "Installing Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}..."

    if [[ "$os" == "macos" ]]; then
        if command -v brew &>/dev/null; then
            brew install python@3.12
            print_success "Python 3.12 installed!"
            return 0
        else
            print_error "Homebrew not found. Please install Homebrew first."
            return 1
        fi
    else
        print_error "Please install Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ manually"
        print_info "  Ubuntu/Debian: sudo apt install python3.12"
        print_info "  Fedora: sudo dnf install python3.12"
        print_info "  Or use pyenv: https://github.com/pyenv/pyenv"
        return 1
    fi
}

check_curl() {
    print_step "Checking for curl..."

    if command -v curl &>/dev/null; then
        print_success "curl found"
        return 0
    else
        print_error "curl not found (this is unusual - it's typically pre-installed)"
        return 1
    fi
}

check_ssl_certs() {
    local os
    os=$(detect_os)

    # Only relevant on macOS (python.org builds use bundled OpenSSL)
    if [[ "$os" != "macos" ]]; then
        return 0
    fi

    print_step "Checking Python SSL certificates..."
    explain "Python on macOS may need extra setup to verify HTTPS certificates."

    # Quick SSL test: try to reach GitHub API
    if python3 -c "import urllib.request; urllib.request.urlopen('https://api.github.com', timeout=5)" 2>/dev/null; then
        print_success "SSL certificates OK"
        return 0
    fi

    # SSL failed — check if certifi is available (installer will auto-use it)
    if python3 -c "import certifi" 2>/dev/null; then
        print_warning "System SSL certs missing, but certifi package found"
        print_info "The installer will use certifi automatically."
        return 0
    fi

    # No certifi — offer to install it
    print_warning "SSL certificate verification failed"
    explain "Python from python.org doesn't trust macOS system certificates by default."
    echo ""
    print_info "Fix options:"
    print_info "  1. pip3 install certifi  (quick fix — installer will auto-detect it)"
    print_info "  2. Run: /Applications/Python 3.*/Install Certificates.command"
    print_info "  3. Use Homebrew Python: brew install python3"
    echo ""

    if confirm "  Try 'pip3 install certifi' now?"; then
        if pip3 install certifi 2>/dev/null; then
            print_success "certifi installed — SSL should work now"
            return 0
        else
            print_warning "pip3 install failed — continuing anyway (Python installer has its own fallback)"
        fi
    else
        print_info "Continuing — the Python installer will report detailed errors if SSL fails."
    fi

    return 0  # Don't block installation — let the Python installer handle it
}

check_claude_code() {
    print_step "Checking for Claude Code..."
    explain "Claude Code is Anthropic's AI coding assistant CLI tool."

    if [[ -d "$HOME/.claude" ]]; then
        print_success "Claude Code directory found: ~/.claude/"
        return 0
    else
        print_error "Claude Code not installed (~/.claude/ not found)"
        echo ""
        print_info "Install Claude Code first:"
        print_info "  npm install -g @anthropic-ai/claude-code"
        print_info "  Then run: claude"
        print_info ""
        print_info "Learn more: https://claude.ai/code"
        return 1
    fi
}

# ============================================================================
# OPTIONAL DEPENDENCY CHECKS
# ============================================================================

check_sf_cli() {
    print_step "Checking for Salesforce CLI..."
    explain "The Salesforce CLI (sf) is required for most sf-skills to work."

    if command -v sf &>/dev/null; then
        local version
        version=$(sf --version 2>/dev/null | head -1)
        print_success "Salesforce CLI found: $version"
        return 0
    else
        print_warning "Salesforce CLI not found (optional)"
        return 1
    fi
}

check_java() {
    print_step "Checking for Java ${MIN_JAVA_VERSION}+..."
    explain "Java is needed for Apex Code Analyzer & LSP (real-time code validation)."

    # Check multiple locations (Homebrew, system, SDKMAN)
    local java_bin=""
    for candidate in \
        "/opt/homebrew/opt/openjdk@21/bin/java" \
        "/opt/homebrew/opt/openjdk@17/bin/java" \
        "/opt/homebrew/opt/openjdk@11/bin/java" \
        "/opt/homebrew/opt/openjdk/bin/java" \
        "$HOME/.sdkman/candidates/java/current/bin/java" \
        "/usr/bin/java"
    do
        if [[ -x "$candidate" ]]; then
            java_bin="$candidate"
            break
        fi
    done

    if [[ -z "$java_bin" ]] && command -v java &>/dev/null; then
        java_bin="$(which java)"
    fi

    if [[ -z "$java_bin" ]]; then
        print_warning "Java not found (optional - needed for Apex validation)"
        return 1
    fi

    # Parse version
    local version major
    version=$("$java_bin" -version 2>&1 | head -1 | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)
    major=${version%%.*}

    if [[ "$major" -ge "$MIN_JAVA_VERSION" ]]; then
        print_success "Java $version found"
        return 0
    else
        print_warning "Java $version found, but ${MIN_JAVA_VERSION}+ recommended"
        return 1
    fi
}

check_node() {
    print_step "Checking for Node.js ${MIN_NODE_VERSION}+..."
    explain "Node.js is needed for LWC validation and Jest testing."

    if ! command -v node &>/dev/null; then
        print_warning "Node.js not found (optional - needed for LWC validation)"
        return 1
    fi

    local version major
    version=$(node --version | sed 's/^v//')
    major=${version%%.*}

    if [[ "$major" -ge "$MIN_NODE_VERSION" ]]; then
        print_success "Node.js $version found"
        return 0
    else
        print_warning "Node.js $version found, but ${MIN_NODE_VERSION}+ recommended"
        return 1
    fi
}

# ============================================================================
# INSTALLATION
# ============================================================================

download_and_run_installer() {
    print_step "Downloading sf-skills installer..."

    local tmp_installer="/tmp/sf-skills-install-$$.py"

    if ! curl -fsSL "$INSTALL_PY_URL" -o "$tmp_installer"; then
        print_error "Failed to download installer"
        return 1
    fi

    print_success "Installer downloaded"

    print_step "Running installation..."
    echo ""

    # Run Python installer with flags to indicate we're calling from bash
    python3 "$tmp_installer" --force --called-from-bash
    local result=$?

    # Cleanup
    rm -f "$tmp_installer"

    return $result
}

# ============================================================================
# POST-INSTALL
# ============================================================================

run_health_check() {
    print_step "Running health check..."

    echo ""
    echo -e "${BOLD}Environment Status:${NC}"
    echo "────────────────────────────────────────"

    # Python
    local py_version
    py_version=$(python3 --version 2>&1)
    echo -e "  Python:       ${GREEN}✓${NC} $py_version"

    # SF CLI
    if command -v sf &>/dev/null; then
        local sf_version
        sf_version=$(sf --version 2>&1 | head -1)
        echo -e "  Salesforce:   ${GREEN}✓${NC} $sf_version"

        # Try to get default org
        local org
        org=$(sf org display --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('username',''))" 2>/dev/null || echo "")
        if [[ -n "$org" ]]; then
            echo -e "  Default Org:  ${GREEN}✓${NC} $org"
        else
            echo -e "  Default Org:  ${YELLOW}○${NC} Not set (run: sf org login web)"
        fi
    else
        echo -e "  Salesforce:   ${YELLOW}○${NC} Not installed (install: npm install -g @salesforce/cli)"
    fi

    # Java
    if command -v java &>/dev/null; then
        local java_version
        java_version=$(java -version 2>&1 | head -1)
        echo -e "  Java:         ${GREEN}✓${NC} $java_version"
    else
        echo -e "  Java:         ${YELLOW}○${NC} Not installed (Apex LSP disabled)"
    fi

    # Node
    if command -v node &>/dev/null; then
        echo -e "  Node.js:      ${GREEN}✓${NC} $(node --version)"
    else
        echo -e "  Node.js:      ${YELLOW}○${NC} Not installed (LWC validation disabled)"
    fi

    echo "────────────────────────────────────────"
}

show_next_steps() {
    echo ""
    echo -e "${BOLD}${GREEN}✅ Installation Complete!${NC}"
    echo ""
    echo -e "${BOLD}Next Steps:${NC}"
    echo ""
    echo -e "  1. ${BOLD}Restart Claude Code${NC} (or start a new session)"
    echo "     Close and reopen your terminal, then run: claude"
    echo ""
    echo -e "  2. ${BOLD}Try your first skill${NC}"
    echo "     In Claude Code, type: /sf-apex"
    echo ""
    echo -e "  3. ${BOLD}Connect a Salesforce org${NC} (if not already)"
    echo "     Run: sf org login web"
    echo ""
    echo -e "  📖 Documentation: ${CYAN}${DOCS_URL}${NC}"
    echo ""
}

open_docs() {
    local os
    os=$(detect_os)

    if confirm "Open documentation in browser?" "n"; then
        case "$os" in
            macos) open "$DOCS_URL" ;;
            linux|wsl) xdg-open "$DOCS_URL" 2>/dev/null || echo "  Open: $DOCS_URL" ;;
        esac
    fi
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    print_banner

    local os arch terminal
    os=$(detect_os)
    arch=$(detect_arch)
    terminal=$(detect_terminal)

    echo -e "${BOLD}System Info:${NC}"
    echo "  OS:       $os ($arch)"
    echo "  Terminal: $terminal"
    echo ""

    # ═══════════════════════════════════════════════════════════════════════
    # Phase 1: Environment Checks
    # ═══════════════════════════════════════════════════════════════════════
    echo -e "${BOLD}Phase 1: Environment Checks${NC}"
    echo "════════════════════════════════════════"

    detect_proxy

    if detect_rosetta; then
        print_warning "Running under Rosetta 2 (x86 emulation on ARM Mac)"
        explain "Your Python may be running in x86 mode. Consider using native ARM Python."
        print_info "To fix: brew uninstall python && brew install python"
        echo ""
    fi

    recommend_terminal

    # ═══════════════════════════════════════════════════════════════════════
    # Phase 2: Required Dependencies
    # ═══════════════════════════════════════════════════════════════════════
    echo ""
    echo -e "${BOLD}Phase 2: Required Dependencies${NC}"
    echo "════════════════════════════════════════"

    # Check curl (should always exist)
    if ! check_curl; then
        print_error "curl is required but not found"
        exit 1
    fi

    # Check Homebrew (macOS only)
    if [[ "$os" == "macos" ]]; then
        if ! check_homebrew; then
            install_homebrew || exit 1
        fi
    fi

    # Check Python
    if ! check_python; then
        if [[ "$os" == "macos" ]]; then
            if confirm "Install Python 3.12 via Homebrew?"; then
                install_python || exit 1
            else
                print_error "Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ is required"
                exit 1
            fi
        else
            install_python || exit 1
        fi
    fi

    # Check SSL certificates (macOS python.org builds)
    check_ssl_certs

    # Check Claude Code
    if ! check_claude_code; then
        exit 1
    fi

    # ═══════════════════════════════════════════════════════════════════════
    # Phase 3: Optional Dependencies
    # ═══════════════════════════════════════════════════════════════════════
    echo ""
    echo -e "${BOLD}Phase 3: Optional Dependencies${NC}"
    echo "════════════════════════════════════════"

    local missing_optional=()

    if ! check_sf_cli; then
        missing_optional+=("sf")
    fi

    if ! check_java; then
        missing_optional+=("java")
    fi

    if ! check_node; then
        missing_optional+=("node")
    fi

    if [[ ${#missing_optional[@]} -gt 0 ]]; then
        echo ""
        print_info "Missing optional dependencies: ${missing_optional[*]}"
        print_info "These enable additional features but are not required."

        if [[ "$os" == "macos" ]] && confirm "Install missing optional dependencies via Homebrew?" "n"; then
            for dep in "${missing_optional[@]}"; do
                case "$dep" in
                    sf)
                        print_info "Installing Salesforce CLI..."
                        if command -v npm &>/dev/null; then
                            npm install -g @salesforce/cli 2>/dev/null || brew install sf 2>/dev/null || true
                        else
                            brew install sf 2>/dev/null || true
                        fi
                        ;;
                    java)
                        print_info "Installing OpenJDK 21..."
                        brew install openjdk@21 2>/dev/null || true
                        ;;
                    node)
                        print_info "Installing Node.js..."
                        brew install node 2>/dev/null || true
                        ;;
                esac
            done
            print_success "Optional dependencies installed"
        fi
    fi

    # ═══════════════════════════════════════════════════════════════════════
    # Phase 4: Installation
    # ═══════════════════════════════════════════════════════════════════════
    echo ""
    echo -e "${BOLD}Phase 4: Installing sf-skills${NC}"
    echo "════════════════════════════════════════"

    if ! download_and_run_installer; then
        echo ""
        # Check if this was an SSL error
        if ! python3 -c "import urllib.request; urllib.request.urlopen('https://api.github.com', timeout=5)" 2>/dev/null; then
            print_error "Installation failed due to SSL certificate error"
            echo ""
            print_info "Fix options:"
            print_info "  1. Run: /Applications/Python\\ 3.*/Install\\ Certificates.command"
            print_info "  2. pip3 install certifi && export SSL_CERT_FILE=\$(python3 -c \"import certifi; print(certifi.where())\")"
            print_info "  3. Use Homebrew Python: brew install python3"
            print_info "  4. Corporate proxy? export SSL_CERT_FILE=/path/to/ca-bundle.pem"
        else
            print_error "Installation failed"
        fi
        exit 1
    fi

    # ── Post-install settings.json integrity check ──
    local settings_file="$HOME/.claude/settings.json"
    if [[ -f "$settings_file" ]]; then
        if ! python3 -c "import json; json.load(open('$settings_file'))" 2>/dev/null; then
            print_error "settings.json is invalid JSON after installation!"
            # Attempt auto-restore from backups
            local backup_dir="$HOME/.claude/.settings-backups"
            if [[ -d "$backup_dir" ]]; then
                local latest_backup
                latest_backup=$(/bin/ls -t "$backup_dir"/settings.*.json 2>/dev/null | head -1)
                if [[ -n "$latest_backup" ]] && python3 -c "import json; json.load(open('$latest_backup'))" 2>/dev/null; then
                    cp "$latest_backup" "$settings_file"
                    print_success "Auto-restored settings.json from backup: $(basename "$latest_backup")"
                    print_info "Restart Claude Code to apply changes"
                else
                    print_error "No valid backup found for auto-restore"
                    print_info "Run: python3 ~/.claude/sf-skills-install.py --diagnose"
                fi
            else
                print_info "Run: python3 ~/.claude/sf-skills-install.py --diagnose"
            fi
        else
            # Valid JSON — check if suspiciously small (might have lost config)
            local key_count
            key_count=$(python3 -c "import json; print(len(json.load(open('$settings_file'))))" 2>/dev/null || echo "0")
            if [[ "$key_count" -lt 3 ]]; then
                print_warning "settings.json has only $key_count top-level key(s) — config may be incomplete"
                print_info "Run: python3 ~/.claude/sf-skills-install.py --diagnose"
            fi
        fi
    fi

    # ═══════════════════════════════════════════════════════════════════════
    # Phase 5: Post-Install
    # ═══════════════════════════════════════════════════════════════════════
    echo ""
    echo -e "${BOLD}Phase 5: Verification${NC}"
    echo "════════════════════════════════════════"

    run_health_check
    show_next_steps
    open_docs
}

main "$@"
