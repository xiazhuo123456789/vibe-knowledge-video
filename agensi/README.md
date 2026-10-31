# Cinematic Knowledge Shorts

Turn one fact, theorem or paper into a 2-minute cinematic knowledge short using
pure code: HTML Canvas animation, synthesized instrumental music, bilingual
on-screen subtitles, no voiceover.

Output: 1920x1080, 30fps, 2:00-2:45, H.264 MP4.

## What this is not

No voiceover. No stock footage. **This package ships no third-party video,
audio, image or transcript files.** Every frame is drawn in code; the music is
synthesized with numpy.

## Requirements

- Python 3.10+ with `playwright`, `pillow`, `numpy`
- `playwright install chromium`
- ffmpeg with libx264 (MP4 mux; `-14 LUFS` loudness target)
- An LLM API key of your own. The host agent writes the script; this package
  never stores, embeds or transmits a key.
- Optional: `tesseract-ocr` + `tesseract-ocr-chi-sim` for subtitle OCR QA

On Windows: use `python` instead of `python3`, and run `build_video.sh` from Git
Bash or WSL.

## Install

Drop this folder into your agent's skills directory, or point the agent at
`SKILL.md`. It follows the plain SKILL.md convention, so any agent that reads
that convention can use it (Claude Code, Cursor, Copilot, and others).

## Use

1. Ask for a short: give a topic plus the one sentence the viewer should
   remember.
2. The skill verifies every fact, writes `script.md`, then `storyboard.md`.
3. It stops and asks you to confirm script + storyboard. **It does not write
   code before you confirm.**
4. It builds `index.html` exposing `window.render(t)` — every frame is a pure
   function of `t` (fixed seeds, no timers, no frame-to-frame state), so
   rendering is deterministic and resumable.
5. Render frames, synthesize the score, mux, then self-check:

```bash
python3 scripts/render_frames.py index.html out_frames/ --fps 30 --duration 140
python3 scripts/synth_bgm.py bgm.wav --bpm 77 --duration 140 --sections storyboard.md
bash scripts/build_video.sh out_frames/ bgm.wav final.mp4
python3 scripts/qa_check.py final.mp4
```

The QA script scores six dimensions (1-10). Anything under 8 means: list the
three worst problems with timestamps, fix, re-render, re-score.

## Layout

| Path | What |
|---|---|
| `SKILL.md` | The seven-step workflow — start here |
| `references/` | Method: explanation design, subtitle writing, structure, render engineering |
| `scripts/` | Frame renderer, BGM synthesizer, muxer, QA scorer |
| `assets/template.html` | Canvas starter page |
| `docs/` | Common mistakes, publishing notes, topic seeds, strict mode |

## License

MIT — see `LICENSE`. You may use, modify and redistribute this package, including
commercially, as long as the copyright notice is kept.
