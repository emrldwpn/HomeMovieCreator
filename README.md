# Home Movie Creator

This script processes and standardizes home videos by fixing aspect ratios, adding timestamps, and concatenating processed videos into a final output file. It supports handling vertical videos, applying pillarboxing, and ensuring consistent encoding settings.

## Features
- Standardizes video aspect ratio and frame rate
- Detects and corrects vertical videos with pillarboxing
- Adds timestamps extracted from filenames
- Supports batch processing of videos in a directory
- Combines processed videos into a final output file
- Allows users to override default settings using command-line arguments

## Requirements
- Python 3.8+
- FFmpeg installed and available in the system PATH

## Installation
1. Clone this repository:
   ```
   git clone https://github.com/emrldwpn/HomeMovieCreator.git
   cd HomeMovieCreator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Run the script with command-line arguments to specify input/output directories and processing parameters.

```
python main.py --input_dir=/path/to/videos --output_dir=/path/to/output --output_video=final.mp4 --width=1920 --height=1080 --fps=30 --ts_duration=5 --ts_fontsize=60 --ts_padding=30
```

### Arguments:
| Argument         | Description                          | Default |
|-----------------|--------------------------------------|---------|
| `--input_dir`   | Path to input video directory       | `D:\Videos` |
| `--output_dir`  | Path to output directory           | `$input_dir\output` |
| `--output_video` | Name of final output video file   | `home_videos.mp4` |
| `--width`       | Target video width                  | `1920` |
| `--height`      | Target video height                 | `1080` |
| `--fps`         | Target frames per second            | `30` |
| `--ts_duration` | Timestamp duration in seconds       | `5` |
| `--ts_fontsize` | Timestamp font size                 | `60` |
| `--ts_padding`  | Padding around timestamp text       | `30` |

## Example Usage
To process videos in `~/Videos`, save the output to `~/Videos/output`, and create a final video file `my_home_video.mp4`:
```
python main.py --input_dir=~/Videos --output_dir=~/Videos/output --output_video=my_home_video.mp4
```

## Error Handling
- The script will validate all input arguments.
- If the input directory does not exist, an error will be raised.
- The output directory will be created if it does not exist.
- Invalid filenames or non-numeric values for parameters will cause the script to abort.

## Notes
- Ensure FFmpeg is installed and accessible from the command line.
- The script automatically creates the output directory if it doesn't exist.
- Video processing may take time depending on file sizes and system performance.

## License
This project is open-source and available under the MIT License.