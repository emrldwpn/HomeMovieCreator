import os
import ffmpeg
from timestamp_utils import extract_date_from_filename, extract_time_from_filename

input_dir = r"C:\Users\ericp\Desktop\videos-test"
output_dir = r"C:\Users\ericp\Desktop\videos-test\output"
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
    
add_timestamp_to_videos(input_dir, output_dir)