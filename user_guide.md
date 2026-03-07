# ComfyUI Image Viewer: User Guide

Welcome to the ComfyUI Image Viewer! This tool is designed for fast, metadata-aware inspection and adjustment of your ComfyUI generations.

## 🚀 Getting Started
1. **Open Folder**: Press `Ctrl+O` to select your ComfyUI output directory.
2. **Reload**: Press `Ctrl+R` to refresh the gallery (pick up new generations).

---

## ⌨️ Keyboard Shortcuts

### Navigation
- **Left / Right / Up / Down**: Browse images in the gallery.
- **Home / End**: Jump to the first or last image.
- **S**: Sort images by creation date (Newest First).

### Viewing & Zoom
- **F**: Fit image to screen.
- **1, 2, 3, 4, 5**: Set absolute zoom (100%, 200%, 300%, 400%, 500%).
- **+ / -**: Incrementally zoom in or out.
- **Mouse Wheel**: Zoom under cursor.
- **Left-Click + Drag**: Pan the image.
- **I**: Toggle the Info Overlay (Filename and Resolution).
- **V**: Toggle Side Panels (Focus View - hides gallery/inspector).

### 🎨 Image Adjustments
- **F10**: Toggle **Persistent Adjustments**. When enabled, your slider values stay active when you switch to the next image.
- **Reset All**: Available in the right-hand panel to clear all filters.

### 🏷️ Tagging & Filtering
- **Alt + 1..5**: Apply color tags (Red, Yellow, Green, Blue, Magenta).
- **Alt + 0**: Clear color tag.
- **Filter Dropdown**: Use the dropdown above the gallery to show only specific tagged images.

### 🌓 Comparison Mode (The Wipe Effect)
1. Select an image and press **A**.
2. Select another image and press **B**.
3. Select Original Image **A**.
4. Press **C** to enter Comparison Mode.
5. **Move your mouse horizontally** to "wipe" between image A (left) and image B (right).
6. Press **C** again to exit.

---

## 🔍 Hidden Features

### Workflow Diffing
When browsing images from the same workflow, the **Workflow Inspector** (right panel) will automatically **highlight changed parameters** in orange. This helps you instantly see what change in your prompt or settings caused the visual difference.

### Portable Metadata
Annotations, notes, and color tags are saved **directly into the PNG file** without breaking the ComfyUI workflow data. You can drag these images back into ComfyUI at any time to reload the original nodes!

### Fast Conversion
The viewer uses a custom high-performance memory buffer for image processing, making it significantly faster than standard image viewers when dealing with large resolutions.
