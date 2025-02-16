import os
import ffmpeg
from config import FINAL_OUTPUT_FILE, INPUT_DIR, OUTPUT_DIR, TARGET_WIDTH, TARGET_HEIGHT, TARGET_FPS, TIMESTAMP_DURATION, TIMESTAMP_FONT_SIZE, TIMESTAMP_PADDING
from cleanup import cleanup_temp_files
from video_utils import get_rotation_info, is_video_vertical
from timestamp_utils import extract_date_from_filename, extract_time_from_filename

def process_and_standardize_videos():
    """Fixes aspect ratio issues, pillarboxes vertical videos, and standardizes encoding."""
    
    create_output_dir(OUTPUT_DIR)
    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".wmv")):
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(output_path):
            print(f"⏩ Skipping {filename} (already processed)")
            continue

        print(f"📌 Processing: {filename}")

        # Extract video metadata
        probe = ffmpeg.probe(input_path)
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        if not video_stream:
            print(f"❌ No video stream found in {filename}")
            continue

        width, height = int(video_stream['width']), int(video_stream['height'])
        rotation, displaymatrix = get_rotation_info(video_stream)
        is_vertical = is_video_vertical(width, height, rotation, displaymatrix)

        print(f"📏 Resolution: {width}x{height}, Rotation: {rotation}°, Is Vertical: {is_vertical}")

        # Define video input and normalize SAR
        video = ffmpeg.input(input_path).filter('fps', fps=TARGET_FPS, round='up')  
        video = video.filter('setsar', '1/1')  # Ensure square pixels
        
        if is_vertical:
            print(f"🔹 Pillarboxing vertical video: {filename}")
            video = video.filter('setdar', '16/9')
            video = video.filter('scale', 'min(iw*1080/ih,1920)', 'min(1080, ih*1920/iw)')
            video = video.filter('pad', TARGET_WIDTH, TARGET_HEIGHT, '(ow-iw)/2', '(oh-ih)/2', color='black')

        # Encode and save the processed file
        try:
            video = add_timestamp_to_video(filename, video)
            ffmpeg.output(
                video, output_path,
                vcodec="libx264", crf=18, preset="slow",
                acodec="aac", audio_bitrate="192k", pix_fmt="yuv420p", format="mp4", map="0:a?",
                **{'bsf:v': 'h264_metadata=sample_aspect_ratio=1/1'}
            ).run(overwrite_output=True)
            print(f"✅ Processed: {filename}")

        except ffmpeg.Error as e:
            print(f"❌ Error processing {filename}: {e.stderr.decode() if e.stderr else 'No detailed error message'}")

    print("🎬 All videos processed successfully!")
    
    
def create_output_dir(output_dir):
    """Create the output directory, cleaning it up first if it already exists."""
    
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Delete file or symlink
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Delete subdirectory
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
    
    print(f"making dir {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def add_timestamp_to_video(filename, video):
    """Adds a timestamp overlay to the video."""

    try:
        date = extract_date_from_filename(filename)
        time = extract_time_from_filename(filename)
    except ValueError as e:
        print(f"❌ Error parsing datetime from {filename}: {e}")
        return video  # Return original video if timestamp extraction fails

    duration_str = str(TIMESTAMP_DURATION)
    date_y = f"h-{TIMESTAMP_FONT_SIZE * 2 + TIMESTAMP_PADDING}"
    time_y = f"h-{TIMESTAMP_FONT_SIZE + TIMESTAMP_PADDING}"

    video = video.filter(
        "drawtext", text=date, fontcolor="white", fontsize=TIMESTAMP_FONT_SIZE,
        x="w-text_w-10", y=date_y, enable=f"lte(t,{duration_str})"
    )
    video = video.filter(
        "drawtext", text=time, fontcolor="white", fontsize=TIMESTAMP_FONT_SIZE,
        x="w-text_w-10", y=time_y, enable=f"lte(t,{duration_str})"
    )

    return video
    

def combine_videos():
    """Combines all processed videos into one final output file."""

    video_files = sorted(
        [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith(".mp4")]
    )

    if not video_files:
        print("No video files found to combine.")
        return

    concat_file_path = os.path.join(OUTPUT_DIR, "videos.txt")
    with open(concat_file_path, "w") as concat_file:
        for video in video_files:
            concat_file.write(f"file '{video}'\n")

    try:
        ffmpeg.input(concat_file_path, format="concat", safe=0).output(
            FINAL_OUTPUT_FILE, c="copy"
        ).run(overwrite_output=True)
        print(f"✅ Combined video saved as: {FINAL_OUTPUT_FILE}")
        cleanup_temp_files(concat_file_path, video_files)
        print(f"✅ Performed cleanup tasks")

    except ffmpeg.Error as e:
        print(f"❌ Error combining videos: {e.stderr.decode()}")