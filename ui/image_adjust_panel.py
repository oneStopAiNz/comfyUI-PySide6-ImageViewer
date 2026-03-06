from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QSlider, QPlainTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class ImageAdjustPanel(QWidget):
    """
    A 4th pane that provides sliders for image adjustments and a text area for notes.
    """
    adjustments_changed = Signal(dict)
    save_notes_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Image Adjustments")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(title)
        
        # Scroll Area for Sliders
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        container = QWidget()
        self.controls_layout = QVBoxLayout(container)
        
        self.sliders = {}
        
        # Define Adjustments: (Key, Label, Min, Max, Default)
        adjustments = [
            ("exposure", "Exposure", -100, 100, 0),
            ("brightness", "Brightness", -100, 100, 0),
            ("contrast", "Contrast", -100, 100, 0),
            ("blacks", "Blacks", -100, 100, 0),
            ("whites", "Whites", -100, 100, 0),
            ("texture", "Texture", 0, 100, 0),
            ("clarity", "Clarity", 0, 100, 0),
            ("dehaze", "Dehaze", 0, 100, 0),
        ]
        
        for key, label, min_val, max_val, default in adjustments:
            self.add_adjustment_slider(key, label, min_val, max_val, default)
            
        self.controls_layout.addStretch()
        scroll.setWidget(container)
        self.layout.addWidget(scroll)
        
        # Divider
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #444; margin: 10px 0;")
        self.layout.addWidget(line)
        
        # Notes Section
        self.layout.addWidget(QLabel("Image Notes (Saved to Metadata)"))
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText("Enter notes here...")
        self.layout.addWidget(self.notes_edit)
        
        self.save_btn = QPushButton("Save Notes")
        self.save_btn.clicked.connect(self.on_save_clicked)
        self.layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset Adjustments")
        self.reset_btn.clicked.connect(self.reset_adjustments)
        self.layout.addWidget(self.reset_btn)

    def add_adjustment_slider(self, key, label_text, min_val, max_val, default):
        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        
        header_hbox = QHBoxLayout()
        label = QLabel(label_text)
        val_label = QLabel(str(default))
        header_hbox.addWidget(label)
        header_hbox.addStretch()
        header_hbox.addWidget(val_label)
        vbox.addLayout(header_hbox)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(lambda v: val_label.setText(str(v)))
        slider.valueChanged.connect(self.on_adjustment_changed)
        
        vbox.addWidget(slider)
        self.controls_layout.addLayout(vbox)
        self.sliders[key] = slider

    def on_adjustment_changed(self):
        data = {k: s.value() for k, s in self.sliders.items()}
        self.adjustments_changed.emit(data)

    def on_save_clicked(self):
        self.save_notes_requested.emit(self.notes_edit.toPlainText())

    def reset_adjustments(self):
        """Resets all sliders to defaults without triggering multiple updates."""
        self.blockSignals(True)
        for slider in self.sliders.values():
            # Most defaults are 0, but check if we need specific ones
            slider.setValue(0)
        self.blockSignals(False)
        self.on_adjustment_changed()

    def set_notes(self, text):
        self.notes_edit.setPlainText(text if text else "")
