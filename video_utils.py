def get_rotation_info(video_stream):
    """Extracts rotation and displaymatrix info from video stream metadata."""
    
    rotation = 0
    displaymatrix = 0

    if "side_data_list" in video_stream:
        for side_data in video_stream["side_data_list"]:
            if "rotation" in side_data:
                rotation = side_data["rotation"]
            if "displaymatrix" in side_data:
                displaymatrix = side_data["rotation"]
    
    return rotation, displaymatrix

def is_video_vertical(width, height, rotation, displaymatrix):
    """Determines if a video is vertical based on rotation and dimensions."""
    
    return (width < height) or (rotation in [90, 270]) or (displaymatrix in [90, -90])
