import os
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPixmap, QImage, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLabel, QGraphicsRectItem, QGraphicsItem, QGraphicsLineItem

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
        
        # Original state for adjustments
        self.original_pixmap = None
        self.original_path = None
        self.original_pil = None # Cached for performance
        self.current_adjustments = {}
        
        # Debouncing timer for slider updates
        from PySide6.QtCore import QTimer
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(10) # 10ms is usually enough to debounce
        self.update_timer.timeout.connect(self._do_apply_adjustments)
        self.pending_adj = None
        
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
        
        # Comparison Mode State
        self.comparison_mode = False
        self.pixmap_a = None
        self.pixmap_b = None
        self.path_a = None
        self.path_b = None
        self.wipe_ratio = 0.5  # 0.0 to 1.0
        
        # Create a second pixmap item for comparison inside a clipping container
        self.clip_container = QGraphicsRectItem()
        self.clip_container.setBrush(Qt.NoBrush)
        self.clip_container.setPen(Qt.NoPen)
        self.clip_container.setFlag(QGraphicsItem.ItemClipsChildrenToShape)
        self.clip_container.setZValue(1)
        self.scene.addItem(self.clip_container)
        
        self.pixmap_item_b = QGraphicsPixmapItem(self.clip_container)
        
        # Divider line (always on top)
        self.divider_line = QGraphicsLineItem()
        self.divider_line.setPen(QPen(Qt.white, 2))
        self.divider_line.setZValue(10) # High Z to be above everything
        self.scene.addItem(self.divider_line)
        self.divider_line.hide()

        # Track mouse move for wipe ratio
        self.setMouseTracking(True)

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
        """Loads an image with maximum speed. Adjustments are reset but applied lazily."""
        self.original_path = path
        if not path or not os.path.exists(path):
            self.pixmap_item.setPixmap(QPixmap())
            self.original_pixmap = None
            self.original_pil = None
            return
            
        # Fast load for switching: just use QPixmap
        pixmap = QPixmap(path)
        if pixmap.isNull():
             pixmap = QPixmap()
             
        self.original_pil = None # Set to None for lazy loading
        self.original_pixmap = pixmap
        self.pixmap_item.setPixmap(pixmap)
        self.setSceneRect(self.pixmap_item.boundingRect())
        self.update_overlay(path, pixmap)
        
        # Reset internal adjustment state for new image
        self.current_adjustments = {}

    def apply_adjustments(self, adj):
        """Debounced application of adjustments. Instant bypass if all values are zero."""
        self.pending_adj = adj
        
        # Check if we should bypass the slow PIL pipeline
        is_zero = all(v == 0 for v in adj.values())
        if is_zero:
            if self.original_pixmap:
                self.pixmap_item.setPixmap(self.original_pixmap)
            self.current_adjustments = adj
            self.update_timer.stop() # Cancel any pending slow update
            return

        if not self.update_timer.isActive():
            self.update_timer.start()

    def _do_apply_adjustments(self):
        """Lazily loads PIL image and applies filters."""
        if self.original_path is None:
            return
            
        # Lazy load PIL if not already loaded
        if self.original_pil is None:
            from PIL import Image
            try:
                self.original_pil = Image.open(self.original_path)
                if self.original_pil.mode != "RGB":
                    self.original_pil = self.original_pil.convert("RGB")
            except Exception as e:
                print(f"Lazy load error: {e}")
                return

        adj = self.pending_adj
        self.current_adjustments = adj
        
        from PIL import ImageEnhance, ImageFilter
        
        # Work on a copy of the cached original
        try:
            pil_img = self.original_pil
            
            # Application order matters. 
            if adj.get("exposure", 0) != 0:
                factor = 1.0 + (adj["exposure"] / 100.0)
                if factor <= 0: factor = 0.01
                pil_img = ImageEnhance.Brightness(pil_img).enhance(factor)
                
            if adj.get("brightness", 0) != 0:
                factor = 1.0 + (adj["brightness"] / 200.0)
                pil_img = ImageEnhance.Brightness(pil_img).enhance(factor)
                
            if adj.get("contrast", 0) != 0:
                factor = 1.0 + (adj["contrast"] / 100.0)
                if factor <= 0: factor = 0.01
                pil_img = ImageEnhance.Contrast(pil_img).enhance(factor)
                
            if adj.get("texture", 0) > 0:
                 pil_img = pil_img.filter(ImageFilter.UnsharpMask(radius=2, percent=int(adj["texture"]), threshold=3))

            # FAST CONVERSION: Avoid PNG/JPEG encoding buffer.
            # Use raw data + QImage constructor.
            data = pil_img.tobytes("raw", "RGB")
            qimg = QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format_RGB888)
            
            # IMPORTANT: QImage doesn't own the 'data' buffer. But here 'data' is a local bytes object
            # that lives until qimg is used to create a QPixmap? 
            # Actually, to be safe and avoid crashes if the GC eats 'data', we'll use QPixmap.fromImage which copies.
            self.pixmap_item.setPixmap(QPixmap.fromImage(qimg))
            
        except Exception as e:
            print(f"Filter error: {e}")

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

    def set_image_a(self, path):
        """Tags current image as A."""
        self.path_a = path
        if path:
            self.pixmap_a = QPixmap(path)
        else:
            self.pixmap_a = None
        self.update_comparison_rendering()

    def set_image_b(self, path):
        """Tags current image as B."""
        self.path_b = path
        if path:
            pixmap = QPixmap(path)
            self.pixmap_b = pixmap
            self.pixmap_item_b.setPixmap(pixmap)
        else:
            self.pixmap_b = None
            self.pixmap_item_b.setPixmap(QPixmap())
        self.update_comparison_rendering()

    def toggle_comparison_mode(self):
        """Toggles the wipe comparison mode."""
        if not self.pixmap_a or not self.pixmap_b:
            return False # Cannot toggle without both images
        
        self.comparison_mode = not self.comparison_mode
        if self.comparison_mode:
            self.clip_container.show()
            self.divider_line.show()
            self.setDragMode(QGraphicsView.NoDrag) # Disable pan so mouse moves wipe
        else:
            self.clip_container.hide()
            self.divider_line.hide()
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        self.update_comparison_rendering()
        return self.comparison_mode

    def update_comparison_rendering(self):
        """Updates the clipping of the top image based on wipe_ratio."""
        if not self.comparison_mode or self.pixmap_b is None:
            return
            
        # We use a rect on the container to clip its child (B)
        rect = self.pixmap_b.rect()
        width = rect.width()
        height = rect.height()
        
        clip_width = width * self.wipe_ratio
        
        # Divider is at clip_width. 
        # Left of divider = A, Right of divider = B.
        # Container visible area = [clip_width, 0, width-clip_width, height]
        visible_rect = QRectF(clip_width, 0, width - clip_width, height)
        self.clip_container.setRect(visible_rect)
        
        # Update divider line (in scene coordinates, but B is at 0,0)
        self.divider_line.setLine(clip_width, 0, clip_width, height)
        
        # Update overlay text if in comparison mode
        if self.comparison_mode:
            file_a = os.path.basename(self.path_a) if self.path_a else "None"
            file_b = os.path.basename(self.path_b) if self.path_b else "None"
            self.overlay.setText(f"COMPARING\n(Move Mouse to Wipe)\nA: {file_a}\nB: {file_b}")
            self.overlay.show()

    def mouseMoveEvent(self, event):
        """Tracks horizontal mouse movement to update wipe ratio."""
        if self.comparison_mode and self.pixmap_b:
            # Map mouse to scene coordinates relative to the image
            scene_pos = self.mapToScene(event.position().toPoint())
            image_rect = self.pixmap_item_b.boundingRect()
            
            if image_rect.width() > 0:
                # Calculate ratio based on X position relative to image bounds
                ratio = (scene_pos.x() - image_rect.left()) / image_rect.width()
                self.wipe_ratio = max(0.0, min(1.0, ratio))
                self.update_comparison_rendering()
        else:
            super().mouseMoveEvent(event)

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

    def set_zoom_level(self, scale_factor):
        """Sets the zoom level to an absolute scale factor."""
        # Reset current transformation to 100%
        self.resetTransform()
        # Apply the absolute scale
        self.scale(scale_factor, scale_factor)
