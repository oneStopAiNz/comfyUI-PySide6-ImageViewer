from PIL import Image
import os
import glob
import argparse
import sys

def downsample_image(image, percentage):
    """
    Downsamples the input image by the given percentage.
    
    Args:
        image: PIL Image object.
        percentage: Float between 0 and 1, e.g., 0.5 for 50% size.
    
    Returns:
        Downsampled PIL Image and its dimensions.
    """
    if percentage <= 0 or percentage > 1:
        raise ValueError("Percentage must be between 0 and 1.")
    
    width, height = image.size
    new_width = int(width * percentage)
    new_height = int(height * percentage)
    
    downsampled = image.resize((new_width, new_height), resample=Image.BILINEAR)
    return downsampled, (new_height, new_width)

def downsample_images_in_folder(folder_path, output_folder_path, percentage, extensions=['.jpg', '.png', '.jpeg', '.bmp', '.webp']):
    """
    Downsamples all images with specified extensions in the given folder by the given percentage
    and saves them in the output folder.
    
    Args:
        folder_path: Path to the folder containing images.
        output_folder_path: Path to the output folder.
        percentage: Float between 0 and 1, e.g., 0.5 for 50% size.
        extensions: List of file extensions to process.
    """
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder path {folder_path} does not exist.")
    
    os.makedirs(output_folder_path, exist_ok=True)
    
    # Collect all files with specified extensions
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(folder_path, f'*{ext}')))
    
    if not files:
        print("No images found with the specified extensions.")
        return
    
    for file_path in files:
        try:
            # Load image using Pillow
            with Image.open(file_path) as img:
                # Downsample
                downsampled_img, dimensions = downsample_image(img, percentage)
                
                # Save to output directory
                base_name = os.path.basename(file_path)
                output_path = os.path.join(output_folder_path, base_name)
                downsampled_img.save(output_path)
                print(f"Downsampled and saved: {output_path} with {dimensions[1]}x{dimensions[0]} pixels")
        except Exception as e:
            print(f"Could not process image {file_path}: {e}")

def sort_and_rename_images(folder_path, extension, prefix="image", start_number=1):
    """
    Sorts images in a folder by name and renames them sequentially.
    
    Args:
        folder_path: Path to the folder containing images.
        extension: File extension to search for (e.g., '.jpg' or ['.jpg', '.png']).
        prefix: Prefix for the renamed files (default: 'image').
        start_number: Starting number for the sequence (default: 1).
    
    Returns:
        List of tuples containing (old_name, new_name) for each renamed file.
    """
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder path {folder_path} does not exist.")
    
    # Handle single extension or list of extensions
    if isinstance(extension, str):
        extensions = [extension] if extension.startswith('.') else [f'.{extension}']
    else:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extension]
    
    # Collect all files with specified extensions
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(folder_path, f'*{ext}')))
    
    if not files:
        print(f"No images found with extension(s): {extensions}")
        return []
    
    # Sort files by name
    files.sort()
    
    # Rename files sequentially
    rename_log = []
    num_digits = len(str(start_number + len(files) - 1))  # Calculate padding needed
    
    for index, file_path in enumerate(files):
        old_name = os.path.basename(file_path)
        ext = os.path.splitext(old_name)[1]
        
        # Create new name with zero-padded number
        new_number = start_number + index
        new_name = f"{prefix}_{new_number:0{num_digits}d}{ext}"
        new_path = os.path.join(folder_path, new_name)
        
        # Rename the file
        os.rename(file_path, new_path)
        rename_log.append((old_name, new_name))
        print(f"Renamed: {old_name} → {new_name}")
    
    return rename_log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility for image processing tasks.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Downsample command
    downsample_parser = subparsers.add_parser("downsample", help="Downsample images in a folder")
    downsample_parser.add_argument("-f","--folder_path", help="Path to the folder containing images.")
    downsample_parser.add_argument("-o","--output_folder", help="Path to the output folder containing images.")
    downsample_parser.add_argument("-p","--percentage", type=float, help="Downsampling percentage (e.g., 0.5 for 50%).")
    downsample_parser.add_argument("--extensions", nargs='+', default=['.jpg', '.png', '.jpeg', '.bmp', '.webp'], 
                        help="List of file extensions to process (default: .jpg .png .jpeg .bmp .webp).")
    
    # Rename command
    rename_parser = subparsers.add_parser("rename", help="Sort and rename images sequentially")
    rename_parser.add_argument("-f", "--folder_path", required=True, help="Path to the folder containing images.")
    rename_parser.add_argument("-e", "--extension", required=True, help="File extension to search for (e.g., '.jpg' or provide multiple: .jpg .png).")
    rename_parser.add_argument("--prefix", default="image", help="Prefix for renamed files (default: 'image').")
    rename_parser.add_argument("--start", type=int, default=1, help="Starting number for sequence (default: 1).")
    
    args = parser.parse_args()
    
    try:
        if args.command == "downsample":
            downsample_images_in_folder(args.folder_path, args.output_folder, args.percentage, args.extensions)
        elif args.command == "rename":
            # Handle extension as single string or list
            extensions = args.extension.split() if ' ' in args.extension else args.extension
            sort_and_rename_images(args.folder_path, extensions, args.prefix, args.start)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
