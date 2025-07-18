import os
import time
import json
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image
import pystray

CONFIG_FILE = "config.json"
VALID_USERNAME = "admin"
VALID_PASSWORD = "1@43"

class FileCleanerApp:
    def __init__(self, root):
        self.root = root
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.delay_var = tk.StringVar()

        self.is_running = False
        self.tray_icon = None
        self.thread = None

        self.load_config()
        self.build_login_ui()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.path_var.set(data.get("path", ""))
                self.delay_var.set(str(data.get("delay", "10")))

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "path": self.path_var.get(),
                "delay": int(self.delay_var.get())
            }, f)

    def build_login_ui(self):
        self.root.title("Login")
        self.root.geometry("300x180")
        self.root.resizable(False, False)

        tk.Label(self.root, text="Username").pack(pady=5)
        tk.Entry(self.root, textvariable=self.username_var).pack()
        tk.Label(self.root, text="Password").pack(pady=5)
        tk.Entry(self.root, textvariable=self.password_var, show="*").pack()
        tk.Button(self.root, text="Login", command=self.login).pack(pady=15)

    def login(self):
        if self.username_var.get() == VALID_USERNAME and self.password_var.get() == VALID_PASSWORD:
            self.root.withdraw()
            self.open_main_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_main_window(self):
        self.main_window = tk.Toplevel()
        self.main_window.title("File Cleaner")
        self.main_window.geometry("400x250")
        self.main_window.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        tk.Label(self.main_window, text="Folder Path").pack(pady=5)
        tk.Entry(self.main_window, textvariable=self.path_var, width=40, state="readonly").pack()
        tk.Button(self.main_window, text="Change Path", command=self.protected_browse).pack(pady=5)

        tk.Label(self.main_window, text="Repeat Delay (seconds)").pack(pady=5)
        tk.Entry(self.main_window, textvariable=self.delay_var).pack()

        tk.Button(self.main_window, text="Start Deletion", command=self.start_loop).pack(pady=10)
        tk.Button(self.main_window, text="Stop Deletion", command=self.stop_loop).pack()

    def protected_browse(self):
        pwd = simpledialog.askstring("Password Required", "Enter password to change path:", show='*')
        if pwd == VALID_PASSWORD:
            folder = filedialog.askdirectory()
            if folder:
                self.path_var.set(folder)
                self.save_config()
        else:
            messagebox.showerror("Access Denied", "Incorrect password")

    def start_loop(self):
        try:
            delay = int(self.delay_var.get())
            path = self.path_var.get()

            if not os.path.isdir(path):
                messagebox.showerror("Error", "Invalid folder path.")
                return

            self.save_config()
            self.is_running = True
            if self.thread is None or not self.thread.is_alive():
                self.thread = threading.Thread(target=self.deletion_loop, daemon=True)
                self.thread.start()
            messagebox.showinfo("Started", f"File deletion will repeat every {delay} seconds.")
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number for delay.")

    def stop_loop(self):
        self.is_running = False
        messagebox.showinfo("Stopped", "File deletion stopped.")

    def deletion_loop(self):
        while self.is_running:
            path = self.path_var.get()
            delay = int(self.delay_var.get())
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            time.sleep(delay)

    def minimize_to_tray(self):
        self.main_window.withdraw()
        image = Image.new("RGB", (64, 64), color=(100, 100, 100))

        def show_window(icon, item):
            self.main_window.deiconify()
            icon.stop()

        def tray_start(icon, item):
            self.start_loop()

        def tray_stop(icon, item):
            self.stop_loop()

        def exit_app(icon, item):
            self.is_running = False
            icon.stop()
            self.root.quit()

        menu = pystray.Menu(
            pystray.MenuItem("Show", show_window),
            pystray.MenuItem("Start", tray_start),
            pystray.MenuItem("Stop", tray_stop),
            pystray.MenuItem("Exit", exit_app)
        )

        self.tray_icon = pystray.Icon("FileCleaner", image, "File Cleaner", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()


# ------------------ Start ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FileCleanerApp(root)
    root.mainloop()

#pyinstaller --noconsole --onefile --icon=Watchdog.ico --name "File Cleaner" "Watchdog2.py"