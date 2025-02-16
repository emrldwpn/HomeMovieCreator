import os
from config import FINAL_OUTPUT_FILE

def cleanup_temp_files(concat_file_path, video_files):
    """
    Cleans up temporary files used during video processing.
    
    :param concat_file_path: Path to the file containing list of video files to concatenate.
    :param video_files: List of processed video files.
    """
    try:
        if os.path.exists(concat_file_path):
            os.remove(concat_file_path)
            print(f"🗑️ Deleted temporary file: {concat_file_path}")

        for video in video_files:
            if video != FINAL_OUTPUT_FILE:
                os.remove(video)
                print(f"🗑️ Deleted temporary video: {video}")

    except Exception as cleanup_error:
        print(f"❌ Error during cleanup: {cleanup_error}")
