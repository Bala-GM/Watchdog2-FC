import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image
import pystray

# ------------------ Login Credentials ------------------
VALID_USERNAME = "admin"
VALID_PASSWORD = "1234"

# ------------------ Main Application Class ------------------
class FileCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x180")
        self.root.resizable(False, False)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(root, text="Username").pack(pady=5)
        tk.Entry(root, textvariable=self.username_var).pack()

        tk.Label(root, text="Password").pack(pady=5)
        tk.Entry(root, textvariable=self.password_var, show="*").pack()

        tk.Button(root, text="Login", command=self.login).pack(pady=15)

    def login(self):
        if self.username_var.get() == VALID_USERNAME and self.password_var.get() == VALID_PASSWORD:
            self.root.withdraw()  # Hide login window
            self.open_main_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_main_window(self):
        self.main_window = tk.Toplevel()
        self.main_window.title("File Cleaner")
        self.main_window.geometry("400x250")

        self.path_var = tk.StringVar()
        self.delay_var = tk.StringVar()

        tk.Label(self.main_window, text="Folder Path").pack(pady=5)
        path_entry = tk.Entry(self.main_window, textvariable=self.path_var, width=40)
        path_entry.pack()
        tk.Button(self.main_window, text="Browse", command=self.browse_folder).pack(pady=5)

        tk.Label(self.main_window, text="Delay (seconds)").pack(pady=5)
        tk.Entry(self.main_window, textvariable=self.delay_var).pack()

        tk.Button(self.main_window, text="Start Deletion", command=self.start_deletion).pack(pady=10)

        self.main_window.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def start_deletion(self):
        path = self.path_var.get()
        try:
            delay = int(self.delay_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid delay in seconds.")
            return

        if not os.path.isdir(path):
            messagebox.showerror("Error", "Invalid folder path.")
            return

        threading.Thread(target=self.delete_files_after_delay, args=(path, delay), daemon=True).start()
        messagebox.showinfo("Started", f"Files will be deleted after {delay} seconds.")

    def delete_files_after_delay(self, path, delay):
        time.sleep(delay)
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

    def minimize_to_tray(self):
        self.main_window.withdraw()
        image = Image.new("RGB", (64, 64), color=(100, 100, 100))  # Simple icon

        def restore_window(icon, item):
            self.main_window.deiconify()
            icon.stop()

        def quit_app(icon, item):
            icon.stop()
            self.root.destroy()

        menu = pystray.Menu(
            pystray.MenuItem("Restore", restore_window),
            pystray.MenuItem("Exit", quit_app),
        )
        self.tray_icon = pystray.Icon("FileCleaner", image, "File Cleaner", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()


# ------------------ Run Application ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FileCleanerApp(root)
    root.mainloop()
