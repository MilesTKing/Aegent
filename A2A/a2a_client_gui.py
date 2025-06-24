import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading

A2A_URL = "http://localhost:9000/a2a"

class A2AClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("A2A Agent Client")
        self.root.geometry("600x400")
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

        # Skill selection
        ttk.Label(main_frame, text="Select Skill:").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.skill_var = tk.StringVar(value="triage")
        self.skill_combo = ttk.Combobox(main_frame, textvariable=self.skill_var, values=["triage", "math", "history"], state="readonly", width=15)
        self.skill_combo.grid(row=0, column=1, sticky="w", pady=(0, 8), padx=(10, 0))

        # Question entry
        ttk.Label(main_frame, text="Enter your question:").grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.question_entry = ttk.Entry(main_frame, width=50)
        self.question_entry.grid(row=1, column=1, sticky="w", pady=(0, 8), padx=(10, 0))
        self.question_entry.bind("<Return>", lambda event: self.ask_agent())

        # Ask button and cursor
        self.ask_button = ttk.Button(main_frame, text="Ask Agent", command=self.ask_agent)
        self.ask_button.grid(row=2, column=0, pady=(0, 12), sticky="ew")
        self.root.bind('<KP_Enter>', lambda event: self.ask_agent())

        self.cursor_label = ttk.Label(main_frame, text="", font=("Segoe UI", 12, "bold"), foreground="#0078D7")
        self.cursor_label.grid(row=2, column=1, sticky="w", pady=(0, 12), padx=(10, 0))
        self.cursor_animating = False
        self.cursor_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.cursor_index = 0

        # Response display
        ttk.Label(main_frame, text="Agent Response:").grid(row=3, column=0, sticky="nw", pady=(0, 8))
        self.response_text = scrolledtext.ScrolledText(main_frame, width=60, height=10, state="disabled", font=("Segoe UI", 11))
        self.response_text.grid(row=3, column=1, sticky="w", pady=(0, 8), padx=(10, 0))

        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

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
        skill = self.skill_var.get()
        question = self.question_entry.get().strip()
        if not question:
            self.root.after(0, lambda: self.display_response("Please enter a question."))
            self.root.after(0, self.ask_button.state, ["!disabled"])
            self.root.after(0, self.stop_cursor)
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
            self.root.after(0, lambda: self.display_response(f"Request failed: {e}"))
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