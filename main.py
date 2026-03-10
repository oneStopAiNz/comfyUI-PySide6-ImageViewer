import sys
import os
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    
    # Calculate font size based on DPI
    # standard DPI is 96. We scale from a base of 10pt or 12pt.
    screen = app.primaryScreen()
    if screen:
        dpi = screen.logicalDotsPerInch()
        # Scale factor: 96 DPI -> 1.0, 144 DPI -> 1.5, etc.
        # We'll use 11pt as a comfortable base for 96 DPI
        base_font_size = max(11, int(11 * (dpi / 96.0)))
    else:
        base_font_size = 11

    # Import MainWindow here after QApplication is initialized 
    # and QPixmaps are safe to create.
    from ui.main_window import MainWindow
    from ui.styles import get_dark_orange_stylesheet
    
    app.setStyleSheet(get_dark_orange_stylesheet(base_font_size))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    from PySide6 import QtCore
    main()
