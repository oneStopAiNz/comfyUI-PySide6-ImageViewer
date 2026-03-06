# Image Tagging and Wipe Comparison Mode

This plan outlines the addition of image tagging (A/B) and a "wipe" comparison mode between two tagged images.

## Proposed Changes

### UI Components

#### [MODIFY] [main_window.py](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py)
- Add state variables for `image_a_path` and `image_b_path`.
- Add shortcuts for 'A' (tag current as A), 'B' (tag current as B), and 'C' (toggle comparison mode).
- Wire these shortcuts to functions that update the state and notify the [ImageViewer](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#6-348).

#### Image Adjustments and Metadata Notes

This addition introduces a fourth panel for real-time image adjustments (Camera Raw style) and metadata-aware notes.

#### [NEW] [image_adjust_panel.py](file:///c:/Users/User/comfyUIImageViewer/ui/image_adjust_panel.py)
- UI: Vertical layout with sliders for:
    - **Exposure**: Multiplicative adjustment.
    - **Brightness**: Linear shift.
    - **Contrast**: Midpoint-relative scaling.
    - **Blacks/Whites**: Level clipping/shifting.
    - **Texture**: High-frequency contrast (Unsharp Mask).
    - **Clarity**: Mid-tone local contrast.
    - **Dehaze**: Atmospheric haze reduction approximation.
- UI: `QPlainTextEdit` for session notes.
- UI: "Save Notes" button.

#### [MODIFY] [main_window.py](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py)
- Incorporate [ImageAdjustPanel](file:///c:/Users/User/comfyUIImageViewer/ui/image_adjust_panel.py#4-140) into the main `QSplitter`.
- Handle slider signals to update the [ImageViewer](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#6-348).
- Manage save button signals to trigger metadata writes.

#### [MODIFY] [image_viewer.py](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py)
- Add a filter pipeline to apply adjustments to the `QPixmap`.
- Cache the original `QPixmap` to avoid quality degradation from repeated filtered processing.
- Potentially use `Pillow` for heavy-duty filtering.

#### [MODIFY] [png_metadata.py](file:///c:/Users/User/comfyUIImageViewer/utils/png_metadata.py)
- Implement [save_notes_to_png(path, notes)](file:///c:/Users/User/comfyUIImageViewer/utils/png_metadata.py#53-56).
- Use `Pillow`'s `PngInfo` to append the [notes](file:///c:/Users/User/comfyUIImageViewer/ui/image_adjust_panel.py#138-140) key while preserving all other existing keys (like `workflow` and `prompt`).

### Zoom Enhancements

#### [MODIFY] [image_viewer.py](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py)
- Implement [set_zoom_level(scale)](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#342-348) to allow setting an absolute scale factor.

#### [MODIFY] [main_window.py](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py)
- Add shortucts for keys '1', '2', '3', '4', '5' to call `viewer.set_zoom_level` with factors 1.0, 2.0, 3.0, 4.0, and 5.0 respectively.

### Folder Reload and Color Tagging

#### [MODIFY] [utils/png_metadata.py](file:///c:/Users/User/comfyUIImageViewer/utils/png_metadata.py)
- Update [save_notes_to_png](file:///c:/Users/User/comfyUIImageViewer/utils/png_metadata.py#53-56) to be more generic or add `save_color_tag_to_png`.
- Ensure metadata reading includes the [color_tag](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py#175-187).

#### [MODIFY] [ui/gallery_panel.py](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py)
- Implement [reload_folder()](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#61-99) to rescan the current directory and update thumbnails.
- Add a `QComboBox` filter at the top: "All", "Red", "Yellow", "Green", "Blue", "Magenta".
- Store [color_tag](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py#175-187) in `QListWidgetItem` data for efficient filtering.

#### [MODIFY] [ui/image_adjust_panel.py](file:///c:/Users/User/comfyUIImageViewer/ui/image_adjust_panel.py)
- Add a "Color Tags" section with 5 circular buttons representing the colors.
- Colors: Red (`#ff4444`), Yellow (`#ffcc00`), Green (`#44ff44`), Blue (`#4444ff`), Magenta (`#ff44ff`).

#### [MODIFY] [ui/image_viewer.py](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py)
- Update [update_overlay](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#186-215) to use HTML in `QLabel` for a colored dot indicator next to the filename.

#### [MODIFY] [ui/main_window.py](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py)
- Add "Reload Folder" (Ctrl+R) to the File menu.
- Add Alt+1..5 shortcuts for applying color tags.
- Connect `adjuster.color_tag_selected` to metadata saving and UI updates.

### Bug Fixes

#### [MODIFY] [ui/gallery_panel.py](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py)
- Update [select_next](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#154-161) and [select_previous](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#160-165) to iterate through items and skip those where `item.isHidden()` is true.
- Unified [reload_folder](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#61-99): Always sorts by `os.path.getmtime`.
- Refactor [sort_by_date](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#176-210) to just call [reload_folder](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#61-99).
- Ensure [apply_filter](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#112-125) is called at the very end of [reload_folder](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#61-99).
- **Stable Sorting Fix**: Switch sorting key from `os.path.getmtime` to `os.path.getctime` to prevent reordering when metadata (tags/notes) are saved.

#### [MODIFY] [ui/main_window.py](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py)
- Remove redundant `Ctrl+R` `QShortcut` from [setup_shortcuts](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py#63-96), as it's already handled by the `reload_action` in the menu.
- Add `toggle_side_panels()` method to toggle between full layout and image-only view.
- Map `Qt.Key_V` (or similar) to `toggle_side_panels`.
- Ensure `reload_action` has `Qt.WindowShortcut` context to work when child widgets have focus.

## Verification Plan

### Automated Tests
- Test that metadata saving preserves ComfyUI `workflow` key.

### Manual Verification
- Adjust sliders and verify real-time viewer updates.
- Enter notes, click save, then refresh or reload to verify notes are persisted in the fourth pane.
- Open the saved image in ComfyUI or another metadata viewer to verify the `workflow` chunk is still valid and present.
