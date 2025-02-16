import os
import argparse

# Default Input and Output Directories
INPUT_DIR = r"D:\Videos"
OUTPUT_DIR = os.path.join(INPUT_DIR, "output")
FINAL_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "home_videos.mp4")

# Video Processing Parameters
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
TARGET_FPS = 30
TIMESTAMP_DURATION = 5  # seconds
TIMESTAMP_FONT_SIZE = 60
TIMESTAMP_PADDING = 30

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

if args.input_dir:
    INPUT_DIR = args.input_dir
    OUTPUT_DIR = os.path.join(INPUT_DIR, "output")
    FINAL_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "home_videos.mp4")

if args.output_dir:
    OUTPUT_DIR = args.output_dir
    FINAL_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "home_videos.mp4")

if args.output_video:
    FINAL_OUTPUT_FILE = os.path.join(OUTPUT_DIR, args.output_video)
    if not FINAL_OUTPUT_FILE.lower().endswith(".mp4"):
        FINAL_OUTPUT_FILE +=  ".mp4"

if args.width:
    TARGET_WIDTH = args.width

if args.height:
    TARGET_HEIGHT = args.height

if args.fps:
    TARGET_FPS = args.fps

if args.ts_duration:
    TIMESTAMP_DURATION = args.ts_duration

if args.ts_fontsize:
    TIMESTAMP_FONT_SIZE = args.ts_fontsize

if args.ts_padding:
    TIMESTAMP_PADDING = args.ts_padding