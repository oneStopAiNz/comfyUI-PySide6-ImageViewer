import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QFileDialog, QMessageBox
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtCore import Qt

from ui.gallery_panel import GalleryPanel
from ui.image_viewer import ImageViewer
from ui.workflow_inspector import WorkflowInspector
from ui.image_adjust_panel import ImageAdjustPanel
from utils.png_metadata import load_metadata_from_png, save_metadata_to_png, json
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
        self.adjuster = ImageAdjustPanel()
        
        # Add them to the splitter
        self.splitter.addWidget(self.gallery)
        self.splitter.addWidget(self.viewer)
        self.splitter.addWidget(self.inspector)
        self.splitter.addWidget(self.adjuster)
        
        # Set initial sizes (relative to layout)
        self.splitter.setSizes([200, 500, 250, 250])
        
        # Set up menu
        self.setup_menu()
        
        # Connect signals
        self.gallery.image_selected.connect(self.on_image_selected)
        self.inspector.node_combo.currentIndexChanged.connect(self.on_inspector_node_changed)
        self.adjuster.adjustments_changed.connect(self.viewer.apply_adjustments)
        self.adjuster.save_notes_requested.connect(self.on_save_notes)
        self.adjuster.color_tag_selected.connect(self.on_color_tag_selected)
        
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
        
        # Numeric Zoom Shortcuts
        QShortcut(QKeySequence(Qt.Key_1), self, lambda: self.viewer.set_zoom_level(1.0))
        QShortcut(QKeySequence(Qt.Key_2), self, lambda: self.viewer.set_zoom_level(2.0))
        QShortcut(QKeySequence(Qt.Key_3), self, lambda: self.viewer.set_zoom_level(3.0))
        QShortcut(QKeySequence(Qt.Key_4), self, lambda: self.viewer.set_zoom_level(4.0))
        QShortcut(QKeySequence(Qt.Key_5), self, lambda: self.viewer.set_zoom_level(5.0))
        
        QShortcut(QKeySequence(Qt.Key_I), self, self.viewer.toggle_info_overlay)
        QShortcut(QKeySequence(Qt.Key_A), self, self.tag_image_a)
        QShortcut(QKeySequence(Qt.Key_B), self, self.tag_image_b)
        QShortcut(QKeySequence(Qt.Key_C), self, self.toggle_comparison)

        # Color Tagging Shortcuts (Alt+1..5)
        QShortcut(QKeySequence("Alt+1"), self, lambda: self.on_color_tag_selected("red"))
        QShortcut(QKeySequence("Alt+2"), self, lambda: self.on_color_tag_selected("yellow"))
        QShortcut(QKeySequence("Alt+3"), self, lambda: self.on_color_tag_selected("green"))
        QShortcut(QKeySequence("Alt+4"), self, lambda: self.on_color_tag_selected("blue"))
        QShortcut(QKeySequence("Alt+5"), self, lambda: self.on_color_tag_selected("magenta"))
        QShortcut(QKeySequence("Alt+0"), self, lambda: self.on_color_tag_selected(None))

        # Folder Reload
        QShortcut(QKeySequence("Ctrl+R"), self, self.gallery.reload_folder)

        QShortcut(QKeySequence(Qt.Key_F12), self, self.showFullScreen)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.showNormal)

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Folder", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)
        
        reload_action = QAction("Reload Folder", self)
        reload_action.setShortcut("Ctrl+R")
        reload_action.triggered.connect(self.gallery.reload_folder)
        file_menu.addAction(reload_action)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if folder_path:
            self.gallery.load_folder(folder_path)

    def on_image_selected(self, path):
        """Called when an image is selected in the GalleryPanel."""
        # 1. Update Viewer
        self.viewer.load_image(path)
        
        # 2. Extract Metadata (Workflow + Notes)
        all_metadata = load_metadata_from_png(path)
        
        # Workflow parsing
        workflow_str = all_metadata.get('workflow') or all_metadata.get('prompt')
        
        # Keep track of previous data to compare
        self.previous_workflow_data = self.current_workflow_data
        
        if workflow_str:
            # 3. Parse Workflow
            try:
                workflow_json = json.loads(workflow_str)
                self.current_workflow_data = parse_workflow(workflow_json)
            except:
                self.current_workflow_data = None
            
            # Save the currently selected node id to try and keep it active
            current_node_id = self.inspector.get_current_node_id()
            
            # 4. Update Inspector UI
            self.inspector.load_workflow(self.current_workflow_data or {})
            
            # Try to re-select the same node ID in the new image
            if current_node_id:
                index = self.inspector.node_combo.findData(current_node_id)
                if index >= 0:
                    self.inspector.node_combo.setCurrentIndex(index)
        else:
            self.current_workflow_data = None
            self.inspector.load_workflow({})

        # Load notes and color into the Adjuster pane
        notes = all_metadata.get('notes', "")
        color_tag = all_metadata.get('color_tag', None)
        self.adjuster.set_notes(notes)
        self.adjuster.reset_adjustments()
        
        # Update Viewer with tag info
        self.viewer.update_overlay(path, self.viewer.pixmap_item.pixmap(), color_tag)

        # 5. Diff & Highlight
        self.run_diff()

    def on_save_notes(self, notes):
        """Saves notes to the current image file."""
        path = self.gallery.get_current_image_path()
        if path:
            success = save_metadata_to_png(path, {'notes': notes})
            if success:
                self.statusBar().showMessage("Notes saved to image metadata.", 3000)
            else:
                QMessageBox.warning(self, "Save Failed", "Could not save notes to image.")

    def on_color_tag_selected(self, color):
        """Applies a color tag to the current image."""
        path = self.gallery.get_current_image_path()
        if path:
            success = save_metadata_to_png(path, {'color_tag': color or ""})
            if success:
                self.statusBar().showMessage(f"Tagged as {color if color else 'None'}", 3000)
                # Update UI immediately
                self.gallery.update_image_tag(path, color)
                self.viewer.update_overlay(path, self.viewer.pixmap_item.pixmap(), color)
            else:
                QMessageBox.warning(self, "Tag Failed", "Could not save color tag to image.")

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

    def toggle_comparison(self):
        """Toggles the wipe comparison mode in the viewer."""
        active = self.viewer.toggle_comparison_mode()
        if not active and not (self.viewer.path_a and self.viewer.path_b):
             QMessageBox.information(self, "Comparison Mode", "Please tag two images first using keys 'A' and 'B'.")

    def tag_image_a(self):
        """Tags the currently selected image as Image A."""
        path = self.gallery.get_current_image_path()
        if path:
            self.viewer.set_image_a(path)
            # Temporary overlay feedback
            self.statusBar().showMessage(f"Tagged as Image A: {os.path.basename(path)}", 3000)

    def tag_image_b(self):
        """Tags the currently selected image as Image B."""
        path = self.gallery.get_current_image_path()
        if path:
            self.viewer.set_image_b(path)
            # Temporary overlay feedback
            self.statusBar().showMessage(f"Tagged as Image B: {os.path.basename(path)}", 3000)

    # keyPressEvent is now handled via QShortcut for better focus handling

