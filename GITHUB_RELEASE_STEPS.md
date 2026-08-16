# GitHub Release Steps

## 1) Initialize and Push
```bash
git init
git add .
git commit -m "Arcanova AI v1: story + narration + gumroad bundle"
git branch -M main
git remote add origin https://github.com/<your-username>/arcanova-ai.git
git push -u origin main
```

## 2) Optional: Build EXE
```bash
pip install pyinstaller
python build_exe.py
```
Output is created in dist/ when build succeeds.

## 3) Prepare Gumroad Source Zip
```bash
python prepare_gumroad_bundle.py
```
Zip output: dist/arcanova_gumroad_source.zip

## 4) Publish GitHub Release
```bash
git tag v1.0.0
git push origin v1.0.0
```
Then upload the Gumroad zip and optional EXE as release assets.
