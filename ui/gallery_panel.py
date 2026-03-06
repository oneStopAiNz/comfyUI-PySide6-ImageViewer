import os
import glob
from PySide6.QtWidgets import (QListWidget, QListWidgetItem, QListView, QAbstractItemView, 
                             QVBoxLayout, QWidget, QHBoxLayout, QComboBox, QLabel)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QColor, QPainter, QBrush

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
        
        # Filter UI
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Red", "Yellow", "Green", "Blue", "Magenta"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        self.layout.addLayout(filter_layout)
        
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
        self.image_tags = {} # path -> color_tag

    def load_folder(self, folder_path):
        """Loads PNG images from the given folder and populates the grid."""
        self.current_folder = folder_path
        self.reload_folder()

    def reload_folder(self):
        """Rescans the current folder for images and updates the gallery."""
        if not self.current_folder or not os.path.exists(self.current_folder):
            self.list_widget.clear()
            return
            
        # Remember selection
        selected_path = self.get_current_image_path()
        
        self.list_widget.clear()
        
        # Get all PNG images
        search_pattern = os.path.join(self.current_folder, "*.png")
        self.image_paths = glob.glob(search_pattern)
        
        # Strictly sort by creation time (ctime) - newest first
        self.image_paths.sort(key=os.path.getctime, reverse=True)

        # Meta-data loading for color tags
        from utils.png_metadata import load_metadata_from_png
        
        for path in self.image_paths:
            # Load metadata for tagging/filtering
            meta = load_metadata_from_png(path)
            color = meta.get('color_tag', None)
            self.image_tags[path] = color
            
            self._add_item_to_list(path, color)

        # Ensure active filter is applied
        self.apply_filter(self.filter_combo.currentText())

        # Restore selection
        if selected_path:
            for i in range(self.list_widget.count()):
                if self.list_widget.item(i).data(Qt.UserRole) == selected_path:
                    self.list_widget.setCurrentRow(i)
                    break

    def _add_item_to_list(self, path, color):
        item = QListWidgetItem(os.path.basename(path))
        item.setData(Qt.UserRole, path)
        item.setData(Qt.UserRole + 1, color) # Store color tag
        item.setSizeHint(QSize(220, 240))
        item.setTextAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.list_widget.addItem(item)
        
        pixmap = self.thumbnail_cache.fetch_thumbnail(path)
        if pixmap:
            item.setIcon(QIcon(pixmap))

    def apply_filter(self, filter_text):
        """Filters the items in the list widget based on color tag."""
        filter_text = filter_text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            tag = item.data(Qt.UserRole + 1)
            
            if filter_text == "all":
                item.setHidden(False)
            elif tag and tag.lower() == filter_text:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def update_image_tag(self, path, color):
        """Updates the tag for a specific image item in the UI."""
        self.image_tags[path] = color
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == path:
                item.setData(Qt.UserRole + 1, color)
                # If current filter doesn't match, hide it
                self.apply_filter(self.filter_combo.currentText())
                break

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
        """Selects the next visible image in the grid."""
        current_row = self.list_widget.currentRow()
        for i in range(current_row + 1, self.list_widget.count()):
            if not self.list_widget.item(i).isHidden():
                self.list_widget.setCurrentRow(i)
                break

    def select_previous(self):
        """Selects the previous visible image in the grid."""
        current_row = self.list_widget.currentRow()
        for i in range(current_row - 1, -1, -1):
            if not self.list_widget.item(i).isHidden():
                self.list_widget.setCurrentRow(i)
                break

    def select_first(self):
        """Selects the first visible image in the grid."""
        for i in range(self.list_widget.count()):
            if not self.list_widget.item(i).isHidden():
                self.list_widget.setCurrentRow(i)
                break

    def select_last(self):
        """Selects the last visible image in the grid."""
        for i in range(self.list_widget.count() - 1, -1, -1):
            if not self.list_widget.item(i).isHidden():
                self.list_widget.setCurrentRow(i)
                break

    def sort_by_date(self):
        """Sorts images by modification date (re-triggers reload)."""
        self.reload_folder()
    def get_current_image_path(self):
        """Returns the path of the currently selected image."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.UserRole)
        return None
