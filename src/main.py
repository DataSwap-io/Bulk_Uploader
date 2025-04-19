import subprocess
import os
import sys


if len(sys.argv) < 2:
    print("Error: Please provide a youtube link as an argument.")
    print("Usage: python main.py '<URL>'")
    sys.exit(1)

url = sys.argv[1]
#url = 'https://www.youtube.com/watch?v=EiHwEq-B9II'

output_dir= 'outputvid'

#
# PAS DEZE AAN
#
subtitle_dir= "C:\\Users\\thoma\\Downloads\\Bulk_Uploader - Copy\\src\\subtitles"

def clear_subtitles():
    for item in os.listdir(subtitle_dir):
        item_path = os.path.join(subtitle_dir, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)

# Genereer videos
print('-- Extracting Clips and Combining --')
proc_clip = subprocess.run(['node', 'main_combiner.js', url], capture_output=True, text=True)
print(proc_clip.stdout)

# Voeg subtitles toe
print('-- Adding Subtitles --')

for filename in os.listdir(output_dir):
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

# Verwijder alle .srt bestanden (Noodzakelijk)
clear_subtitles()
