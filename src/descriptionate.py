import argparse
import os
import re
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv


# ────────────────────────── Helpers ──────────────────────────────
def parse_srt(srt_path: str) -> str:
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"\d+\s+\d{2}:\d{2}:\d{2},\d{3} --> .*?\n(.*?)(?=\n\n|\Z)"
    blocks: List[str] = re.findall(pattern, content, flags=re.DOTALL)

    cleaned: List[str] = []
    for block in blocks:
        text = re.sub(r"<[^>]+>", "", block)   
        text = re.sub(r"\s+", " ", text).strip() 
        cleaned.append(text)

    return " ".join(cleaned)


def _configure(api_key: str) -> genai.GenerativeModel:
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-pro")


# ────────────────────────── Generators ───────────────────────────
def generate_title(transcript: str, api_key: str) -> str:
    model = _configure(api_key)
    prompt = (
        "Craft a punchy, curiosity‑driven video title in NO MORE THAN 12 words. "
        "Front‑load strong keywords for SEO. "
        "Avoid hashtags, emojis, and excessive punctuation. "
        "Use a bit of click‑bait. "
        "Transcript excerpt:\n"
        f"{transcript}"
    )
    response = model.generate_content(prompt)
    return response.text.strip().replace("\n", " ")


def generate_description(transcript: str, api_key: str) -> str:

    model = _configure(api_key)
    prompt = (
        "Summarize the following video transcript into 2–3 concise paragraphs. "
        "Highlight the main topics, value for the viewer, and keep the tone engaging yet informative. "
        "DO NOT include hashtags, timestamps, or bullet points. "
        "Transcript:\n"
        f"{transcript}"
    )
    response = model.generate_content(prompt)
    return response.text.strip()


# ──────────────────────────── CLI ────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a video TITLE and/or DESCRIPTION from an .SRT file via Gemini"
    )
    parser.add_argument("srt_file", help=".srt subtitle file to analyse")
    parser.add_argument(
        "--api_key", "-k", help="Gemini API key (overrides GEMINI_API_KEY in .env)"
    )
    parser.add_argument(
        "--only",
        choices=["title", "description"],
        default="title",
        help="Generate only the title or only the description (default: title)",
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Gemini API key missing (use --api_key or set GEMINI_API_KEY in .env)")

    transcript = parse_srt(args.srt_file)

    if args.only == "title":
        print(generate_title(transcript, api_key))
    else:
        print(generate_description(transcript, api_key))


if __name__ == "__main__":
    main()
