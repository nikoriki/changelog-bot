import tkinter as tk
from tkinter import scrolledtext, messagebox
import datetime
import time
import threading
import os
import json
import requests

CONFIG_FILE = "config.json"

class ChangelogBot:
    def __init__(self):
        self.config = self.load_config()
        self.setup_gui()
        
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            default_config = {
                "webhook_url": "",
                "bot_name": "Changelog Bot",
                "bot_avatar": ""
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=4)
            return default_config
        
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    
    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Discord Changelog Bot")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#2C2F33")
        
        main_frame = tk.Frame(self.root, bg="#2C2F33")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        config_frame = tk.LabelFrame(main_frame, text="Bot Configuration", bg="#2C2F33", fg="white")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(config_frame, text="Webhook URL:", bg="#2C2F33", fg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.webhook_entry = tk.Entry(config_frame, width=50)
        self.webhook_entry.grid(row=0, column=1, padx=5, pady=5)
        self.webhook_entry.insert(0, self.config["webhook_url"])
        
        tk.Label(config_frame, text="Bot Name:", bg="#2C2F33", fg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.botname_entry = tk.Entry(config_frame, width=50)
        self.botname_entry.grid(row=1, column=1, padx=5, pady=5)
        self.botname_entry.insert(0, self.config["bot_name"])
        
        tk.Label(config_frame, text="Avatar URL:", bg="#2C2F33", fg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.avatar_entry = tk.Entry(config_frame, width=50)
        self.avatar_entry.grid(row=2, column=1, padx=5, pady=5)
        self.avatar_entry.insert(0, self.config["bot_avatar"])
        
        save_btn = tk.Button(config_frame, text="Save Configuration", command=self.save_bot_config, bg="#7289DA", fg="white")
        save_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        changelog_frame = tk.LabelFrame(main_frame, text="Changelog Message", bg="#2C2F33", fg="white")
        changelog_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        date_frame = tk.Frame(changelog_frame, bg="#2C2F33")
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(date_frame, text="Date:", bg="#2C2F33", fg="white").pack(side=tk.LEFT, padx=5)
        self.date_entry = tk.Entry(date_frame, width=15)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, current_date)
        
        timestamp_btn = tk.Button(date_frame, text="Generate Discord Timestamp", command=self.generate_timestamp, bg="#7289DA", fg="white")
        timestamp_btn.pack(side=tk.LEFT, padx=5)
        
        title_frame = tk.Frame(changelog_frame, bg="#2C2F33")
        title_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(title_frame, text="Title:", bg="#2C2F33", fg="white").pack(side=tk.LEFT, padx=5)
        self.title_entry = tk.Entry(title_frame, width=60)
        self.title_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        content_frame = tk.Frame(changelog_frame, bg="#2C2F33")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(content_frame, text="Changes:", bg="#2C2F33", fg="white").pack(anchor="w", padx=5)
        self.changelog_text = scrolledtext.ScrolledText(content_frame, height=10, width=60)
        self.changelog_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        preview_frame = tk.LabelFrame(main_frame, text="Message Preview", bg="#2C2F33", fg="white")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, width=60, bg="#36393F", fg="white")
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_text.config(state=tk.DISABLED)
        
        button_frame = tk.Frame(main_frame, bg="#2C2F33")
        button_frame.pack(fill=tk.X, pady=10)
        
        preview_btn = tk.Button(button_frame, text="Generate Preview", command=self.update_preview, bg="#7289DA", fg="white")
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        send_btn = tk.Button(button_frame, text="🚀 Push Changelog", command=self.send_changelog, bg="#43B581", fg="white", height=2, width=20)
        send_btn.pack(side=tk.RIGHT, padx=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#23272A", fg="white")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.root.after(100, self.update_preview)

    def generate_timestamp(self):
        try:
            date_str = self.date_entry.get()
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            epoch = int(time.mktime(date_obj.timetuple()))
            
            popup = tk.Toplevel(self.root)
            popup.title("Discord Timestamps")
            popup.geometry("400x300")
            popup.configure(bg="#2C2F33")
            
            tk.Label(popup, text="Discord Timestamp Formats", font=("Arial", 12, "bold"), bg="#2C2F33", fg="white").pack(pady=10)
            
            formats = [
                ("Date", "D", f"<t:{epoch}:D>"),
                ("Short Date", "d", f"<t:{epoch}:d>"),
                ("Long Date with Time", "F", f"<t:{epoch}:F>"),
                ("Short Date with Time", "f", f"<t:{epoch}:f>"),
                ("Time", "t", f"<t:{epoch}:t>"),
                ("Relative Time", "R", f"<t:{epoch}:R>")
            ]
            
            for name, code, format_str in formats:
                frame = tk.Frame(popup, bg="#2C2F33")
                frame.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(frame, text=f"{name} ({code}):", width=15, anchor="w", bg="#2C2F33", fg="white").pack(side=tk.LEFT)
                entry = tk.Entry(frame, width=25)
                entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                entry.insert(0, format_str)
                
                copy_btn = tk.Button(frame, text="Copy", bg="#7289DA", fg="white",
                                    command=lambda f=format_str: self.copy_to_clipboard(popup, f))
                copy_btn.pack(side=tk.RIGHT)
            
            self.status_var.set(f"Generated timestamps for {date_str}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid date format. Please use YYYY-MM-DD.\nError: {str(e)}")
    
    def copy_to_clipboard(self, parent, text):
        parent.clipboard_clear()
        parent.clipboard_append(text)
        self.status_var.set(f"Copied: {text}")
    
    def update_preview(self):
        try:
            date_str = self.date_entry.get()
            title = self.title_entry.get()
            changes = self.changelog_text.get("1.0", tk.END).strip()
            
            embed_preview = f"""
```
📢 **{title}**
📅 {date_str}

{changes}
```
"""
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", embed_preview)
            self.preview_text.config(state=tk.DISABLED)
            
            self.status_var.set("Preview updated")
        except Exception as e:
            self.status_var.set(f"Error generating preview: {str(e)}")
    
    def save_bot_config(self):
        self.config["webhook_url"] = self.webhook_entry.get()
        self.config["bot_name"] = self.botname_entry.get()
        self.config["bot_avatar"] = self.avatar_entry.get()
        self.save_config()
        self.status_var.set("Configuration saved")
        messagebox.showinfo("Success", "Bot configuration saved successfully!")
    
    def send_changelog(self):
        webhook_url = self.config["webhook_url"]
        
        if not webhook_url:
            messagebox.showerror("Configuration Error", "Please set your webhook URL in the configuration!")
            return
        
        title = self.title_entry.get()
        changes = self.changelog_text.get("1.0", tk.END).strip()
        
        if not title or not changes:
            messagebox.showerror("Input Error", "Please provide a title and changelog content!")
            return
        
        threading.Thread(target=self.send_webhook, args=(title, changes), daemon=True).start()
        self.status_var.set("Sending changelog...")
    
    def send_webhook(self, title, changes):
        try:
            payload = {
                "username": self.config["bot_name"],
                "avatar_url": self.config["bot_avatar"] if self.config["bot_avatar"] else None,
                "embeds": [
                    {
                        "title": f"📢 {title}",
                        "description": changes,
                        "color": 7506394,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                ]
            }
            
            if not payload["avatar_url"]:
                del payload["avatar_url"]
            
            response = requests.post(
                self.config["webhook_url"],
                json=payload
            )
            
            if response.status_code == 204:
                self.update_status("Changelog successfully sent!")
            else:
                self.update_status(f"Error: Discord returned status code {response.status_code}")
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ChangelogBot()
    app.run()
