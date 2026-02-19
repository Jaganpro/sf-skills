<!-- Parent: sf-diagram-nanobananapro/SKILL.md -->
   1 # Gemini CLI Setup for sf-diagram-nanobananapro
   2 
   3 ## Prerequisites
   4 
   5 ### 1. Authenticate with Google
   6 
   7 ```bash
   8 # Start Gemini CLI - opens browser for OAuth
   9 gemini
  10 
  11 # Select "Login with Google" when prompted
  12 # Credentials cached at ~/.gemini/oauth_creds.json
  13 ```
  14 
  15 ### 2. Install Nano Banana Extension
  16 
  17 ```bash
  18 gemini extensions install https://github.com/gemini-cli-extensions/nanobanana
  19 ```
  20 
  21 ### 3. Install timg for Image Display
  22 
  23 ```bash
  24 brew install timg
  25 ```
  26 
  27 ### 4. Configure Environment
  28 
  29 Add to `~/.zshrc`:
  30 
  31 ```bash
  32 export NANOBANANA_MODEL=gemini-3-pro-image-preview
  33 export PATH="$HOME/.local/bin:$PATH"
  34 ```
  35 
  36 ---
  37 
  38 ## Verification
  39 
  40 ```bash
  41 # Check Gemini CLI
  42 gemini --version
  43 
  44 # Check Nano Banana
  45 gemini extensions list
  46 
  47 # Check timg
  48 which timg
  49 
  50 # Test image generation
  51 gemini "/generate 'A blue circle on white background'"
  52 timg ~/gemini-images/*.png
  53 ```
  54 
  55 ---
  56 
  57 ## File Locations
  58 
  59 | File | Purpose |
  60 |------|---------|
  61 | `~/.gemini/settings.json` | Gemini CLI settings |
  62 | `~/.gemini/oauth_creds.json` | OAuth tokens |
  63 | `~/.gemini/extensions/nanobanana/` | Nano Banana extension |
  64 | `~/gemini-images/` | Generated images |
