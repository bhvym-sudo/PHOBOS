def get_dark_stylesheet():
    return """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 12px;
    }
    
    QLabel {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
    }
    
    QPushButton {
        background-color: #4a90e2;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
        min-width: 100px;
    }
    
    QPushButton:hover {
        background-color: #357abd;
    }
    
    QPushButton:pressed {
        background-color: #2563eb;
    }
    
    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }
    
    QPushButton#stopButton {
        background-color: #dc3545;
    }
    
    QPushButton#stopButton:hover {
        background-color: #c82333;
    }
    
    QComboBox {
        background-color: #3c3c3c;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 8px 12px;
        border-radius: 4px;
        min-width: 150px;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iNiIgdmlld0JveD0iMCAwIDEwIDYiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik01IDZMMCAwaDEwTDUgNnoiIGZpbGw9IiNmZmZmZmYiLz4KPC9zdmc+);
    }
    
    QComboBox QAbstractItemView {
        background-color: #3c3c3c;
        color: #ffffff;
        border: 1px solid #555555;
        selection-background-color: #4a90e2;
    }
    
    QTextEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 8px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 11px;
        line-height: 1.4;
    }
    
    QScrollBar:vertical {
        background-color: #3c3c3c;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #777777;
    }
    """

