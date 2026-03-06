# Build Plan

Implement modules in this order.

## Task 1
Implement core/thumbnail_cache.py.

Requirements:
- Generate thumbnails
- Cache thumbnails to .thumbcache
- Return QPixmap thumbnails
- Default size 256px

---

## Task 2
Implement utils/png_metadata.py.

Function:
load_prompt_from_png(path)

Behavior:
Extract ComfyUI JSON metadata from PNG files.

---

## Task 3
Implement core/comfy_parser.py.

Function:
parse_workflow(data)

Output:
{
  node_id:{
     "type":node_type,
     "inputs":{key:value}
  }
}

---

## Task 4
Implement ui/image_viewer.py.

Requirements:
Subclass QGraphicsView.

Features:
- load_image(path)
- zoom with mouse wheel
- pan with drag
- maintain transform

---

## Task 5
Implement ui/gallery_panel.py.

Requirements:
Thumbnail grid viewer using QListWidget.
Use ThumbnailCache.

Emit signal when image selected.

---

## Task 6
Implement ui/workflow_inspector.py.

Features:
- Node combo box
- Parameter table
- load_workflow()

---

## Task 7
Implement ui/main_window.py.

Layout:

Gallery | ImageViewer | WorkflowInspector

Behavior:

Selecting image:
- load viewer
- extract metadata
- update inspector

Keyboard navigation:
Left / Right keys switch images while preserving zoom.

---

## Task 8
Implement core/workflow_diff.py.

Function:
compare_nodes(nodeA,nodeB)

Return changed parameters.

---

## Task 9
Enhance workflow_inspector.py.

Highlight changed parameters in yellow.