import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                            QLabel, QTextEdit, QPushButton, QComboBox, QFrame, 
                            QSizePolicy, QTabWidget, QSplitter, QLineEdit, QMessageBox,
                            QListWidget, QListWidgetItem)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from ui.styles import get_dark_stylesheet
from config.app_config import TIMER_INTERVALS, DEFAULT_INTERVAL
from core.monitor import MonitorWorker

class DarkWebMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PHOBOS - Dark Web Monitoring Division")
        self.setStyleSheet(get_dark_stylesheet())
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_monitoring)
        self.is_monitoring = False
        self.current_interval = DEFAULT_INTERVAL
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = self.create_header()
        content = self.create_content()
        
        main_layout.addWidget(header)
        main_layout.addWidget(content)
        
    def create_header(self):
        header_widget = QFrame()
        header_widget.setObjectName("headerWidget")
        header_widget.setStyleSheet("""
            QFrame#headerWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                                          stop: 0 #1a1a2e, stop: 1 #16213e);
                border-bottom: 2px solid #4a90e2;
                min-height: 120px;
                max-height: 120px;
            }
        """)
        
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(30, 20, 30, 20)
        
        app_name = QLabel("PHOBOS")
        app_name.setObjectName("appName")
        app_name.setStyleSheet("""
            QLabel#appName {
                color: #ffffff;
                font-weight: bold;
                letter-spacing: 3px;
                background: transparent;
                font-size: 56px;
            }
        """)
        
        left_header = QVBoxLayout()
        left_header.addWidget(app_name)
        left_header.setSpacing(5)
        
        layout.addLayout(left_header)
        layout.addStretch()
        
        return header_widget

    def create_content(self):
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel_with_tabs()
        
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 2)
        
        return content_widget
        
    def create_left_panel(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setLineWidth(1)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        
        header = QLabel("Control Panel")
        header.setObjectName("headerLabel")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 15px; color: #ffffff;")
        
        layout.addWidget(header)
        
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(15)
        
        interval_label = QLabel("Monitor Interval:")
        interval_label.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        
        self.interval_combo = QComboBox()
        for label, value in TIMER_INTERVALS:
            self.interval_combo.addItem(label, value)
        
        default_index = next((i for i, (_, v) in enumerate(TIMER_INTERVALS) if v == DEFAULT_INTERVAL), 1)
        self.interval_combo.setCurrentIndex(default_index)
        self.interval_combo.currentIndexChanged.connect(self.on_interval_changed)
        
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)
        
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-size: 16px; margin-top: 20px; margin-bottom: 5px;")
        
        self.status_text = QLabel("Idle")
        self.status_text.setStyleSheet("color: #cccccc; font-size: 14px; padding: 10px; background-color: #1e1e1e; border-radius: 4px;")
        
        url_label = QLabel("Add URL to Monitor:")
        url_label.setStyleSheet("font-size: 16px; margin-top: 20px; margin-bottom: 5px;")
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to monitor (e.g., https://example.com)")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a90e2;
            }
        """)
        self.url_input.returnPressed.connect(self.add_url)
        
        self.add_url_button = QPushButton("Add URL")
        self.add_url_button.clicked.connect(self.add_url)
        
        controls_layout.addWidget(interval_label)
        controls_layout.addWidget(self.interval_combo)
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(status_label)
        controls_layout.addWidget(self.status_text)
        controls_layout.addWidget(url_label)
        controls_layout.addWidget(self.url_input)
        controls_layout.addWidget(self.add_url_button)
        controls_layout.addStretch()
        
        layout.addWidget(controls_frame)
        layout.addStretch()
        
        footer = QLabel("Secured by Government Cybersecurity Protocol")
        footer.setStyleSheet("font-size: 12px; color: #888888; text-align: center; padding: 20px;")
        layout.addWidget(footer)
        
        return panel
    
    def add_url(self):
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL to monitor.")
            return
        
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Invalid URL", "URL must start with http:// or https://")
            return
        
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(app_dir)
            scraper_dir = os.path.join(project_root, "scraper")
            urls_file = os.path.join(scraper_dir, "url.txt")
            
            existing_urls = set()
            if os.path.exists(urls_file):
                with open(urls_file, 'r', encoding='utf-8') as f:
                    existing_urls = set(line.strip() for line in f.readlines())
            
            if url in existing_urls:
                QMessageBox.information(self, "Duplicate URL", "This URL is already being monitored.")
                self.url_input.clear()
                return
            
            with open(urls_file, 'a', encoding='utf-8') as f:
                f.write(url + '\n')
            
            QMessageBox.information(self, "URL Added", f"Successfully added URL to monitoring list:\n{url}")
            self.url_input.clear()
            self.refresh_url_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add URL: {str(e)}")
    
    def create_right_panel_with_tabs(self):
        tab_widget = QTabWidget()
        tab_widget.setObjectName("mainTabWidget")
        tab_widget.setStyleSheet("""
            QTabWidget#mainTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
                border-radius: 4px;
            }
            
            QTabWidget#mainTabWidget::tab-bar {
                left: 5px;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #404040, stop: 1 #303030);
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 120px;
                padding: 12px 16px;
                margin-right: 2px;
                color: #cccccc;
                font-size: 13px;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #4a90e2, stop: 1 #357abd);
                color: #ffffff;
                border-bottom: 1px solid #2b2b2b;
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #505050, stop: 1 #404040);
            }
        """)
        
        ai_results_tab = self.create_ai_results_tab()
        data_logs_tab = self.create_data_logs_tab()
        urls_tab = self.create_urls_tab()
        system_logs_tab = self.create_system_logs_tab()
        
        tab_widget.addTab(ai_results_tab, "AI Analysis")
        tab_widget.addTab(data_logs_tab, "Data Logs")
        tab_widget.addTab(urls_tab, "URLs")
        tab_widget.addTab(system_logs_tab, "System Logs")
        
        return tab_widget
    
    def create_ai_results_tab(self):
        ai_tab = QWidget()
        layout = QVBoxLayout(ai_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        ai_label = QLabel("AI Analysis Results")
        ai_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #ffffff;")
        
        self.ai_log = QTextEdit()
        self.ai_log.setPlainText("AI analysis will appear here when monitoring starts...")
        self.ai_log.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 22px;
                line-height: 1.5;
            }
        """)
        
        layout.addWidget(ai_label)
        layout.addWidget(self.ai_log)
        
        return ai_tab
    
    def create_data_logs_tab(self):
        data_tab = QWidget()
        layout = QVBoxLayout(data_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #555555;
                height: 3px;
            }
            QSplitter::handle:hover {
                background-color: #777777;
            }
        """)
        
        scraped_frame = QFrame()
        scraped_layout = QVBoxLayout(scraped_frame)
        scraped_layout.setSpacing(5)
        scraped_layout.setContentsMargins(0, 0, 0, 5)
        
        scraped_label = QLabel("Scraped Data (data.json)")
        scraped_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        self.scraped_log = QTextEdit()
        self.scraped_log.setPlainText("Waiting for monitoring to start...")
        self.scraped_log.setStyleSheet("font-size: 22px;")
        
        scraped_layout.addWidget(scraped_label)
        scraped_layout.addWidget(self.scraped_log)
        
        parsed_frame = QFrame()
        parsed_layout = QVBoxLayout(parsed_frame)
        parsed_layout.setSpacing(5)
        parsed_layout.setContentsMargins(0, 5, 0, 0)
        
        parsed_label = QLabel("Parsed Data (results.json)")
        parsed_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        self.parsed_log = QTextEdit()
        self.parsed_log.setPlainText("Waiting for monitoring to start...")
        self.parsed_log.setStyleSheet("font-size: 22px;")
        
        parsed_layout.addWidget(parsed_label)
        parsed_layout.addWidget(self.parsed_log)
        
        splitter.addWidget(scraped_frame)
        splitter.addWidget(parsed_frame)
        splitter.setSizes([300, 300])
        
        layout.addWidget(splitter)
        
        return data_tab

    def create_urls_tab(self):
        urls_tab = QWidget()
        layout = QVBoxLayout(urls_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        urls_label = QLabel("Monitored URLs")
        urls_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px; color: #ffffff;")
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.refresh_url_list)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2968a3;
            }
        """)
        
        self.clear_all_button = QPushButton("Clear All URLs")
        self.clear_all_button.clicked.connect(self.clear_all_urls)
        self.clear_all_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #a71e2a;
            }
        """)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.clear_all_button)
        buttons_layout.addStretch()
        
        self.urls_list = QListWidget()
        self.urls_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #333333;
                margin: 5px;
                border-radius: 6px;
                background-color: #2a2a2a;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
            }
        """)
        
        layout.addWidget(urls_label)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.urls_list)
        
        self.refresh_url_list()
        
        return urls_tab

    def create_system_logs_tab(self):
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        logs_header = QHBoxLayout()
        
        logs_label = QLabel("System Logs")
        logs_label.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 10px; color: #ffffff;")
        
        clear_logs_button = QPushButton("Clear Logs")
        clear_logs_button.clicked.connect(self.clear_system_logs)
        clear_logs_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 22px;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        logs_header.addWidget(logs_label)
        logs_header.addStretch()
        logs_header.addWidget(clear_logs_button)
        
        self.system_log = QTextEdit()
        self.system_log.setPlainText("System logs will appear here...")
        self.system_log.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #58a6ff;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 22px;
                line-height: 1.4;
            }
        """)
        self.system_log.setReadOnly(True)
        
        layout.addLayout(logs_header)
        layout.addWidget(self.system_log)
        
        return logs_tab

    def log_system_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "#58a6ff",
            "WARNING": "#f1c40f", 
            "ERROR": "#e74c3c",
            "SUCCESS": "#2ecc71"
        }
        
        color = color_map.get(level, "#58a6ff")
        formatted_message = f'<span style="color: {color};">[{timestamp}] [{level}] {message}</span>'
        
        self.system_log.append(formatted_message)
        self.system_log.verticalScrollBar().setValue(self.system_log.verticalScrollBar().maximum())

    def clear_system_logs(self):
        self.system_log.clear()
        self.log_system_message("System logs cleared", "INFO")

    def refresh_url_list(self):
        self.urls_list.clear()
        
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(app_dir)
            scraper_dir = os.path.join(project_root, "scraper")
            urls_file = os.path.join(scraper_dir, "url.txt")
            
            if not os.path.exists(urls_file):
                item = QListWidgetItem("No URLs found. Add URLs using the control panel.")
                item.setForeground(Qt.gray)
                self.urls_list.addItem(item)
                return
            
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
            
            if not urls:
                item = QListWidgetItem("No URLs found. Add URLs using the control panel.")
                item.setForeground(Qt.gray)
                self.urls_list.addItem(item)
                return
            
            for i, url in enumerate(urls, 1):
                item_widget = QWidget()
                item_widget.setMinimumHeight(80)
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(15, 15, 15, 15)
                item_layout.setSpacing(20)
                
                url_container = QVBoxLayout()
                
                number_label = QLabel(f"#{i}")
                number_label.setStyleSheet("""
                    color: #4a90e2; 
                    font-size: 16px; 
                    font-weight: bold;
                    margin-bottom: 5px;
                """)
                
                url_label = QLabel(url)
                url_label.setStyleSheet("""
                    color: #ffffff; 
                    font-size: 14px;
                    background-color: #333333;
                    padding: 12px;
                    border-radius: 6px;
                    border: 1px solid #555555;
                    min-height: 20px;
                """)
                url_label.setWordWrap(True)
                url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                
                url_container.addWidget(number_label)
                url_container.addWidget(url_label)
                
                remove_button = QPushButton("Remove")
                remove_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 15px 25px;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: bold;
                        min-width: 100px;
                        max-width: 120px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                    QPushButton:pressed {
                        background-color: #a71e2a;
                    }
                """)
                remove_button.clicked.connect(lambda checked, url=url: self.remove_url(url))
                
                item_layout.addLayout(url_container, 1)
                item_layout.addWidget(remove_button)
                
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())
                
                self.urls_list.addItem(list_item)
                self.urls_list.setItemWidget(list_item, item_widget)
                
        except Exception as e:
            item = QListWidgetItem(f"Error loading URLs: {str(e)}")
            item.setForeground(Qt.red)
            self.urls_list.addItem(item)

    def remove_url(self, url_to_remove):
        reply = QMessageBox.question(self, "Remove URL", 
                                   f"Are you sure you want to remove this URL?\n\n{url_to_remove}",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(app_dir)
            scraper_dir = os.path.join(project_root, "scraper")
            urls_file = os.path.join(scraper_dir, "url.txt")
            
            if not os.path.exists(urls_file):
                return
            
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
            
            if url_to_remove in urls:
                urls.remove(url_to_remove)
                
                with open(urls_file, 'w', encoding='utf-8') as f:
                    for url in urls:
                        f.write(url + '\n')
                
                QMessageBox.information(self, "URL Removed", "URL successfully removed from monitoring list.")
                self.refresh_url_list()
                self.log_system_message(f"URL removed from monitoring: {url_to_remove}", "SUCCESS")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove URL: {str(e)}")
            self.log_system_message(f"Failed to remove URL: {str(e)}", "ERROR")

    def clear_all_urls(self):
        reply = QMessageBox.question(self, "Clear All URLs", 
                                   "Are you sure you want to remove all monitored URLs?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(app_dir)
            scraper_dir = os.path.join(project_root, "scraper")
            urls_file = os.path.join(scraper_dir, "url.txt")
            
            if os.path.exists(urls_file):
                with open(urls_file, 'w', encoding='utf-8') as f:
                    f.write('')
                
                QMessageBox.information(self, "URLs Cleared", "All URLs have been removed from monitoring list.")
                self.refresh_url_list()
                self.log_system_message("All URLs cleared from monitoring list", "SUCCESS")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear URLs: {str(e)}")
            self.log_system_message(f"Failed to clear URLs: {str(e)}", "ERROR")
    
    def on_interval_changed(self, index):
        _, value = TIMER_INTERVALS[index]
        self.current_interval = value
        self.log_system_message(f"Monitor interval changed to {value} seconds", "INFO")
        if self.is_monitoring:
            self.timer.setInterval(value * 1000)
    
    def start_monitoring(self):
        self.is_monitoring = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_text.setText("Monitoring Active")
        self.status_text.setStyleSheet("color: #28a745; font-size: 14px; padding: 10px; background-color: #1e1e1e; border-radius: 4px;")
        
        self.timer.start(self.current_interval * 1000)
        self.log_system_message("Monitoring started", "SUCCESS")
        self.run_monitoring()
    
    def stop_monitoring(self):
        self.is_monitoring = False
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_text.setText("Monitoring Stopped")
        self.status_text.setStyleSheet("color: #dc3545; font-size: 14px; padding: 10px; background-color: #1e1e1e; border-radius: 4px;")
        self.log_system_message("Monitoring stopped", "INFO")
    
    def run_monitoring(self):
        self.log_system_message(f"Timer triggered - monitoring active: {self.is_monitoring}", "INFO")
        if not self.is_monitoring:
            return

        if hasattr(self, 'worker') and self.worker.isRunning():
            self.log_system_message("Previous worker still running, skipping...", "WARNING")
            return

        self.log_system_message("Starting MonitorWorker", "INFO")
        self.worker = MonitorWorker()
        self.worker.scraped_data.connect(self.update_scraped_log)
        self.worker.parsed_data.connect(self.update_parsed_log)
        self.worker.ai_results.connect(self.update_ai_log)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

    def worker_finished(self):
        self.log_system_message("MonitorWorker finished", "SUCCESS")
    
    def update_scraped_log(self, data):
        self.scraped_log.setPlainText(data)
        self.scraped_log.verticalScrollBar().setValue(self.scraped_log.verticalScrollBar().maximum())
        self.log_system_message("Scraped data updated", "SUCCESS")
    
    def update_parsed_log(self, data):
        self.parsed_log.setPlainText(data)
        self.parsed_log.verticalScrollBar().setValue(self.parsed_log.verticalScrollBar().maximum())
        self.log_system_message("Parsed data updated", "SUCCESS")
    
    def update_ai_log(self, data):
        self.ai_log.setPlainText(data)
        self.ai_log.verticalScrollBar().setValue(self.ai_log.verticalScrollBar().maximum())
        self.log_system_message("AI analysis completed", "SUCCESS")

