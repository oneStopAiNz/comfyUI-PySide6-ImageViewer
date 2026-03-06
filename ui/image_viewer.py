import os
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLabel
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPixmap, QImage, QPainter

class ImageViewer(QGraphicsView):
    """
    A custom QGraphicsView that provides zoom and pan functionality 
    for displaying full-resolution images.
    Preserves zoom and pan state when switching images.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        
        # UI settings for smooth scaling and panning
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Remove scrollbars for a cleaner look
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(Qt.black)

        # Track the zoom factor to properly maintain zoom levels
        self.zoom_factor = 1.1

        # Info Overlay (Bottom Left)
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 127);
            color: white;
            padding: 10px;
            border-top-right-radius: 10px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.overlay.hide()
        self.overlay_visible = True # We'll toggle this state

    def load_image(self, path):
        """
        Loads an image from the given path into the viewer.
        The current scroll/pan and zoom transformation are maintained automatically
        because we're reusing the same scene and QGraphicsPixmapItem.
        """
        if not path or not os.path.exists(path):
            self.pixmap_item.setPixmap(QPixmap())
            return
            
        # Using PIL + QImage fallback if QPixmap straight from path has issues, 
        # but QPixmap usually handles caching/loading standard formats fine locally. 
        # For simplicity and performance, QPixmap constructor is used.
        pixmap = QPixmap(path)
        
        # If the image was invalid or couldn't load, set empty map
        if pixmap.isNull():
             pixmap = QPixmap()
             
        # Optional: We could get the scene bounding rect and reset scale 
        # ONLY if this is the very first image loaded or if the user requests "fit to screen".
        # But the prompt requests: "Preserve zoom and pan when switching images"
        # Since we just replace the pixmap on the existing item, PySide handles keeping
        # the view's current matrix state (zoom/pan) by default relative to the scene.
        
        self.pixmap_item.setPixmap(pixmap)
        
        # Ensure the scene rect matches the new image size so panning bounds are correct
        self.setSceneRect(self.pixmap_item.boundingRect())
        
        # Update Info Overlay
        self.update_overlay(path, pixmap)

    def update_overlay(self, path, pixmap):
        """Updates the information overlay with filename and resolution."""
        if not path or pixmap.isNull():
            self.overlay.hide()
            return
            
        filename = os.path.basename(path)
        w = pixmap.width()
        h = pixmap.height()
        
        self.overlay.setText(f"{filename}\n{w} x {h} px")
        self.overlay.adjustSize()
        self.position_overlay()
        
        if self.overlay_visible:
            self.overlay.show()

    def position_overlay(self):
        """Positions the overlay at the bottom left."""
        self.overlay.move(0, self.height() - self.overlay.height())

    def resizeEvent(self, event):
        """Keep overlay anchored when view is resized."""
        super().resizeEvent(event)
        self.position_overlay()

    def toggle_info_overlay(self):
        """Toggles the visibility state of the overlay."""
        self.overlay_visible = not self.overlay_visible
        if self.overlay_visible and not self.pixmap_item.pixmap().isNull():
            self.overlay.show()
        else:
            self.overlay.hide()

    def wheelEvent(self, event):
        """
        Overrides wheel event to provide zooming with the mouse wheel.
        """
        # Calculate the zoom factor based on the wheel scroll direction
        if event.angleDelta().y() > 0:
            zoom = self.zoom_factor
        else:
            zoom = 1 / self.zoom_factor

        self.scale(zoom, zoom)

    def fit_in_view(self):
        """
        Helper to reset zoom/pan to fit the current image inside the view perfectly.
        """
        if not self.pixmap_item.pixmap().isNull():
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def zoom_in(self):
        """Zooms in by the zoom_factor."""
        self.scale(self.zoom_factor, self.zoom_factor)

    def zoom_out(self):
        """Zooms out by the zoom_factor."""
        self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
