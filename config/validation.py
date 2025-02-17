import os
import re
import shutil

def validate_config(config):
    """Validates config settings after applying user-provided arguments."""
    
    input_dir = config["input_dir"]
    output_dir = config["output_dir"]
    final_output_file = config["final_output_file"]

    # Check if input directory exists
    if not os.path.isdir(input_dir):
        raise ValueError(f"❌ Input directory does not exist: {input_dir}")

    # Ensure output directory can be created
    create_output_dir(output_dir)

    # Validate output video filename
    if not is_valid_filename(final_output_file):
        raise ValueError(f"❌ Invalid output video filename: {final_output_file}. Avoid using special characters.")

    numeric_configs = ["width", "height", "fps", "ts_duration", "ts_fontsize", "ts_padding"]

    for name in numeric_configs:
        value = config[name]
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError(f"❌ Invalid value for {name}: {value}. Must be a number greater than 0.")

    
def create_output_dir(output_dir):
    """Create the output directory, cleaning it up first if it already exists."""
    
    if not os.path.isabs(output_dir):  
        raise ValueError(f"❌ Output directory is not a valid absolute path: {output_dir}")
        
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
    
    print(f"making dir {output_dir}")
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        raise ValueError(f"❌ Failed to create output directory: {output_dir}. Error: {e}")


def is_valid_filename(filename):
    """Check if the filename is valid (no special characters except dashes/underscores)."""
    
    return re.match(r'^[\w\-. ]+$', filename) is not None
