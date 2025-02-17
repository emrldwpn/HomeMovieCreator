import os
import argparse
from config.validation import validate_config

# Default Input and Output Directories
settings = {
    "input_dir": r"D:\Videos",
    "output_dir": r"D:\Videos\output",
    "final_output_file": "home_videos.mp4",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "ts_duration": 5,  # seconds
    "ts_fontsize": 60,
    "ts_padding": 30,
}

parser = argparse.ArgumentParser(description="Process and standardize home videos.")
parser.add_argument("--input_dir", type=str, help="Path to the input video directory.")
parser.add_argument("--output_dir", type=str, help="Path to the output directory.")
parser.add_argument("--output_video", type=str, help="Name of the final concatenated video file.")
parser.add_argument("--width", type=int, help="Target video width.")
parser.add_argument("--height", type=int, help="Target video height.")
parser.add_argument("--fps", type=int, help="Target video FPS.")
parser.add_argument("--ts_duration", type=int, help="Timestamp duration.")
parser.add_argument("--ts_fontsize", type=int, help="Timestamp font size.")
parser.add_argument("--ts_padding", type=int, help="Timestamp padding.")
args = parser.parse_args()

# Apply user arguments, if provided
if args.input_dir:
    settings["input_dir"] = args.input_dir
    settings["output_dir"] = os.path.join(settings["input_dir"], "output")

if args.output_dir:
    settings["output_dir"] = args.output_dir

if args.output_video:
    settings["final_output_file"] = args.output_video
    if not settings["final_output_file"].lower().endswith(".mp4"):
        settings["final_output_file"] += ".mp4"

if args.width:
    settings["width"] = args.width

if args.height:
    settings["height"] = args.height

if args.fps:
    settings["fps"] = args.fps

if args.ts_duration:
    settings["ts_duration"] = args.ts_duration

if args.ts_fontsize:
    settings["ts_fontsize"] = args.ts_fontsize

if args.ts_padding:
    settings["ts_padding"] = args.ts_padding

validate_config(settings)
