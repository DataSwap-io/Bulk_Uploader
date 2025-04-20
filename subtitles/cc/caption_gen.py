import whisper
import os
from moviepy.editor import VideoFileClip
import datetime
import sys


# Paths
#video_path = "input_vid.mp4"
audio_path = "Audio.wav"
subtitle_path = "output.srt"

video_path = sys.argv[1]

print("Extracting audio...")
video = VideoFileClip(video_path)
video.audio.write_audiofile(audio_path)

print("Loading Whisper model...")
model = whisper.load_model("base")
print("Transcribing...")
result = model.transcribe(audio_path)

def format_timestamp(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

print("Writing subtitles...")
with open(subtitle_path, "w", encoding="utf-8") as srt_file:
    subtitle_num = 1

    for segment in result["segments"]:
        text = segment["text"].strip()
        start = segment["start"]
        end = segment["end"]
        duration = end - start

        words = text.split()
        chunk_size = 3
        chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
        chunk_count = len(chunks)

        for i, chunk in enumerate(chunks):
            chunk_text = ' '.join(chunk)
            chunk_start = start + (i / chunk_count) * duration
            chunk_end = start + ((i + 1) / chunk_count) * duration

            start_str = format_timestamp(chunk_start)
            end_str = format_timestamp(chunk_end)

            srt_file.write(f"{subtitle_num}\n{start_str} --> {end_str}\n{chunk_text}\n\n")
            subtitle_num += 1

print("Subtitles saved to", subtitle_path)
