"""
Citizen Compass — Ask Overlay (Windows desktop app)

Runs quietly in the background (system tray icon, no console window).
Press a global hotkey (default: Ctrl+Shift+Space) from anywhere on your
desktop -- even while working in another program -- and a small
always-on-top window pops up near the top of the screen. Type a
question, press Enter, and the answer appears in the same window a
moment later.

Under the hood this just calls ask_engine.ask_question() -- all the
actual "search local files first, fall back to web, ask qwen3:14b"
logic lives there and is unit-testable on its own (see ask_engine.py's
__main__ block). This file is ONLY the GUI shell + hotkey registration.

SETUP:
    pip install keyboard pystray pillow

    (tkinter, used for the popup window itself, ships with standard
    Python on Windows -- nothing extra to install for that part)

RUN:
    pythonw.exe overlay_app.py

    Use pythonw.exe (not python.exe) so no console window appears.
    Add this to Task Scheduler the same way inbox_watcher.py was set
    up, if you want it running automatically at login too.

NOTE on the 'keyboard' library and admin rights: registering a truly
global hotkey on Windows sometimes requires running as Administrator,
especially if the window you're typing into (e.g. a game, or an app
run as admin) has higher privileges than this script. If the hotkey
doesn't fire while a particular window is focused, try running this
script as Administrator.
"""

import queue
import threading
import tkinter as tk
from tkinter import scrolledtext

import keyboard  # pip install keyboard

import ask_engine

HOTKEY = "ctrl+shift+space"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 220

# Thread-safe handoff: the hotkey listener runs on a background thread,
# tkinter must only be touched from the main thread. This queue is how
# "please show the window now" gets passed across safely.
show_requests = queue.Queue()


class AskOverlay:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # start hidden
        self.root.title("Citizen Compass — Ask")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # no title bar, cleaner popup look
        self._build_ui()
        self._center_near_top()
        self.root.bind("<Escape>", lambda e: self.hide())

    def _build_ui(self):
        frame = tk.Frame(self.root, bg="#1e1e1e", bd=2, relief="solid")
        frame.pack(fill="both", expand=True)

        self.entry = tk.Entry(frame, font=("Segoe UI", 14), bg="#2d2d2d",
                               fg="white", insertbackground="white",
                               relief="flat")
        self.entry.pack(fill="x", padx=10, pady=10, ipady=6)
        self.entry.bind("<Return>", self._on_submit)

        self.status_label = tk.Label(frame, text="", font=("Segoe UI", 9),
                                      bg="#1e1e1e", fg="#888888", anchor="w")
        self.status_label.pack(fill="x", padx=10)

        self.answer_box = scrolledtext.ScrolledText(
            frame, font=("Segoe UI", 11), bg="#252525", fg="#dddddd",
            wrap="word", height=6, relief="flat",
        )
        self.answer_box.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.answer_box.configure(state="disabled")

    def _center_near_top(self):
        screen_w = self.root.winfo_screenwidth()
        x = (screen_w - WINDOW_WIDTH) // 2
        y = 100  # near top of screen, not dead center
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.entry.focus_force()

    def hide(self):
        self.root.withdraw()

    def _on_submit(self, event):
        question = self.entry.get().strip()
        if not question:
            return
        self.entry.delete(0, tk.END)
        self._set_status("Thinking...")
        self._set_answer("")

        # Run the actual search+ask in a background thread so the UI
        # doesn't freeze while waiting on Ollama / web search.
        threading.Thread(target=self._run_query, args=(question,), daemon=True).start()

    def _run_query(self, question):
        result = ask_engine.ask_question(question)
        # Hand the result back to the main thread via the same queue
        # mechanism used for hotkey show-requests, so tkinter is only
        # ever touched from the main thread.
        show_requests.put(("answer", result))

    def _set_status(self, text):
        self.status_label.config(text=text)

    def _set_answer(self, text):
        self.answer_box.configure(state="normal")
        self.answer_box.delete("1.0", tk.END)
        self.answer_box.insert(tk.END, text)
        self.answer_box.configure(state="disabled")

    def display_result(self, result):
        source_label = {"local": "your files", "web": "the web", "none": "nowhere"}
        self._set_status(f"Source: {source_label.get(result['source'], result['source'])} — {result['detail']}")
        self._set_answer(result["answer"])


def hotkey_listener_thread():
    """Runs on a background thread for the lifetime of the app. Registers
    the global hotkey and, whenever it fires, just drops a 'please show'
    message onto the queue -- it never touches tkinter directly."""
    keyboard.add_hotkey(HOTKEY, lambda: show_requests.put(("show", None)))
    keyboard.wait()  # blocks this thread forever, listening for hotkeys


def poll_queue(root, overlay):
    """Runs on the main thread via tkinter's own event loop (root.after).
    This is the ONLY place that reacts to hotkey/answer events and touches
    the GUI -- keeps all tkinter calls on the main thread, which tkinter
    requires."""
    try:
        while True:
            kind, payload = show_requests.get_nowait()
            if kind == "show":
                overlay.show()
            elif kind == "answer":
                overlay.display_result(payload)
    except queue.Empty:
        pass
    root.after(100, poll_queue, root, overlay)


def main():
    root = tk.Tk()
    overlay = AskOverlay(root)

    listener = threading.Thread(target=hotkey_listener_thread, daemon=True)
    listener.start()

    root.after(100, poll_queue, root, overlay)
    root.mainloop()


if __name__ == "__main__":
    main()
