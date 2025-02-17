import os
import ffmpeg
import shutil
from .cleanup import cleanup_temp_files
from config import settings
from utils.video_utils import get_rotation_info, is_video_vertical
from utils.timestamp_utils import extract_date_from_filename, extract_time_from_filename

def process_and_standardize_videos():
    """Fixes aspect ratio issues, pillarboxes vertical videos, and standardizes encoding."""
    
    for filename in os.listdir(settings["input_dir"]):
        if not filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".wmv")):
            continue

        input_path = os.path.join(settings["input_dir"], filename)
        output_path = os.path.join(settings["output_dir"], filename)

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
        video = ffmpeg.input(input_path).filter('fps', fps=settings["fps"], round='up')  
        video = video.filter('setsar', '1/1')  # Ensure square pixels
        
        if is_vertical:
            print(f"🔹 Pillarboxing vertical video: {filename}")
            video = video.filter('setdar', '16/9')
            video = video.filter('scale', 'min(iw*1080/ih,1920)', 'min(1080, ih*1920/iw)')
            video = video.filter('pad', settings["width"], settings["height"], '(ow-iw)/2', '(oh-ih)/2', color='black')

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


def add_timestamp_to_video(filename, video):
    """
    Adds a timestamp overlay to the video.
    
    :param filename: The filename of the video to add the timestamp to.
    :param video: The video stream to apply to the timestamp to.
    """

    try:
        date = extract_date_from_filename(filename)
        time = extract_time_from_filename(filename)
    except ValueError as e:
        print(f"❌ Error parsing datetime from {filename}: {e}")
        return video  # Return original video if timestamp extraction fails

    duration_str = str(settings["ts_duration"])
    date_y = f"h-{settings["ts_fontsize"] * 2 + settings["ts_padding"]}"
    time_y = f"h-{settings["ts_fontsize"] + settings["ts_padding"]}"

    video = video.filter(
        "drawtext", text=date, fontcolor="white", fontsize=settings["ts_fontsize"],
        x="w-text_w-10", y=date_y, enable=f"lte(t,{duration_str})"
    )
    video = video.filter(
        "drawtext", text=time, fontcolor="white", fontsize=settings["ts_fontsize"],
        x="w-text_w-10", y=time_y, enable=f"lte(t,{duration_str})"
    )

    return video
    

def combine_videos():
    """Combines all processed videos into one final output file."""

    video_files = sorted(
        [os.path.join(settings["output_dir"], f) for f in os.listdir(settings["output_dir"]) if f.endswith(".mp4")]
    )

    if not video_files:
        print("No video files found to combine.")
        return

    concat_file_path = os.path.join(settings["output_dir"], "videos.txt")
    with open(concat_file_path, "w") as concat_file:
        for video in video_files:
            concat_file.write(f"file '{video}'\n")

    try:
        ffmpeg.input(concat_file_path, format="concat", safe=0).output(
            os.path.join(settings["output_dir"], settings["final_output_file"]), c="copy"
        ).run(overwrite_output=True)
        print(f"✅ Combined video saved as: {settings["final_output_file"]}")
        cleanup_temp_files(concat_file_path, video_files)
        print(f"✅ Performed cleanup tasks")

    except ffmpeg.Error as e:
        print(f"❌ Error combining videos: {e.stderr.decode()}")