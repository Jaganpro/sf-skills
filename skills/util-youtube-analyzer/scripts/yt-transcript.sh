#!/bin/bash
# util-youtube-analyzer: YouTube Transcript Extractor
# Usage: yt-transcript.sh "YOUTUBE_URL"

set -euo pipefail

URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "Usage: yt-transcript.sh <YOUTUBE_URL>"
  exit 1
fi

# Extract video ID for output filename
VIDEO_ID=$(echo "$URL" | sed -n 's/.*[?&]v=\([^&]*\).*/\1/p')
if [[ -z "$VIDEO_ID" ]]; then
  VIDEO_ID=$(echo "$URL" | sed -n 's/.*youtu\.be\/\([^?]*\).*/\1/p')
fi
if [[ -z "$VIDEO_ID" ]]; then
  VIDEO_ID="unknown-$(date +%s)"
fi

OUTPUT_FILE="/tmp/yt-transcript-${VIDEO_ID}.txt"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "📥 Fetching transcript for: $URL"
echo "   Video ID: $VIDEO_ID"

# Get video title
TITLE=$(yt-dlp --print title "$URL" 2>/dev/null || echo "Unknown Title")
echo "   Title: $TITLE"

# Try to get existing transcript first (fast path)
if yt-dlp --write-auto-sub --sub-lang en --skip-download \
    --sub-format vtt -o "$TMPDIR/video" "$URL" 2>/dev/null; then

  VTT_FILE=$(find "$TMPDIR" -name "*.vtt" 2>/dev/null | head -1)
  if [[ -f "$VTT_FILE" ]]; then
    echo "✅ Found existing captions"

    # Clean VTT to plain text (remove timestamps, duplicates, formatting)
    {
      echo "# $TITLE"
      echo "# Source: $URL"
      echo "# Video ID: $VIDEO_ID"
      echo ""
      grep -v "^WEBVTT\|^Kind:\|^Language:\|^NOTE\|^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\|^[0-9][0-9]:[0-9][0-9]\.[0-9]\|^$\|^[[:space:]]*$" "$VTT_FILE" | \
        sed 's/<[^>]*>//g' | \
        awk '!seen[$0]++' | \
        tr -s '\n'
    } > "$OUTPUT_FILE"

    echo "📄 Transcript saved to: $OUTPUT_FILE"
    echo "   Lines: $(wc -l < "$OUTPUT_FILE" | tr -d ' ')"
    exit 0
  fi
fi

# Fallback: Download audio and transcribe locally
echo "⚠️  No captions found. Downloading audio for local transcription..."

if ! command -v whisper-cli &>/dev/null; then
  echo "❌ whisper-cli not found. Install with: brew install whisper-cpp"
  exit 1
fi

MODEL_PATH="$HOME/.local/share/whisper/ggml-base.en.bin"
if [[ ! -f "$MODEL_PATH" ]]; then
  echo "❌ Whisper model not found at $MODEL_PATH"
  echo "   Download with:"
  echo "   curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin -o $MODEL_PATH"
  exit 1
fi

yt-dlp -x --audio-format wav --audio-quality 0 \
  -o "$TMPDIR/audio.%(ext)s" "$URL" 2>/dev/null

AUDIO_FILE="$TMPDIR/audio.wav"
if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "❌ Failed to download audio"
  exit 1
fi

echo "🎙️  Transcribing with whisper-cli (this may take a while)..."
whisper-cli -m "$MODEL_PATH" -f "$AUDIO_FILE" -otxt 2>/dev/null

{
  echo "# $TITLE"
  echo "# Source: $URL"
  echo "# Video ID: $VIDEO_ID"
  echo "# (Transcribed locally via whisper-cpp)"
  echo ""
  cat "$TMPDIR/audio.wav.txt"
} > "$OUTPUT_FILE"

echo "📄 Transcript saved to: $OUTPUT_FILE"
echo "   Lines: $(wc -l < "$OUTPUT_FILE" | tr -d ' ')"
