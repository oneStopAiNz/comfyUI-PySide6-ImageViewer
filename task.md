- [x] **Environment Setup**
  - [x] Create virtual environment `.venv`
  - [x] Install dependencies (PySide6, Pillow, orjson)
  - [x] Migrate code from PySide2 to PySide6

- [x] **Implementation Task 1: thumbnail_cache.py**
  - [x] Manage async thumbnail generation
  - [x] Cache thumbnails to `.thumbcache`
  - [x] Return QPixmap


- [x] **Implementation Task 2: png_metadata.py**
  - [x] Extract ComfyUI JSON metadata from PNGs

- [x] **Implementation Task 3: comfy_parser.py**
  - [x] Parse workflow JSON into structured data

- [x] **Implementation Task 4: image_viewer.py**
  - [x] Subclass QGraphicsView
  - [x] Implement load_image
  - [x] Implement zoom and pan
  
- [x] **Implementation Task 5: gallery_panel.py**
  - [x] Implement thumbnail grid viewer
  - [x] Emit signal on selection

- [x] **Implementation Task 6: workflow_inspector.py**
  - [x] Node combo box and parameter table

- [x] **Implementation Task 8: workflow_diff.py**
  - [x] Compare parameters between nodes

- [x] **Implementation Task 7: main_window.py**
  - [x] Assemble UI components
  - [x] Handle interactions (selection, keyboard navigation)

- [x] **Implementation Task 9: Enhance workflow_inspector.py**
  - [x] Highlight changed parameters in UI

- [x] **Styling & Theming**
  - [x] Define Dark Orange QSS styling
  - [x] Apply theme to main application
  - [x] Refine component colors (selection, highlights)

- [x] **Keyboard Shortcuts & Sorting**
  - [x] Implement First/Last/Sort in [GalleryPanel](file:///c:/Users/User/comfyUIImageViewer/ui/gallery_panel.py#9-151)
  - [x] Add `keyPressEvent` handlers in [MainWindow](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py#13-144)
  - [x] Connect `F` key to `ImageViewer.fit_in_view`

- [x] **Refine Input Handling**
  - [x] Implement `QShortcut` for global window-level access
  - [x] Ensure navigation works regardless of widget focus

- [x] **Enhance Node Display**
  - [x] Extract `title` from ComfyUI metadata in [comfy_parser.py](file:///c:/Users/User/comfyUIImageViewer/core/comfy_parser.py)
  - [x] Display titles in [WorkflowInspector](file:///c:/Users/User/comfyUIImageViewer/ui/workflow_inspector.py#5-155) combo box

- [x] **Zoom Shortcuts**
  - [x] Implement [zoom_in](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#135-138) and [zoom_out](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#139-142) in [ImageViewer](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#6-142)
  - [x] Add `QShortcut` for `=` and `-` in [MainWindow](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py#13-144)

- [x] **Image Info Overlay**
  - [x] Implement overlay widget in [ImageViewer](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#6-142)
  - [x] Update overlay content on image load
  - [x] Add [toggle_info_overlay](file:///c:/Users/User/comfyUIImageViewer/ui/image_viewer.py#108-115) functionality
  - [x] Add `I` shortcut in [MainWindow](file:///c:/Users/User/comfyUIImageViewer/ui/main_window.py#13-144)

- [x] **Full Screen Mode**
  - [x] Implement `F12` shortcut for `showFullScreen`
  - [x] Implement `Esc` shortcut for `showNormal`

- [x] **Repository Management**
  - [x] Initialize Git repository
  - [x] Configure [.gitignore](file:///c:/Users/User/comfyUIImageViewer/.gitignore) for `.venv` and `.thumbcache`
  - [x] Push code to `git@github.com:oneStopAiNz/comfyUI-PySide6-ImageViewer.git`






