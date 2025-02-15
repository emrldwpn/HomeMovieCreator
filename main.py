import os
import ffmpeg
from timestamp_utils import extract_date_from_filename, extract_time_from_filename

input_dir = r"I:\Phoenix Home Videos"
output_dir = r"I:\Phoenix Home Videos\output"
final_output_file = r"I:\Phoenix Home Videos\output\combined_video.mp4"
os.makedirs(output_dir, exist_ok=True)


def process_and_standardize_videos(input_dir, output_dir, target_width=1920, target_height=1080, target_fps=30):
    """Fixes aspect ratio issues, pillarboxes vertical videos, and standardizes encoding."""
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".wmv")):
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

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
        sar = video_stream.get('sample_aspect_ratio', '1:1')  # Get SAR, default to 1:1
        dar = video_stream.get('display_aspect_ratio', '1:1')  # Get DAR, default to 1:1

        print(f"📏 Original Resolution: {width}x{height}, SAR: {sar}, DAR: {dar}")

        # Define video input and normalize SAR
        video = ffmpeg.input(input_path).filter('fps', fps=target_fps, round='up')  # Normalize frame rate
        video = video.filter('setsar', '1/1')  # Ensure square pixels
            
        rotation = 0
        displaymatrix = 0
        if "side_data_list" in video_stream:
            for side_data in video_stream["side_data_list"]:
                if "rotation" in side_data:
                    rotation = side_data["rotation"]
                if "displaymatrix" in side_data:
                    displaymatrix = side_data["rotation"]
                    print(f"displaymatrix = {displaymatrix}") 
        
        is_vertical = (width < height) or (rotation in [90, 270]) or (displaymatrix) in ([90, -90])
           
        print(f"🔍 Rotation: {rotation}°, Is Vertical: {is_vertical}")
        
        if is_vertical:
            print(f"🔹 Pillarboxing vertical video: {filename}")

            video = video.filter('setdar', '16/9')
            
            # Scale while maintaining aspect ratio
            video = video.filter('scale', 'min(iw*1080/ih,1920)', 'min(1080, ih*1920/iw)')
            video = video.filter('pad', target_width, target_height, '(ow-iw)/2', '(oh-ih)/2', color='black')

        # Encode and save the processed file, forcing SAR at the bitstream level
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
            print(f"❌ Error processing {filename}")
            print(e.stderr.decode() if e.stderr else "No detailed error message available.")

    print("🎬 All videos processed successfully!")
    

def add_timestamp_to_video(filename, video, duration=5, font_size=60, padding=30):
            
    try:
        date=extract_date_from_filename(filename)
        time=extract_time_from_filename(filename)
    except ValueError as e:
        print(f"❌ Error parsing datetime from {filename}")
        print(e)
        return

    try:
        duration_str = str(duration)
        
        date_y = f"h-{font_size * 2 + padding}"
        time_y = f"h-{font_size + padding}"

        video = video.filter(
            "drawtext", text=date, fontcolor="white", fontsize=font_size,
            x="w-text_w-10", y=date_y, enable=f"lte(t,{duration_str})"
        )
        video = video.filter(
            "drawtext", text=time, fontcolor="white", fontsize=font_size,
            x="w-text_w-10", y=time_y, enable=f"lte(t,{duration_str})"
        )

    except ffmpeg.Error as e:
        print(f"❌ Error processing {filename}")
        print("------ FFmpeg Error Output ------")
        print(e.stderr.decode() if e.stderr else "No detailed error message available.")
        print("---------------------------------")
        
    return video
    
    
def combine_videos(output_folder, final_output_file):
    """
    Combine all processed video files in the output folder into a single video.
    
    :param output_folder: Path to the folder containing processed video files.
    :param final_output_file: Path for the final combined video file.
    """
    video_files = sorted(
        [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".mp4")]
    )

    if not video_files:
        print("No video files found to combine.")
        return

    concat_file_path = os.path.join(output_folder, "videos.txt")
    with open(concat_file_path, "w") as concat_file:
        for video in video_files:
            concat_file.write(f"file '{video}'\n")

    # Run FFmpeg concatenation command
    try:
        ffmpeg.input(concat_file_path, format="concat", safe=0).output(
            final_output_file, c="copy"
        ).run(overwrite_output=True)
        print(f"✅ Combined video saved as: {final_output_file}")
        cleanup(concat_file_path, video_files)
        print(f"✅ Performed cleanup tasks")
    except ffmpeg.Error as e:
        print(f"❌ Error combining videos: {e.stderr.decode()}")
        
def cleanup(concat_file_path, video_files):
    """
    Cleanup the temporary files created.
    
    :param concat_file_path: Path to the file containing list of video files to concat.
    :param video_files: List of video files to be cleaned up.
    """
    try:
        if os.path.exists(concat_file_path):
            os.remove(concat_file_path)
            print(f"🗑️ Deleted temporary file: {concat_file_path}")

        for video in video_files:
            if video != final_output_file:
                os.remove(video)
                print(f"🗑️ Deleted temporary video: {video}")

    except Exception as cleanup_error:
        print(f"❌ Error during cleanup: {cleanup_error}")
    
    
process_and_standardize_videos(input_dir, output_dir)
combine_videos(output_dir, final_output_file)