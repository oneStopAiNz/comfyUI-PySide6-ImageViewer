import sys
import os
from PySide6.QtWidgets import QApplication

def main():
    # Allow Qt to use high DPI scaling if configured by the user system
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling') else None
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps') else None

    app = QApplication(sys.argv)
    
    # Import MainWindow here after QApplication is initialized 
    # and QPixmaps are safe to create.
    from ui.main_window import MainWindow
    from ui.styles import get_dark_orange_stylesheet
    
    app.setStyleSheet(get_dark_orange_stylesheet())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    from PySide6 import QtCore
    main()
