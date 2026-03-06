import os
import hashlib
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Qt
from PySide6.QtGui import QPixmap, QImage
from PIL import Image

class ThumbnailWorkerSignals(QObject):
    # Sends back the original file path and the generated QImage (to be converted to QPixmap in main thread)
    finished = Signal(str, QImage)

class ThumbnailWorker(QRunnable):
    """
    Worker thread to generate a thumbnail from an image path and save it to a cache directory.
    Uses PIL for fast, non-GUI blocking image resizing.
    """
    def __init__(self, image_path, cache_dir, size=256):
        super().__init__()
        self.image_path = image_path
        self.cache_dir = cache_dir
        self.size = size
        self.signals = ThumbnailWorkerSignals()

    def run(self):
        try:
            # Generate a unique filename for the cache based on the original image path
            path_hash = hashlib.md5(self.image_path.encode('utf-8')).hexdigest()
            cache_file_path = os.path.join(self.cache_dir, f"{path_hash}_{self.size}.jpg")

            # Check if we already have a cached version
            if not os.path.exists(cache_file_path):
                # Generate new thumbnail
                with Image.open(self.image_path) as img:
                    img.thumbnail((self.size, self.size))
                    # Convert to RGB to ensure we can save as JPEG
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(cache_file_path, "JPEG", quality=85)
            
            # Pass QImage to the main thread securely.
            # QPixmap should NOT be instantiated in a non-GUI thread in PySide6.
            q_image = QImage(cache_file_path)
            self.signals.finished.emit(self.image_path, q_image)
            
        except Exception as e:
            print(f"Error generating thumbnail for {self.image_path}: {e}")
            # Could emit an error signal here if needed, but for now just fail silently

            
class ThumbnailCache(QObject):
    """
    Manages a cache of image thumbnails.
    Requests for thumbnails are asynchronous to prevent blocking the UI.
    """
    # Signal emitted when a new thumbnail is ready: (original_image_path, thumbnail_pixmap)
    thumbnail_ready = Signal(str, QPixmap)

    def __init__(self, cache_dir_name=".thumbcache", default_size=256, parent=None):
        super().__init__(parent)
        self.cache_dir = os.path.join(os.getcwd(), cache_dir_name)
        self.default_size = default_size
        self.thread_pool = QThreadPool.globalInstance()
        
        # Ensure our cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # Keep an in-memory cache of already loaded QPixmaps for instant retrieval
        self.memory_cache = {}

    def fetch_thumbnail(self, image_path):
        """
        Request a thumbnail for the given image path.
        If it's in the memory cache, it returns the QPixmap immediately.
        Otherwise, it starts a background worker and returns None. The thumbnail_ready signal
        will be emitted when the thumbnail is generated.
        """
        if image_path in self.memory_cache:
            return self.memory_cache[image_path]

        # Not in memory, start horizontal worker to load from disk cache or generate
        worker = ThumbnailWorker(image_path, self.cache_dir, self.default_size)
        worker.signals.finished.connect(self._on_worker_finished)
        self.thread_pool.start(worker)
        
        return None
        
    def _on_worker_finished(self, image_path, q_image):
        """Slot called when the background thread finishes creating/loading the thumbnail."""
        # Convert QImage to QPixmap safely in the main GUI thread
        pixmap = QPixmap.fromImage(q_image)
        self.memory_cache[image_path] = pixmap
        self.thumbnail_ready.emit(image_path, pixmap)

    def clear_cache(self):
        """Empties the memory cache."""
        self.memory_cache.clear()
