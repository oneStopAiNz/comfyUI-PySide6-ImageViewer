# Image Adjustments in Video Export

This document explains the technical implementation and sequence of operations when creating an MP4 video with image adjustments.

## Sequence of Operations

The following sequence is triggered when [MainWindow.create_video()](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py) is called:

### 1. Detection & Setup
- **Line Condition**: `use_adjustments = self.viewer.apply_adj_on_load and any(v != 0 for v in self.viewer.current_adjustments.values())`
- **Action**: If true, a temporary directory is created via `tempfile.mkdtemp()`.
- **Function**: `GalleryPanel.get_visible_image_paths()` is called to retrieve the current list of images following UI sorting and filtering.

### 2. Frame Processing (Loop)
For each image path in the list, the following occurs inside `MainWindow.create_video()`:
1.  **Open**: `Image.open(path)` from the **Pillow** library.
2.  **Adjust**: `apply_adjustments_to_pil(img, self.viewer.current_adjustments)` is called from `core/imageUtils.py`.
    -   Internally uses `ImageEnhance.Brightness`, `ImageEnhance.Contrast`, and `ImageFilter.UnsharpMask`.
3.  **Save**: `adjusted_img.save(temp_path)` writes the adjusted frame to the temporary directory.

### 3. Video Encoding
- **Function**: `create_video_from_path_list(paths_to_use, output_path)` in `core/videoUtils.py` is invoked.
- **Workflow**:
    1.  Creates a `.txt` file for the FFmpeg `concat` demuxer.
    2.  Writes `file 'path/to/frame.png'` and `duration` for each frame.
    3.  Runs `subprocess.run(["ffmpeg", ...])` to encode the MP4.

### 4. Automatic Cleanup
- **Mechanism**: A `finally:` block in `MainWindow.create_video()`.
- **Action**: `shutil.rmtree(temp_dir)` clears all temporary frames and the directory itself immediately after encoding finishes.

## Summary of Functions Called

| Module | Function | Purpose |
| :--- | :--- | :--- |
| `ui/gallery_panel.py` | `get_visible_image_paths()` | Gets the sorted/filtered image list. |
| `core/imageUtils.py` | `apply_adjustments_to_pil()` | The core engine that applies Exposure, Gamma, etc. |
| `core/videoUtils.py` | `create_video_from_path_list()`| Manages the FFmpeg concat/encoding process. |
| `ui/main_window.py`  | `create_video()` | Orchestrates the entire temporary-file-workflow. |

## Why use temporary files?

We use temporary files instead of piping raw data to FFmpeg for several reasons:
-   **Reliability**: It prevents pipe-buffer issues when processing large sequences.
-   **Memory Efficiency**: The application only keeps one adjusted frame in memory at a time.
-   **Stability**: Avoids complexities with FFmpeg's `stdin` when handling variable frame processing times.

---
*Note: This process requires FFmpeg to be installed on your system.*
