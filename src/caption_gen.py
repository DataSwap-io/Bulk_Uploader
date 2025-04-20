import whisper
import os
from moviepy.editor import VideoFileClip
import datetime
import sys

# Paths
audio_path = "Audio.wav"


# Check if video path is provided as command line argument
if len(sys.argv) < 2:
    print("Error: Please provide a video file path as an argument.")
    print("Usage: python script.py /path/to/video.mp4")
    sys.exit(1)

video_path = sys.argv[1]
filename = sys.argv[2]


subtitle_path = f"C:\\Users\\thoma\\Downloads\\Bulk_Uploader - Copy\\src\\subtitles\\{filename}.srt" ######################AANPASSEN#############################

# Step 1: Extract audio from video
print("Extracting audio...")
try:
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
except Exception as e:
    print(f"Error extracting audio: {e}")
    sys.exit(1)

# Step 2: Load Whisper model
print("Loading Whisper model...")
try:
    model = whisper.load_model("base")  # Or "small", "medium", "large"
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    sys.exit(1)

# Step 3: Transcribe audio
print("Transcribing...")
try:
    result = model.transcribe(audio_path)
    print("Transcription completed successfully")
except Exception as e:
    print(f"Error during transcription: {e}")
    sys.exit(1)

# Helper function: format seconds to SRT timestamp
def format_timestamp(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

# Step 4: Write SRT with max 3 words per subtitle
print("Writing subtitles...")
with open(subtitle_path, "w", encoding="utf-8") as srt_file:
    subtitle_num = 1
    for segment in result["segments"]:
        text = segment["text"].strip()
        start = segment["start"]
        end = segment["end"]
        duration = end - start
        print(f"Processing segment starting at {start:.2f}s")
        words = text.split()
        chunk_size = 3
        chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
        chunk_count = len(chunks)
        
        # Distribute timing proportionally
        for i, chunk in enumerate(chunks):
            chunk_text = ' '.join(chunk)
            chunk_start = start + (i / chunk_count) * duration
            chunk_end = start + ((i + 1) / chunk_count) * duration
            start_str = format_timestamp(chunk_start)
            end_str = format_timestamp(chunk_end)
            srt_file.write(f"{subtitle_num}\n{start_str} --> {end_str}\n{chunk_text}\n\n")
            subtitle_num += 1

print("Subtitles saved to", subtitle_path)
print("Cleaning up temporary files...")
try:
    os.remove(audio_path)
    print(f"Temporary audio file {audio_path} removed")
except:
    print(f"Could not remove temporary audio file {audio_path}")