# Bulk_Uploader

Automated pipeline that:
1. Downloads & combines clips from a YouTube video.
2. Generates subtitles with OpenAI Whisper.
3. Overlays those subtitles on the video (`moviepy`).
4. Summarises the transcript and creates an SEO‑friendly **title** & **description** with Google Gemini.
5. Builds a Publer‑compatible Excel/CSV schedule that auto‑posts Reels/Shorts to Instagram, TikTok & YouTube.

---

## 1 Quick Start
```bash
# Clone and enter
git clone https://github.com/DataSwap-io/Bulk_Uploader.git
cd Bulk_Uploader

# Python 3.10+ recommended
python -m venv env
source env/bin/activate          # Windows: env\Scripts\activate

pip install -r requirements.txt  # moviepy, whisper, google-generativeai, ...

# Add your Google Gemini API‑key (and optional env vars)
cp .env.example .env
nano .env                         # or any editor

# Run end‑to‑end test
python main.py "https://youtu.be/VIDEO_ID" $GEMINI_API_KEY
```
The script creates `final/<name>_subtitled.mp4` and updates `videouploader.xlsx` in Publer’s CSV layout.

---

## 2 Configuration Checklist

| Variable | File | Default | Purpose / How to change |
|----------|------|---------|-------------------------|
| `GEMINI_API_KEY` | `.env`   or CLI | *empty* | **Required.** Google Gemini key used by `descriptionate.py`. |
| `output_dir` | `main.py` | `outputvid` | Folder where `main_combiner.js` writes raw clip compilations. |
| `excel_path` | `main.py` | `videouploader.xlsx` | Publer‑formatted Excel file (UTF‑8 CSV exportable). |
| `subtitle_dir` | `main.py`, `caption_gen.py` | `C:/Users/thoma/Downloads/Bulk_Uploader - Copy/src/subtitles` | Working directory for `.srt` files. Set to any writable path. |
| `font` | `subtitler.py` CLI | `Montserrat-Black.otf` | Font used for subtitle overlay. Supply TTF/OTF or system font. |
| `--fontsize` | `subtitler.py` CLI | `80` | Subtitle font size. |
| `--color` | `subtitler.py` CLI | `#ffe88c` | Subtitle font colour (hex). |
| `ImageMagick` path | `subtitler.py › configure_imagemagick()` | Auto‑detect | Set env `IMAGEMAGICK_BINARY` if detection fails. |
| `audio_path` | `caption_gen.py` | `Audio.wav` | Temporary WAV extracted from video; auto‑deleted after run. |
| `chunk_size` | `caption_gen.py` | `3` | Words per subtitle line (affects readability). |
| `target_hours` | `main.py › get_target_timestamp()` | `[12,14,17]` | Original upload‑scheduler; superseded by `schedule_utils.py`. |
| `SCHEDULE` dict | `schedule_utils.py` | See file | Posting timetable for each platform. Modify to suit your cadence. |
| `youtube_tags` | `main.py` | `#shorts …` | Default hashtags appended to YouTube description. Edit as desired. |
| `tiktok_tags` | `main.py` | `#fy #foryou …` | TikTok hashtag set. |
| `insta_tags` | `main.py` | `#fy #foryou …` | Instagram Reels hashtag set. |

> **Tip:** place any per‑environment overrides in a `config.toml` and import it at runtime to avoid Git conflicts.

---

## 3 Repository Layout
```
Bulk_Uploader/
├─ caption_gen.py        # Whisper → .srt
├─ descriptionate.py     # Gemini titles & descriptions
├─ main.py               # Orchestrator: combine, subtitle, schedule
├─ schedule_utils.py     # Generates next posting slots
├─ subtitler.py          # Burn subtitles into video
├─ requirements.txt
├─ main_combiner.js      # Node script – combines clips
└─ .env.example          # Template for secrets & keys
```

---

## 4 Environment Variables (`.env`)
```
# Google Gemini
GEMINI_API_KEY=YOUR_API_KEY

# (Optional) Force ImageMagick binary if auto‑detection fails
IMAGEMAGICK_BINARY="/usr/bin/convert"
```
Add any additional secrets (e.g. AWS credentials if you auto‑upload videos) here.

---

## 5 Detailed Workflow
1. **`main.py`** executes `node main_combiner.js` to download & splice YouTube clips → `outputvid/*.mp4`.
2. Loop over every compiled video:
   * `caption_gen.py` extracts audio & runs Whisper (**base** model by default) → `.srt`.
   * `subtitler.py` overlays the subtitles and writes `final/<name>_subtitled.mp4`.
   * `descriptionate.py` calls Gemini twice:
        1. **Title (≤ 12 words).**  
        2. **2–3 paragraph description.**  
   * Static platform‑specific hashtags are appended.
   * `schedule_utils.next_slots()` returns the next free slot in the pre‑set timetable.
   * Row added to `videouploader.xlsx` with **all 12 Publer columns** (Reminder is `FALSE`).
3. Export `videouploader.xlsx` as **CSV UTF‑8** and drag‑drop into [Publer Bulk Upload](https://publer.io).

---

## 6 Installation Notes
* **ffmpeg** is required by moviepy. On Debian/Ubuntu/Kali: `sudo apt install ffmpeg`.
* **ImageMagick** ≥ 7.0 must be in `$PATH`. On macOS with Homebrew: `brew install imagemagick`.
* On systems with PEP 668 (Kali rolling), create a virtual environment:  
  `python3 -m venv env && source env/bin/activate` before running `pip install …`.

---

## 7 Testing
```bash
pytest   # (add your own tests in tests/)
```
Or run `python descriptionate.py tests/sample.srt --only title` to ensure Gemini connectivity.

---

## 8 Contributing
1. Fork → create feature branch (`git checkout -b feat/my-feature`).
2. Commit & push → open Pull Request.
3. Ensure CI passes and code is formatted with `black` + `isort`.

---

## 9 License
MIT – see `LICENSE` file.

