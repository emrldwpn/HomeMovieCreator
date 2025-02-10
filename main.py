import os
import ffmpeg
from timestamp_utils import extract_date_from_filename, extract_time_from_filename

# Paths
input_dir = r"C:\Users\ericp\Desktop\videos-test"
output_dir = r"C:\Users\ericp\Desktop\videos-test\output"
final_output_file = r"C:\Users\ericp\Desktop\videos-test\output\combined_video.mp4"
os.makedirs(output_dir, exist_ok=True)

def get_resolution(video_file):
    """Extract width, height, and rotation metadata from a video file."""
    probe = ffmpeg.probe(video_file)
    video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
    if not video_stream:
        raise ValueError(f"No video stream found in {video_file}")

    width = int(video_stream['width'])
    height = int(video_stream['height'])

    # Detect rotation metadata
    rotation = int(video_stream.get('tags', {}).get('rotate', 0))

    return width, height, rotation
    

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



def batch_concatenate(output_directory, final_output_file, batch_size=5):
    # Gather all video files from the output directory
    video_files = [
        os.path.join(output_directory, file)
        for file in os.listdir(output_directory)
        if file.endswith(".mp4")
    ]
    
    if not video_files:
        raise ValueError("No video files found in the specified directory.")

    temp_files = []
    batch_count = 0

    # Process batches
    for i in range(0, len(video_files), batch_size):
        batch = video_files[i:i + batch_size]
        batch_concat_file = os.path.join(output_directory, f"batch_{batch_count}.txt")
        with open(batch_concat_file, "w") as f:
            for file in batch:
                f.write(f"file '{file}'\n")
        
        intermediate_output = os.path.join(output_directory, f"batch_{batch_count}.mp4")
        temp_files.append(intermediate_output)

        # Run FFmpeg to concatenate the current batch with proper scaling and padding
        ffmpeg.input(batch_concat_file, format="concat", safe=0).output(
            intermediate_output, vcodec="libx264", acodec="aac", pix_fmt="yuv420p"
        ).run(overwrite_output=True)
        
        os.remove(batch_concat_file)
        batch_count += 1

    # Final concatenation with scaling & pillarboxing to 1920x1080
    final_concat_file = os.path.join(output_directory, "final_concat_list.txt")
    with open(final_concat_file, "w") as f:
        for temp_file in temp_files:
            f.write(f"file '{temp_file}'\n")

    # Apply scaling & pillarboxing correctly
    ffmpeg.input(final_concat_file, format="concat", safe=0).output(
        final_output_file, vcodec="libx264", acodec="aac", pix_fmt="yuv420p"
        # final_output_file, vcodec="libx264", acodec="aac", pix_fmt="yuv420p",
        # vf="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black"
    ).run(overwrite_output=True)

    # Cleanup temporary files
    for temp_file in temp_files:
        os.remove(temp_file)
    os.remove(final_concat_file)

    print(f"✅ Final video created: {final_output_file}")



# Run the process
process_and_standardize_videos(input_dir, output_dir)
batch_concatenate(output_dir, final_output_file, batch_size=5)
