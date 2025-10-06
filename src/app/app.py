#!/usr/bin/env python3
"""
Simple PyQt5 GUI for running Linux commands / processes.
"""

import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QLineEdit
)
from PyQt5.QtCore import QProcess


class ProcessManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux Process Manager")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout()

        # Input for command
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("Command:"))
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("e.g., ls -l /home")
        cmd_layout.addWidget(self.cmd_input)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_command)
        cmd_layout.addWidget(self.run_btn)

        layout.addLayout(cmd_layout)

        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output)

        # Kill button
        self.kill_btn = QPushButton("Kill Process")
        self.kill_btn.clicked.connect(self.kill_process)
        self.kill_btn.setEnabled(False)
        layout.addWidget(self.kill_btn)

        self.setLayout(layout)

        # QProcess for async execution
        self.process = None

    def run_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            self.output.append("⚠️ No command entered.")
            return

        # Kill existing process if running
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()

        self.process = QProcess(self)
        self.process.setProgram("bash")
        self.process.setArguments(["-c", cmd])
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        self.output.append(f"\n▶ Running: {cmd}")
        self.process.start()
        self.kill_btn.setEnabled(True)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output.append(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.output.append(f"❌ {data}")

    def process_finished(self):
        self.output.append("✅ Process finished.")
        self.kill_btn.setEnabled(False)

    def kill_process(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.output.append("⛔ Process killed.")
            self.kill_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = ProcessManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

