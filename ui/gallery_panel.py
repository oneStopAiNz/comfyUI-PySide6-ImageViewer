import os
import glob
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QListView, QAbstractItemView, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from core.thumbnail_cache import ThumbnailCache

class GalleryPanel(QWidget):
    """
    Shows a grid of image thumbnails from a selected folder.
    Coordinates with ThumbnailCache for lazy asynchronous loading.
    """
    image_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # UI Setup
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListView.IconMode)
        self.list_widget.setIconSize(QSize(200, 200)) # Size of the thumbnails in the UI
        self.list_widget.setResizeMode(QListView.Adjust)
        self.list_widget.setSpacing(10)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.setUniformItemSizes(True)
        
        self.layout.addWidget(self.list_widget)
        
        # Core Thumbnail Cache
        self.thumbnail_cache = ThumbnailCache(default_size=256)
        self.thumbnail_cache.thumbnail_ready.connect(self.on_thumbnail_ready)

        # Connect signals
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        # State
        self.current_folder = ""
        self.image_paths = []

    def load_folder(self, folder_path):
        """Loads PNG images from the given folder and populates the grid."""
        self.list_widget.clear()
        self.thumbnail_cache.clear_cache()
        
        self.current_folder = folder_path
        if not folder_path or not os.path.exists(folder_path):
            return
            
        # Get all PNG images
        search_pattern = os.path.join(folder_path, "*.png")
        self.image_paths = glob.glob(search_pattern)
        
        # You could sort by modification time here:
        # self.image_paths.sort(key=os.path.getmtime, reverse=True)

        # Create items (they will load their thumbnails asynchronously)
        for path in self.image_paths:
            # We use Custom Item linking to the path so we can retrieve it
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.UserRole, path)
            item.setSizeHint(QSize(220, 240)) # Give space for text below icon
            item.setTextAlignment(Qt.AlignBottom | Qt.AlignHCenter)
            self.list_widget.addItem(item)
            
            # Start lazy loading the thumbnail
            pixmap = self.thumbnail_cache.fetch_thumbnail(path)
            if pixmap:
                # Value was already in memory cache
                item.setIcon(QIcon(pixmap))
            else:
                 # It's loading... maybe set a placeholder icon
                 pass

    def on_thumbnail_ready(self, image_path, pixmap):
        """Slot triggered when ThumbnailCache finishes generating a thumbnail for an image."""
        # Find the item corresponding to this path and set its icon
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == image_path:
                item.setIcon(QIcon(pixmap))
                break

    def on_selection_changed(self):
        """Triggered when the user clicks/selects an image in the grid."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            # Get path we stored in the UserRole
            path = selected_items[0].data(Qt.UserRole)
            self.image_selected.emit(path)

    def select_next(self):
        """Selects the next image in the grid (for keyboard navigation)."""
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(current_row + 1)

    def select_previous(self):
        """Selects the previous image in the grid (for keyboard navigation)."""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            self.list_widget.setCurrentRow(current_row - 1)

    def select_first(self):
        """Selects the first image in the grid."""
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def select_last(self):
        """Selects the last image in the grid."""
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def sort_by_date(self):
        """Sorts images by creation (modification) date and reloads the gallery."""
        if not self.image_paths:
            return
            
        # Sort by modification time (creation date is platform dependent, mtime is usually what users want)
        self.image_paths.sort(key=os.path.getmtime, reverse=True)
        
        # Reload the list widget with the new order
        # Save current selection path if any
        selected_path = None
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            selected_path = selected_items[0].data(Qt.UserRole)
            
        self.list_widget.clear()
        for path in self.image_paths:
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.UserRole, path)
            item.setSizeHint(QSize(220, 240))
            item.setTextAlignment(Qt.AlignBottom | Qt.AlignHCenter)
            self.list_widget.addItem(item)
            
            # Use fetch_thumbnail to get from cache or start loading
            pixmap = self.thumbnail_cache.fetch_thumbnail(path)
            if pixmap:
                item.setIcon(QIcon(pixmap))
                
        # Restore selection if it still exists
        if selected_path:
            for i in range(self.list_widget.count()):
                if self.list_widget.item(i).data(Qt.UserRole) == selected_path:
                    self.list_widget.setCurrentRow(i)
                    break
