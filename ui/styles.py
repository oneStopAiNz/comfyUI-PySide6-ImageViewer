def get_dark_orange_stylesheet():
    return """
    QMainWindow {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    QWidget {
        background-color: #1e1e1e;
        color: #e0e0e0;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    QSplitter::handle {
        background-color: #333333;
    }
    
    /* Menu Bar Styling */
    QMenuBar {
        background-color: #252525;
        border-bottom: 1px solid #333333;
    }
    QMenuBar::item:selected {
        background-color: #d35400;
    }
    
    QMenu {
        background-color: #252525;
        border: 1px solid #333333;
    }
    QMenu::item:selected {
        background-color: #d35400;
    }

    /* List Widget (Gallery) */
    QListWidget {
        background-color: #1e1e1e;
        border: none;
        outline: none;
    }
    QListWidget::item {
        border-radius: 4px;
        padding: 5px;
        color: #e0e0e0;
    }
    QListWidget::item:selected {
        background-color: #d35400;
        color: white;
    }
    QListWidget::item:hover {
        background-color: #3d3d3d;
    }

    /* Table Widget (Inspector) */
    QTableWidget {
        background-color: #252525;
        gridline-color: #333333;
        border: 1px solid #333333;
        border-radius: 4px;
    }
    QHeaderView::section {
        background-color: #333333;
        padding: 4px;
        border: 1px solid #1e1e1e;
        color: #e0e0e0;
    }
    QTableWidget QTableCornerButton::section {
        background-color: #333333;
    }

    /* Combo Box */
    QComboBox {
        background-color: #333333;
        border: 1px solid #444444;
        border-radius: 3px;
        padding: 5px;
        min-height: 25px;
    }
    QComboBox:hover {
        border: 1px solid #ff8c00;
    }
    QComboBox::drop-down {
        border-left: 1px solid #444444;
    }

    /* Scroll Bars */
    QScrollBar:vertical {
        background: #1e1e1e;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #444444;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #ff8c00;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background: #1e1e1e;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #444444;
        min-width: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #ff8c00;
    }
    """
