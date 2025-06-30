"""
Modern A2A/MCP Client GUI using PySide6
Run with: python A2A/a2a_client_gui_qt.py
"""
import sys
import json
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QTextEdit, QFormLayout, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal

A2A_URL = "http://localhost:9000/a2a"
MCP_URL = "http://localhost:8090/mcp/"
MCP_TOOLS = {
    "explain_concept": ["subject", "concept"],
    "quiz_question": ["subject", "topic"],
    "summarize_text": ["text"],
    "list_coffee_types": []
}
A2A_SKILLS = ["triage", "math", "history", "coffee"]

class Worker(QThread):
    resultReady = Signal(object)
    def __init__(self, mode, skill, tool, args):
        super().__init__()
        self.mode = mode
        self.skill = skill
        self.tool = tool
        self.args = args
    def run(self):
        try:
            if self.mode == "A2A":
                if self.skill == "triage":
                    params = {"query": self.args.get("question", "")}
                else:
                    params = {"question": self.args.get("question", "")}
                payload = {
                    "jsonrpc": "2.0",
                    "method": self.skill,
                    "params": params,
                    "id": "1"
                }
                response = requests.post(A2A_URL, json=payload, timeout=10)
                response.raise_for_status()
                data = response.json()
                if "result" in data:
                    val = next(iter(data["result"].values()))
                    self.resultReady.emit(val)
                elif "error" in data:
                    self.resultReady.emit(f"Error: {data['error']['message']}")
                else:
                    self.resultReady.emit("Unknown response format.")
            else:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": self.tool,
                        "arguments": self.args
                    },
                    "id": "1"
                }
                headers = {"Accept": "application/json, text/event-stream"}
                response = requests.post(MCP_URL, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")
                if "text/event-stream" in content_type:
                    lines = response.text.splitlines()
                    data_lines = [line[6:] for line in lines if line.startswith("data: ")]
                    if data_lines:
                        data = json.loads(data_lines[-1])
                    else:
                        self.resultReady.emit("No data received in event stream.")
                        return
                else:
                    data = response.json()
                if "result" in data:
                    content = data["result"].get("content")
                    if isinstance(content, list) and content and "text" in content[0]:
                        self.resultReady.emit(content[0]["text"])
                    else:
                        self.resultReady.emit(json.dumps(data["result"], indent=2))
                elif "error" in data:
                    self.resultReady.emit(f"Error: {data['error']['message']}")
                else:
                    self.resultReady.emit("Unknown response format.")
        except Exception as e:
            self.resultReady.emit(f"Request failed: {e}")

class A2AClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A2A/MCP Agent Client (Modern)")
        self.setMinimumSize(650, 500)
        self.mode = "A2A"
        self.worker = None  # Store the worker thread
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["A2A", "MCP Tool"])
        self.mode_combo.currentTextChanged.connect(self.update_mode)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        main_layout.addLayout(mode_layout)
        # Skill/tool selection
        self.skill_label = QLabel("Select Skill:")
        self.skill_combo = QComboBox()
        self.skill_combo.addItems(A2A_SKILLS)
        self.skill_combo.currentTextChanged.connect(self.update_skill)
        self.tool_label = QLabel("Select MCP Tool:")
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(list(MCP_TOOLS.keys()))
        self.tool_combo.currentTextChanged.connect(self.update_tool_args)
        # Dynamic argument fields
        self.form_layout = QFormLayout()
        self.arg_widgets = {}
        # Question entry (A2A)
        self.question_label = QLabel("Enter your question:")
        self.question_entry = QLineEdit()
        self.question_entry.returnPressed.connect(self.ask_agent)
        # Ask button
        self.ask_button = QPushButton("Ask Agent")
        self.ask_button.clicked.connect(self.ask_agent)
        # Response display
        self.response_label = QLabel("Agent Response:")
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setMinimumHeight(120)
        self.response_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Assemble
        main_layout.addSpacing(10)
        main_layout.addWidget(self.skill_label)
        main_layout.addWidget(self.skill_combo)
        main_layout.addWidget(self.tool_label)
        main_layout.addWidget(self.tool_combo)
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(self.question_label)
        main_layout.addWidget(self.question_entry)
        main_layout.addWidget(self.ask_button)
        main_layout.addWidget(self.response_label)
        main_layout.addWidget(self.response_text)
        self.setLayout(main_layout)
        self.update_mode()

    def update_mode(self):
        self.mode = self.mode_combo.currentText()
        if self.mode == "A2A":
            self.skill_label.show()
            self.skill_combo.show()
            self.question_label.show()
            self.question_entry.show()
            self.tool_label.hide()
            self.tool_combo.hide()
            # Clear MCP tool args
            for i in reversed(range(self.form_layout.count())):
                item = self.form_layout.itemAt(i)
                if item.widget():
                    item.widget().deleteLater()
            self.arg_widgets = {}
        else:
            self.skill_label.hide()
            self.skill_combo.hide()
            self.question_label.hide()
            self.question_entry.hide()
            self.tool_label.show()
            self.tool_combo.show()
            self.update_tool_args()

    def update_skill(self):
        # For future: update skill-specific UI
        pass

    def update_tool_args(self):
        # Remove old widgets
        for i in reversed(range(self.form_layout.count())):
            item = self.form_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        self.arg_widgets = {}
        tool = self.tool_combo.currentText()
        args = MCP_TOOLS.get(tool, [])
        for arg in args:
            label = QLabel(f"{arg.capitalize()}:")
            entry = QLineEdit()
            self.form_layout.addRow(label, entry)
            self.arg_widgets[arg] = entry

    def ask_agent(self):
        self.ask_button.setEnabled(False)
        self.response_text.setPlainText("Waiting for response...")
        mode = self.mode_combo.currentText()
        if mode == "A2A":
            skill = self.skill_combo.currentText()
            question = self.question_entry.text().strip()
            if not question:
                self.response_text.setPlainText("Please enter a question.")
                self.ask_button.setEnabled(True)
                return
            args = {"question": question}
            self.worker = Worker(mode, skill, None, args)
        else:
            tool = self.tool_combo.currentText()
            args = {k: w.text().strip() for k, w in self.arg_widgets.items()}
            if any(not val for val in args.values()):
                self.response_text.setPlainText("Please fill in all tool arguments.")
                self.ask_button.setEnabled(True)
                return
            self.worker = Worker(mode, None, tool, args)
        self.worker.resultReady.connect(self.display_response)
        self.worker.finished.connect(lambda: self.ask_button.setEnabled(True))
        self.worker.finished.connect(self.cleanup_worker)
        self.worker.start()

    def cleanup_worker(self):
        self.worker = None

    def display_response(self, text):
        self.response_text.setPlainText(str(text))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = A2AClientGUI()
    gui.show()
    sys.exit(app.exec()) 