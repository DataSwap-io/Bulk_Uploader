from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.config as mpy_conf
import sys

mpy_conf.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"}) #####AANPASSEN; BASIC BIJ WINDOWS/LINUX ANDER VERHAAL
video = VideoFileClip(sys.argv[1])
script = sys.argv[2]

# Define subtitle style
def subtitle_generator(txt):
    return TextClip(
        txt,
        font="fonts/Montserrat-Black.otf",

        fontsize=80,
        color="#ffe88c",
        stroke_color="black",
        stroke_width=3,
        method="caption",
        size=(980, None),
        align="center"
    )

subtitles = SubtitlesClip(script, subtitle_generator)
final_video = CompositeVideoClip([
    video,
    subtitles.set_position(('center', video.h - 580)) 
])

final_video.write_videofile("video_with_subtitles.mp4", codec='libx264', audio_codec='aac')
