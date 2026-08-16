# Arcanova AI

Arcanova AI is a local-first story generation and narration app built with Streamlit.

It combines:
- Qwen 3B class models for story writing
- Kokoro-style TTS flow with offline fallback
- Purple/white animated UI
- No API keys required

## Current v1 Features
- Story modes: Character Tale, Mythology Remix, Personal Memoir, Flash Fiction, Sci-Fi Masque, Custom
- Audience guardrails: Kids, Teens, Family, Adults
- Full-story narration completion by chunking and stitching long audio
- Optional booming narration effect
- Exports: TXT, PDF, WAV
- Simple login screen (guest login supported)
- Feedback capture saved to outputs/feedback.jsonl

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Login
Default credentials are managed from config.py and can be overridden in config.json:
- username: admin
- password: admin123

Guest login can be used from the UI for quick demo access.

## Colab Tesla T4 Notes
- Enable GPU runtime.
- Keep 4-bit loading enabled in sidebar.
- First run downloads model weights.

## GitHub Ready Flow
1. Push source to GitHub.
2. Use index.html as landing page (GitHub Pages optional).
3. Add release tag and upload source zip/build assets.

See:
- GITHUB_RELEASE_STEPS.md
- GUMROAD_CHECKLIST.md

## EXE Conversion

```bash
pip install pyinstaller
python build_exe.py
```

## Gumroad Preparation
A source bundle helper script is included:

```bash
python prepare_gumroad_bundle.py
```

If the zip is not generated automatically in your environment, run the same command locally from the project folder and upload the resulting archive.
