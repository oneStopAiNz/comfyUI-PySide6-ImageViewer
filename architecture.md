System architecture

MainWindow
 ├ GalleryPanel
 ├ ImageViewer
 └ WorkflowInspector

Data Flow

Image selected →
Extract metadata →
Parse workflow →
Populate inspector

All modules must remain under 400 lines.
Avoid circular imports.