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

def save_notes_to_png(path, notes):
    """
    Saves notes to the 'notes' text chunk in the PNG, preserving all other metadata.
    """
    try:
        from PIL.PngImagePlugin import PngInfo
        
        # 1. Read existing metadata and image data
        with Image.open(path) as img:
            # We must load the image data into memory before closing the file
            # or saving to the same path
            img.load() 
            info = img.info.copy()
            
            # 2. Update/Add notes
            info['notes'] = notes
            
            # 3. Create PngInfo object for saving
            target_info = PngInfo()
            for k, v in info.items():
                if isinstance(v, str):
                    target_info.add_text(k, v)
            
            # 4. Save back to the same path (or temp then rename if paranoid)
            # We use the existing img object which is already in memory
            img.save(path, "PNG", pnginfo=target_info)
            return True
            
    except Exception as e:
        print(f"Error saving metadata to {path}: {e}")
        return False
