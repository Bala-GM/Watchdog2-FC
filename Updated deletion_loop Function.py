import time
import os

def deletion_loop(self):
    while self.is_running:
        path = self.path_var.get()
        delay = int(self.delay_var.get())
        now = time.time()

        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)  # last modified time
                    if file_age >= delay:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        time.sleep(delay)
