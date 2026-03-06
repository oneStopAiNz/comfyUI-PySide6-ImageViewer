import json
from PIL import Image

def load_prompt_from_png(path):
    """
    Extracts ComfyUI JSON metadata from a PNG file.
    ComfyUI stores the workflow data in the 'workflow' or 'prompt' text chunks in the PNG metadata.
    
    Returns:
        dict: The parsed JSON metadata, or None if no valid metadata is found.
    """
    try:
        with Image.open(path) as img:
            # PNG metadata is stored in img.info
            # ComfyUI typically uses 'workflow' and 'prompt' keys. This will prioritize 'workflow'
            # if both exist, otherwise fallback to 'prompt', or return None if neither exist.
            
            metadata_str = None
            if 'workflow' in img.info:
                metadata_str = img.info['workflow']
            elif 'prompt' in img.info:
                metadata_str = img.info['prompt']
                
            if metadata_str:
                return json.loads(metadata_str)
            else:
                return None
                
    except Exception as e:
        print(f"Error reading metadata from {path}: {e}")
        return None
