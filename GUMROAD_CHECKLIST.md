# Arcanova AI Gumroad Checklist

## Product Positioning
- Product name: Arcanova AI Story Narration Studio
- Delivery: source package (GitHub-ready) + optional EXE build instructions
- Target: creators, educators, parents, storytelling channels

## What To Upload On Gumroad
- Source zip generated from this repo
- Product images (screenshots of app + index page)
- Demo audio samples (.wav)
- Short demo video (recommended)

## Included Features
- Local Qwen 3B story generation (no API keys)
- Full-story narration completion with chunked synthesis
- Sci-Fi Masque mode
- Age group guardrails (Kids, Teens, Family, Adults)
- Booming narration effect
- Feedback capture in outputs/feedback.jsonl

## Pricing Suggestion
- Starter source pack: $19-$29
- Pro pack (includes support): $49-$79

## Customer Instructions
1. Install Python 3.10+.
2. Install dependencies: pip install -r requirements.txt
3. Run app: streamlit run app.py
4. Build EXE (optional): python build_exe.py

## Notes
- First model load requires internet to download weights.
- After download, story generation runs locally.
