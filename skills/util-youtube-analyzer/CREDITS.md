# Credits

## Author

- **Jag Valaiyapathy** — Initial implementation

## Dependencies

This skill relies on the following open-source tools:

| Tool | License | Purpose |
|------|---------|---------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Unlicense | Video/subtitle downloading |
| [ffmpeg](https://ffmpeg.org/) | LGPL/GPL | Audio extraction |
| [whisper.cpp](https://github.com/ggerganov/whisper.cpp) | MIT | Local speech-to-text |

## Whisper Model

Uses OpenAI's Whisper base.en model, converted to GGML format by Georgi Gerganov.

- Model: `ggml-base.en.bin` (~141MB)
- Source: [HuggingFace](https://huggingface.co/ggerganov/whisper.cpp)
- Original: [OpenAI Whisper](https://github.com/openai/whisper) (MIT License)
