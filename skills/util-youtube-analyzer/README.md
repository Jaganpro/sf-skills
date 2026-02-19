# util-youtube-analyzer

Analyze YouTube videos by extracting and processing transcripts locally. Supports both existing captions (fast) and local AI transcription via whisper-cpp (fallback).

## Use Cases

- **Dreamforce talks** — Summarize keynotes, extract product announcements
- **Trail Together sessions** — Create study notes from live coding
- **Salesforce tutorials** — Find specific topics or code examples
- **Any YouTube video** — General video analysis and summarization

## Prerequisites

Install via Homebrew:

```bash
brew install yt-dlp ffmpeg whisper-cpp
```

Download the Whisper model (~141MB):

```bash
mkdir -p ~/.local/share/whisper
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" \
  -o ~/.local/share/whisper/ggml-base.en.bin
```

## Usage

Simply paste a YouTube URL in your Claude Code conversation:

```
Summarize this Dreamforce talk: https://youtube.com/watch?v=VIDEO_ID
```

Or invoke the skill directly:

```
/util-youtube-analyzer https://youtube.com/watch?v=VIDEO_ID
```

## How It Works

1. **Fast path**: Fetches existing YouTube captions (instant, no AI)
2. **Fallback**: Downloads audio → transcribes locally via whisper-cli
3. **Analysis**: Claude reads the transcript and responds to your query

## Output

Transcripts are saved to `/tmp/yt-transcript-{video_id}.txt` with metadata:

```
# Video Title
# Source: https://youtube.com/watch?v=...
# Video ID: abc123

[Transcript content...]
```

## Analysis Prompts

- "Summarize the key points"
- "What did they say about [topic]?"
- "Extract all code examples mentioned"
- "Create a timeline of topics covered"
- "Find quotes about [subject]"

## License

MIT
