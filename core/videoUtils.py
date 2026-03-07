import glob
import os
import sys
import argparse
import subprocess

def create_video_from_images(folder_path, output_path, pattern="image_%04d.png", fps=30, codec="libx264", crf=23):
    """
    Creates a video from a sequence of images using ffmpeg.
    
    Args:
        folder_path: Path to the folder containing the image sequence.
        output_path: Path for the output video file (e.g., 'output.mp4').
        pattern: Pattern for the image filenames (default: 'image_%04d.png').
                Use %04d for 4-digit zero-padded numbers.
        fps: Frames per second for the output video (default: 30).
        codec: Video codec to use (default: 'libx264' for H.264).
               Other options: 'libx265' for H.265, 'mpeg4', etc.
        crf: Quality level for H.264 codec, 0-51 (lower=better, default: 23).
             Only applies when codec is 'libx264' or 'libx265'.
    
    Returns:
        True if successful, False otherwise.
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder path {folder_path} does not exist.")
        return False
    
    # Construct the full input pattern path
    input_pattern = os.path.join(folder_path, pattern)
    
    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-framerate", str(fps),
        "-i", input_pattern,
        "-c:v", codec,
    ]
    
    # Add quality setting for H.264/H.265 codecs
    if codec in ["libx264", "libx265"]:
        cmd.extend(["-crf", str(crf)])
    
    cmd.extend([
        "-y",  # Overwrite output file without asking
        output_path
    ])
    
    try:
        print(f"Creating video from images in {folder_path}...")
        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Video created successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not found in PATH.")
        return False

def convert_mkv_to_mp4(input_path, output_path=None):
    """
    Converts an MKV file to MP4 using ffmpeg with stream copy (no re-encoding).
    
    Args:
        input_path: Path to the input MKV file.
        output_path: Path for the output MP4 file. If None, replaces .mkv with .mp4.
    
    Returns:
        True if successful, False otherwise.
    """
    if not os.path.isfile(input_path):
        print(f"Error: File {input_path} does not exist.")
        return False
    
    if output_path is None:
        output_path = input_path.replace(".mkv", ".mp4")
    
    if os.path.isfile(output_path):
        print(f"Output file {output_path} already exists. Skipping.")
        return True
    
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c", "copy",
        "-y",
        output_path
    ]
    
    try:
        print(f"Converting: {input_path}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Converted successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not found in PATH.")
        return False

def batch_convert_mkv_to_mp4(root_folder_path):
    """
    Recursively converts all MKV files in a folder hierarchy to MP4.
    
    Args:
        root_folder_path: Root folder to search for MKV files.
    
    Returns:
        Dictionary with conversion statistics.
    """
    stats = {"total": 0, "converted": 0, "failed": 0, "skipped": 0}
    
    for root, dirs, files in os.walk(root_folder_path):
        for file in files:
            if file.endswith(".mkv"):
                file_path = os.path.join(root, file)
                stats["total"] += 1
                mp4_output_path = file_path.replace(".mkv", ".mp4")
                
                if convert_mkv_to_mp4(file_path, mp4_output_path):
                    if os.path.isfile(mp4_output_path):
                        stats["converted"] += 1
                    else:
                        stats["skipped"] += 1
                else:
                    stats["failed"] += 1
    
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video processing utilities using ffmpeg.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create video from images command
    images_parser = subparsers.add_parser("create", help="Create video from image sequence")
    images_parser.add_argument("-f", "--folder", required=True, help="Path to folder containing images.")
    images_parser.add_argument("-o", "--output", required=True, help="Output video file path.")
    images_parser.add_argument("-p", "--pattern", default="image_%04d.png", 
                              help="Image filename pattern (default: 'image_%%04d.png'). Use %%04d for 4-digit numbers.")
    images_parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30).")
    images_parser.add_argument("--codec", default="libx264", help="Video codec (default: 'libx264').")
    images_parser.add_argument("--crf", type=int, default=23, help="Quality level 0-51 for H.264/H.265 (default: 23).")
    
    # Convert MKV to MP4 command
    mkv_parser = subparsers.add_parser("convert", help="Convert MKV file(s) to MP4")
    mkv_parser.add_argument("-i", "--input", help="Input MKV file path (for single file conversion).")
    mkv_parser.add_argument("-o", "--output", help="Output MP4 file path (optional, defaults to replacing .mkv with .mp4).")
    mkv_parser.add_argument("-b", "--batch", help="Batch convert all MKV files in folder recursively.")
    
    args = parser.parse_args()
    
    try:
        if args.command == "create":
            success = create_video_from_images(args.folder, args.output, args.pattern, args.fps, args.codec, args.crf)
            sys.exit(0 if success else 1)
        elif args.command == "convert":
            if args.batch:
                stats = batch_convert_mkv_to_mp4(args.batch)
                print(f"\nConversion Statistics:")
                print(f"Total files: {stats['total']}")
                print(f"Converted: {stats['converted']}")
                print(f"Skipped: {stats['skipped']}")
                print(f"Failed: {stats['failed']}")
            elif args.input:
                success = convert_mkv_to_mp4(args.input, args.output)
                sys.exit(0 if success else 1)
            else:
                mkv_parser.print_help()
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)