from datetime import datetime

def extract_date_from_filename(filename):
    """
    Extracts and formats the date from a filename (YYYYMMDD_HHMMSS format).
    
    :param filename: The video filename (e.g., '20200717_135135.mp4')
    :return: Formatted date string (e.g., 'July 17, 2020')
    :raises ValueError: If the date cannot be extracted or formatted properly.
    """
    try:
        date_part = filename.split("_")[0]
        date_obj = datetime.strptime(date_part, "%Y%m%d")
        
        return date_obj.strftime("%B %d, %Y")
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid filename format for date extraction: {filename}") from e


def extract_time_from_filename(filename):
    """
    Extracts and formats the time from a filename (YYYYMMDD_HHMMSS format).
    
    :param filename: The video filename (e.g., '20200717_135135.mp4')
    :return: Formatted time string (e.g., '1:51:35 PM')
    :raises ValueError: If the time cannot be extracted or formatted properly.
    """
    try:
        time_part = filename.split("_")[1][:6]
        time_obj = datetime.strptime(time_part, "%H%M%S")
        formatted_time = time_obj.strftime("%I:%M:%S %p")

        return formatted_time.lstrip("0") if formatted_time.startswith("0") else formatted_time
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid filename format for time extraction: {filename}") from e