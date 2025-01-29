import os
import ffmpeg
from timestamp_utils import extract_date_from_filename, extract_time_from_filename

input_dir = r"C:\Users\ericp\Desktop\videos-test"
output_dir = r"C:\Users\ericp\Desktop\videos-test\output"
final_output_file = r"C:\Users\ericp\Desktop\videos-test\output\combined_video.mp4"
os.makedirs(output_dir, exist_ok=True)

def add_timestamp_to_videos(input_dir, output_dir, duration=2.5):
    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".wmv")):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{filename}")
                        
            if os.path.exists(output_path):
                print(f"⏩ Skipping {filename} (already processed)")
                continue

            print(f"Processing: {filename}")
            
            try:
                date=extract_date_from_filename(filename)
                time=extract_time_from_filename(filename)
            except ValueError as e:
                print(f"❌ Error parsing datetime from {filename}")
                print(e)
                continue

            try:
                video = ffmpeg.input(input_path)
                video = video.filter("drawtext", text=date, fontcolor="white", fontsize=24,
                                     x="w-text_w-10", y="h-text_h-50", enable="lte(t,2.5)")
                video = video.filter("drawtext", text=time, fontcolor="white", fontsize=24,
                                     x="w-text_w-10", y="h-text_h-25", enable="lte(t,2.5)")
                ffmpeg.output(video, output_path, vcodec="libx264", crf=18, preset="medium",
                              acodec="copy", map="0:a?").run(overwrite_output=True)

                print(f"✅ Processed: {output_path}")

            except ffmpeg.Error as e:
                print(f"❌ Error processing {filename}")
                print("------ FFmpeg Error Output ------")
                print(e.stderr.decode() if e.stderr else "No detailed error message available.")
                print("---------------------------------")

    print("✅ All videos processed successfully.")
    
    
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
    
    
add_timestamp_to_videos(input_dir, output_dir)
combine_videos(output_dir, final_output_file)