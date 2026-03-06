import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QFileDialog, QMessageBox
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtCore import Qt

from ui.gallery_panel import GalleryPanel
from ui.image_viewer import ImageViewer
from ui.workflow_inspector import WorkflowInspector
from utils.png_metadata import load_prompt_from_png
from core.comfy_parser import parse_workflow
from core.workflow_diff import compare_nodes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ComfyUI Image Viewer")
        self.resize(1200, 800)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter to allow resizing the 3 panels
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Initialize the 3 main UI components
        self.gallery = GalleryPanel()
        self.viewer = ImageViewer()
        self.inspector = WorkflowInspector()
        
        # Add them to the splitter
        self.splitter.addWidget(self.gallery)
        self.splitter.addWidget(self.viewer)
        self.splitter.addWidget(self.inspector)
        
        # Set initial sizes (relative to layout)
        self.splitter.setSizes([300, 600, 300])
        
        # Set up menu
        self.setup_menu()
        
        # Connect signals
        self.gallery.image_selected.connect(self.on_image_selected)
        self.inspector.node_combo.currentIndexChanged.connect(self.on_inspector_node_changed)
        
        # State tracking for diffing
        self.previous_workflow_data = None
        self.current_workflow_data = None
        
        # Set up Shortcuts
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Set up window-level shortcuts that work regardless of focus."""
        QShortcut(QKeySequence(Qt.Key_Left), self, self.gallery.select_previous)
        QShortcut(QKeySequence(Qt.Key_Right), self, self.gallery.select_next)
        QShortcut(QKeySequence(Qt.Key_F), self, self.viewer.fit_in_view)
        QShortcut(QKeySequence(Qt.Key_Home), self, self.gallery.select_first)
        QShortcut(QKeySequence(Qt.Key_End), self, self.gallery.select_last)
        QShortcut(QKeySequence(Qt.Key_S), self, self.gallery.sort_by_date)
        QShortcut(QKeySequence(Qt.Key_Equal), self, self.viewer.zoom_in)
        QShortcut(QKeySequence(Qt.Key_Minus), self, self.viewer.zoom_out)
        QShortcut(QKeySequence(Qt.Key_I), self, self.viewer.toggle_info_overlay)
        QShortcut(QKeySequence(Qt.Key_F12), self, self.showFullScreen)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.showNormal)

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Folder", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if folder_path:
            self.gallery.load_folder(folder_path)

    def on_image_selected(self, path):
        """Called when an image is selected in the GalleryPanel."""
        # 1. Update Viewer
        self.viewer.load_image(path)
        
        # 2. Extract Metadata
        metadata = load_prompt_from_png(path)
        
        # Keep track of previous data to compare
        self.previous_workflow_data = self.current_workflow_data
        
        if metadata:
            # 3. Parse Workflow
            self.current_workflow_data = parse_workflow(metadata)
            
            # Save the currently selected node id to try and keep it active
            current_node_id = self.inspector.get_current_node_id()
            
            # 4. Update Inspector UI
            self.inspector.load_workflow(self.current_workflow_data)
            
            # Try to re-select the same node ID in the new image
            if current_node_id:
                index = self.inspector.node_combo.findData(current_node_id)
                if index >= 0:
                    self.inspector.node_combo.setCurrentIndex(index)
        else:
            self.current_workflow_data = None
            self.inspector.load_workflow({})

        # 5. Diff & Highlight (Task 9)
        self.run_diff()

    def on_inspector_node_changed(self, index):
        """When the user changes the selected node in the inspector, update highlights."""
        self.run_diff()

    def run_diff(self):
        """Compares the current node to the previous image's matching node and highlights."""
        if not self.current_workflow_data or not self.previous_workflow_data:
            # Nothing to diff against
            self.inspector.highlight_parameters([])
            return
            
        current_node_id = self.inspector.get_current_node_id()
        if not current_node_id:
            return
            
        current_node = self.current_workflow_data.get(current_node_id)
        prev_node = self.previous_workflow_data.get(current_node_id)
        
        if current_node and prev_node:
            changed_keys = compare_nodes(current_node, prev_node)
            self.inspector.highlight_parameters(changed_keys)
        else:
             # Node might not exist in previous image workflow
             self.inspector.highlight_parameters([])

    # keyPressEvent is now handled via QShortcut for better focus handling

