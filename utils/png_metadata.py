import json
from PIL import Image

def load_metadata_from_png(path):
    """
    Extracts all text metadata from a PNG file.
    Returns:
        dict: All info keys, or None if error.
    """
    try:
        with Image.open(path) as img:
            return img.info
    except Exception as e:
        print(f"Error reading metadata from {path}: {e}")
        return {}

def save_metadata_to_png(path, updates):
    """
    Saves a dictionary of key-value pairs to the PNG text chunks, preserving all other metadata.
    Args:
        path (str): Path to PNG
        updates (dict): Keys and values to add/update
    """
    try:
        from PIL.PngImagePlugin import PngInfo
        
        # 1. Read existing metadata and image data
        with Image.open(path) as img:
            img.load() 
            info = img.info.copy()
            
            # 2. Update/Add metadata
            for k, v in updates.items():
                if v is None:
                    if k in info: del info[k]
                else:
                    info[k] = str(v)
            
            # 3. Create PngInfo object for saving
            target_info = PngInfo()
            for k, v in info.items():
                if isinstance(v, str):
                    target_info.add_text(k, v)
            
            # 4. Save back to the same path
            img.save(path, "PNG", pnginfo=target_info)
            return True
            
    except Exception as e:
        print(f"Error saving metadata to {path}: {e}")
        return False

def save_notes_to_png(path, notes):
    """Legacy wrapper for save_metadata_to_png."""
    return save_metadata_to_png(path, {'notes': notes})
