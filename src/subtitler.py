from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.config as mpy_conf
import sys
import os
import argparse

def setup_argparse():
    parser = argparse.ArgumentParser(description='Add subtitles to a video file.')
    parser.add_argument('input_video', help='Path to the input video file')
    parser.add_argument('subtitle_file', help='Path to the subtitle file (.srt format)')
    parser.add_argument('--output', '-o', default=None, help='Output video filename (default: input_name_subtitled.mp4)')
    parser.add_argument('--font', default='Montserrat-Black.otf', help='Font to use for subtitles')
    parser.add_argument('--fontsize', type=int, default=80, help='Font size for subtitles')
    parser.add_argument('--color', default='#ffe88c', help='Font color for subtitles (hex code)')
    parser.add_argument('--position', default='bottom', choices=['bottom', 'middle', 'custom'], 
                        help='Position of subtitles')
    parser.add_argument('--custom-position', type=int, default=None, 
                        help='Custom position from bottom in pixels (if --position=custom)')
    parser.add_argument('--preview', action='store_true', help='Generate a preview image of subtitles without rendering')
    return parser.parse_args()

def configure_imagemagick():
    possible_paths = [
        r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",  # Windows
        r"/usr/local/bin/convert",  # Mac/Linux
        r"/usr/bin/convert"  # Linux
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            mpy_conf.change_settings({"IMAGEMAGICK_BINARY": path})
            print(f"Using ImageMagick at: {path}")
            return True
    
    print("WARNING: Could not find ImageMagick. Please install it or specify the path manually.")
    return False

def subtitle_generator(txt, args):
    font_path = f"fonts/{args.font}" if not os.path.exists(args.font) else args.font
    
    return TextClip(
        txt,
        font=font_path,
        fontsize=args.fontsize,
        color=args.color,
        stroke_color="black",
        stroke_width=3,
        method="caption",
        size=(min(1020, int(video.w * 0.8)), None),
        align="center"
    )

def calculate_position(args, video_height):
    """Calculate the subtitle position based on user preferences"""
    if args.position == 'bottom':
        return ('center', 'bottom')
    elif args.position == 'middle':
        return ('center', video_height - int(video_height/2))
    elif args.position == 'custom' and args.custom_position is not None:
        return ('center', video_height - args.custom_position)
    else:
        return ('center', 'bottom')

def generate_preview(generator_func, output_path="subtitle_preview.png"):
    """Generate a preview image of how subtitles will look"""
    generator_func("This is a preview of how your subtitles will look").save_frame(output_path)
    print(f"Preview image saved to {output_path}")

def main():
    args = setup_argparse()
    
    configure_imagemagick()
    
    global video
    try:
        video = VideoFileClip(args.input_video)
    except Exception as e:
        print(f"Error loading video file: {e}")
        sys.exit(1)
    
    generator = lambda txt: subtitle_generator(txt, args)
    
    if args.preview:
        generate_preview(generator)
        sys.exit(0)
    
    try:
        subtitles = SubtitlesClip(args.subtitle_file, generator)
    except Exception as e:
        print(f"Error loading subtitle file: {e}")
        sys.exit(1)
    
    position = calculate_position(args, video.h)
    
    final_video = CompositeVideoClip([
        video,
        subtitles.set_position(position)
    ])
    
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(os.path.basename(args.input_video))[0]
        output_file = f"{base_name}_subtitled.mp4"
    
    print(f"Rendering video with subtitles to {output_file}...")
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac')
    print("Rendering complete!")

if __name__ == "__main__":
    main()