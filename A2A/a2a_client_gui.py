import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading

A2A_URL = "http://localhost:9000/a2a"
MCP_URL = "http://localhost:8090/mcp/"
MCP_TOOLS = {
    "explain_concept": ["subject", "concept"],
    "quiz_question": ["subject", "topic"],
    "summarize_text": ["text"],
    "list_coffee_types": []
}

class A2AClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("A2A Agent Client")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.style = ttk.Style()
        # Use a modern theme if available
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6)
        self.style.configure("TLabel", font=("Segoe UI", 11))
        self.style.configure("TCombobox", font=("Segoe UI", 11))
        self.style.configure("TEntry", font=("Segoe UI", 11))

        main_frame = ttk.Frame(root, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Mode selection
        ttk.Label(main_frame, text="Mode:").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.mode_var = tk.StringVar(value="A2A")
        self.mode_combo = ttk.Combobox(main_frame, textvariable=self.mode_var, values=["A2A", "MCP Tool"], state="readonly", width=15)
        self.mode_combo.grid(row=0, column=1, sticky="w", pady=(0, 8), padx=(10, 0))
        self.mode_combo.bind("<<ComboboxSelected>>", lambda e: self.update_mode())

        # Skill selection (A2A)
        self.skill_label = ttk.Label(main_frame, text="Select Skill:")
        self.skill_label.grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.skill_var = tk.StringVar(value="triage")
        self.skill_combo = ttk.Combobox(main_frame, textvariable=self.skill_var, values=["triage", "math", "history", "coffee"], state="readonly", width=15)
        self.skill_combo.grid(row=1, column=1, sticky="w", pady=(0, 8), padx=(10, 0))

        # MCP tool selection
        self.tool_label = ttk.Label(main_frame, text="Select MCP Tool:")
        self.tool_var = tk.StringVar(value="explain_concept")
        self.tool_combo = ttk.Combobox(main_frame, textvariable=self.tool_var, values=list(MCP_TOOLS.keys()), state="readonly", width=20)
        self.tool_args_frame = ttk.Frame(main_frame)
        self.tool_arg_vars = {}
        self.tool_label.grid_remove()
        self.tool_combo.grid_remove()
        self.tool_args_frame.grid_remove()

        # Question entry (A2A)
        self.question_label = ttk.Label(main_frame, text="Enter your question:")
        self.question_label.grid(row=2, column=0, sticky="w", pady=(0, 8))
        self.question_entry = ttk.Entry(main_frame, width=50)
        self.question_entry.grid(row=2, column=1, sticky="w", pady=(0, 8), padx=(10, 0))
        self.question_entry.bind("<Return>", lambda event: self.ask_agent())

        # Ask button and cursor
        self.ask_button = ttk.Button(main_frame, text="Ask Agent", command=self.ask_agent)
        self.ask_button.grid(row=3, column=0, pady=(0, 12), sticky="ew")
        self.root.bind('<KP_Enter>', lambda event: self.ask_agent())

        self.cursor_label = ttk.Label(main_frame, text="", font=("Segoe UI", 12, "bold"), foreground="#0078D7")
        self.cursor_label.grid(row=3, column=1, sticky="w", pady=(0, 12), padx=(10, 0))
        self.cursor_animating = False
        self.cursor_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.cursor_index = 0

        # Response display
        ttk.Label(main_frame, text="Agent Response:").grid(row=4, column=0, sticky="nw", pady=(0, 8))
        self.response_text = scrolledtext.ScrolledText(main_frame, width=60, height=10, state="disabled", font=("Segoe UI", 11))
        self.response_text.grid(row=4, column=1, sticky="w", pady=(0, 8), padx=(10, 0))

        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        self.update_mode()

    def update_mode(self):
        mode = self.mode_var.get()
        if mode == "A2A":
            self.skill_label.grid()
            self.skill_combo.grid()
            self.question_label.grid()
            self.question_entry.grid()
            self.tool_label.grid_remove()
            self.tool_combo.grid_remove()
            self.tool_args_frame.grid_remove()
            self.root.after(100, lambda: self.question_entry.focus_set())
        else:
            self.skill_label.grid_remove()
            self.skill_combo.grid_remove()
            self.question_label.grid_remove()
            self.question_entry.grid_remove()
            self.tool_label.grid(row=1, column=0, sticky="w", pady=(0, 8))
            self.tool_combo.grid(row=1, column=1, sticky="w", pady=(0, 8), padx=(10, 0))
            self.tool_args_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))
            self.update_tool_args()
            self.root.after(100, self.focus_first_tool_arg)
        self.root.update()

    def update_tool_args(self):
        for widget in self.tool_args_frame.winfo_children():
            widget.destroy()
        self.tool_arg_vars = {}
        tool = self.tool_var.get()
        args = MCP_TOOLS.get(tool, [])
        self.tool_combo.bind("<<ComboboxSelected>>", lambda e: self.update_tool_args())
        for i, arg in enumerate(args):
            label = ttk.Label(self.tool_args_frame, text=f"{arg.capitalize()}:")
            label.grid(row=i, column=0, sticky="w", pady=(0, 4))
            var = tk.StringVar()
            entry = ttk.Entry(self.tool_args_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, sticky="w", pady=(0, 4), padx=(10, 0))
            self.tool_arg_vars[arg] = var
            entry.bind("<Return>", lambda event: self.ask_agent())
        self.root.after(100, self.focus_first_tool_arg)

    def focus_first_tool_arg(self):
        entries = [w for w in self.tool_args_frame.winfo_children() if isinstance(w, ttk.Entry)]
        if entries:
            entries[0].focus_set()

    def start_cursor(self):
        self.cursor_animating = True
        self.cursor_index = 0
        self.animate_cursor()

    def animate_cursor(self):
        if self.cursor_animating:
            self.cursor_label.config(text=self.cursor_frames[self.cursor_index])
            self.cursor_index = (self.cursor_index + 1) % len(self.cursor_frames)
            self.root.after(80, self.animate_cursor)
        else:
            self.cursor_label.config(text="")

    def stop_cursor(self):
        self.cursor_animating = False

    def ask_agent(self):
        self.ask_button.state(["disabled"])
        self.start_cursor()
        threading.Thread(target=self._ask_agent, daemon=True).start()

    def _ask_agent(self):
        try:
            mode = self.mode_var.get()
            if mode == "A2A":
                skill = self.skill_var.get()
                question = self.question_entry.get().strip()
                if not question:
                    self.root.after(0, lambda: self.display_response("Please enter a question."))
                    return
                if skill == "triage":
                    params = {"query": question}
                else:
                    params = {"question": question}
                payload = {
                    "jsonrpc": "2.0",
                    "method": skill,
                    "params": params,
                    "id": "1"
                }
                try:
                    response = requests.post(A2A_URL, json=payload, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    if "result" in data:
                        result_val = next(iter(data["result"].values()))
                        self.root.after(0, lambda: self.display_response(result_val))
                    elif "error" in data:
                        self.root.after(0, lambda: self.display_response(f"Error: {data['error']['message']}"))
                    else:
                        self.root.after(0, lambda: self.display_response("Unknown response format."))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.display_response(f"Request failed: {e}"))
            else:
                tool = self.tool_var.get()
                args = {k: v.get().strip() for k, v in self.tool_arg_vars.items()}
                if any(not val for val in args.values()):
                    self.root.after(0, lambda: self.display_response("Please fill in all tool arguments."))
                    return
                payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool,
                        "arguments": args
                    },
                    "id": "1"
                }
                try:
                    headers = {"Accept": "application/json, text/event-stream"}
                    response = requests.post(MCP_URL, json=payload, headers=headers, timeout=10)
                    response.raise_for_status()
                    content_type = response.headers.get("Content-Type", "")
                    if "text/event-stream" in content_type:
                        lines = response.text.splitlines()
                        data_lines = [line[6:] for line in lines if line.startswith("data: ")]
                        if data_lines:
                            try:
                                data = json.loads(data_lines[-1])
                            except Exception as e:
                                self.root.after(0, lambda e=e: self.display_response(f"Failed to parse event-stream data: {e}"))
                                return
                        else:
                            self.root.after(0, lambda: self.display_response("No data received in event stream."))
                            return
                    else:
                        data = response.json()
                    if "result" in data:
                        content = data["result"].get("content")
                        if isinstance(content, list) and content and "text" in content[0]:
                            self.root.after(0, lambda: self.display_response(content[0]["text"]))
                        else:
                            self.root.after(0, lambda: self.display_response(json.dumps(data["result"], indent=2)))
                    elif "error" in data:
                        self.root.after(0, lambda: self.display_response(f"Error: {data['error']['message']}"))
                    else:
                        self.root.after(0, lambda: self.display_response("Unknown response format."))
                except Exception as e:
                    self.root.after(0, lambda e=e: self.display_response(f"Request failed: {e}"))
        finally:
            self.root.after(0, self.ask_button.state, ["!disabled"])
            self.root.after(0, self.stop_cursor)

    def display_response(self, text):
        self.response_text.config(state="normal")
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, text)
        self.response_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = A2AClientGUI(root)
    root.mainloop() 