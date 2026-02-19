---
name: util-youtube-analyzer
description: >
  Analyze YouTube videos by extracting and processing transcripts. Triggers when
  user provides a YouTube URL (youtube.com, youtu.be) or asks to analyze, summarize,
  or extract insights from a YouTube video. Supports both existing captions and
  local AI transcription via whisper-cpp. Useful for learning from Dreamforce talks,
  Trail Together sessions, and Salesforce tutorials.
license: MIT
metadata:
  version: "1.0.0"
  author: "Jag Valaiyapathy"
  category: "utility"
---

# YouTube Video Analyzer

Agentic workflow for extracting and analyzing YouTube video content locally.

## Prerequisites

Ensure these are installed (via Homebrew):
- `yt-dlp` — Video/subtitle downloader
- `ffmpeg` — Audio extraction
- `whisper-cpp` — Local transcription (+ model at `~/.local/share/whisper/ggml-base.en.bin`)

## Agentic Workflow

When a user provides a YouTube URL:

### Step 1: Extract Transcript
Run the extraction script from this skill's directory:

```bash
${SKILL_DIR}/scripts/yt-transcript.sh "YOUTUBE_URL"
```

**Output:** Transcript saved to `/tmp/yt-transcript-{video_id}.txt`

### Step 2: Read the Transcript
Use the Read tool to load the transcript:

```
Read /tmp/yt-transcript-{video_id}.txt
```

### Step 3: Analyze Based on User Intent

| User Request | Analysis Pattern |
|--------------|------------------|
| "Summarize this video" | Structured summary with key points, takeaways |
| "What are the main topics?" | Topic extraction with timestamps |
| "Tell me about X" | Search transcript for X, provide context |
| "Create notes" | Formatted notes with section headers |
| "Find quotes about Y" | Extract relevant quotations |

## Script Behavior

The `yt-transcript.sh` script automatically:
1. **Fast path:** Fetches existing YouTube captions (no AI needed, instant)
2. **Fallback:** Downloads audio + transcribes locally via whisper-cpp
3. **Cleanup:** Converts VTT format to clean plain text

## Example Interactions

**User:** "Summarize this Dreamforce talk: https://youtube.com/watch?v=..."
**Claude:** Runs script → Reads transcript → Provides structured summary

**User:** "What did they say about Agentforce in this video?"
**Claude:** Runs script → Reads transcript → Searches for Agentforce mentions → Provides context
