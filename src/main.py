import subprocess
import os
import sys
from openpyxl import Workbook, load_workbook
import time
from datetime import datetime, timedelta

from descriptionate import parse_srt, generate_description_with_hashtags

if len(sys.argv) < 3:
    print("Error: Please provide a youtube link and api key as arguments.")
    print("Usage: python main.py '<URL>'")
    sys.exit(1)

url = sys.argv[1]
api_key = sys.argv[2]
#url = 'https://www.youtube.com/watch?v=EiHwEq-B9II'

output_dir= 'outputvid'
excel_path = 'final\\info.xlsx'

#
# PAS DEZE AAN
#
subtitle_dir= "C:\\Users\\thoma\\Downloads\\Bulk_Uploader - Copy\\src\\subtitles"

def clear_subtitles():
    print('[INFO] Clearing subtitle files...')
    for item in os.listdir(subtitle_dir):
        item_path = os.path.join(subtitle_dir, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)

def get_target_timestamp(iteration: int):
    target_hours = [12, 14, 17]
    now = datetime.now()
    today = now.date()
    
    # Figure out which day and hour based on iteration
    day_offset = iteration // len(target_hours)
    hour_index = iteration % len(target_hours)
    
    target_time = datetime.combine(today + timedelta(days=day_offset), datetime.min.time()) + timedelta(hours=target_hours[hour_index])
    
    return int(target_time.timestamp())

# Genereer videos
print('-- Extracting Clips and Combining --')
proc_clip = subprocess.run(['node', 'main_combiner.js', url], capture_output=True, text=True)
print(proc_clip.stdout)

# Voeg subtitles toe
print('-- Adding Subtitles --')

# Create excel file
wb = Workbook()
ws = wb.active
ws.append(["File Path", "Description", "Schedule"])  # Add header row
wb.save(excel_path)

# Load excel file
wb = load_workbook(excel_path)
ws = wb.active

for i, filename in enumerate(os.listdir(output_dir)):
    file_path = os.path.join(output_dir, filename)
    if os.path.isfile(file_path):
        print(f'Processing: {file_path}')
        proc_subtitle = subprocess.run(['python', 'caption_gen.py', file_path, os.path.splitext(filename)[0]], capture_output=True, text=True)
        print(proc_subtitle.stdout)
        print(f'Subtitling: {file_path}')
        proc_captioning = subprocess.run(['python', 'subtitler.py',
                                          file_path,
                                          f'subtitles\\{os.path.splitext(filename)[0]}.srt',
                                         '-o', f'final\\{os.path.splitext(filename)[0]}_subtitled.mp4',
                                         '--position', 'middle'],
                                         capture_output=True, text=True)
        print(proc_captioning.stdout)

        # Add both the filepath, description and upload time to an excel file.
        subtitle_text = parse_srt(f'subtitles\\{os.path.splitext(filename)[0]}.srt')

        print('[INFO] Generating description...')
        vid_description = generate_description_with_hashtags(subtitle_text, api_key)

        ws.append([f'final\\{os.path.splitext(filename)[0]}_subtitled.mp4', vid_description, get_target_timestamp(i)])

wb.save(excel_path)

# Verwijder alle .srt bestanden (Noodzakelijk)
clear_subtitles()
