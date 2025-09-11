import tkinter as tk
from tkinter import ttk, messagebox
import time
import os
from pynput import mouse, keyboard

class InactivityShutdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inactivity Shutdown Controller")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Disable close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_attempt)
        
        # Set inactivity thresholds (in seconds)
        self.inactivity_threshold = 60  # 1 minute of no input
        self.shutdown_threshold = 180   # 3 minutes to click the button
        
        # Initialize variables
        self.last_activity_time = time.time()
        self.shutdown_time = None
        self.is_counting = False
        self.running = True
        self.notification_window = None
        
        # Setup GUI
        self.setup_gui()
        
        # Start monitoring input
        self.start_input_monitoring()
        
        # Start the countdown check
        self.check_inactivity()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Inactivity Shutdown Controller", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Instructions
        instructions = (
            "This program will shut down your computer if no mouse or keyboard\n"
            "activity is detected for 1 minute, followed by no button click for 3 minutes.\n"
            "Click the button below to prevent shutdown."
        )
        instr_label = ttk.Label(main_frame, text=instructions, justify=tk.CENTER)
        instr_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Countdown display
        self.countdown_var = tk.StringVar(value="System active")
        self.countdown_label = ttk.Label(main_frame, textvariable=self.countdown_var, 
                                       font=("Arial", 14), foreground="green")
        self.countdown_label.grid(row=2, column=0, columnspan=2, pady=(0, 30))
        
        # Active button
        self.active_button = ttk.Button(main_frame, text="I'm Active!", 
                                       command=self.button_clicked, state=tk.DISABLED)
        self.active_button.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Status label
        self.status_var = tk.StringVar(value="Monitoring for inactivity...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=2)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def start_input_monitoring(self):
        # Start mouse listener
        self.mouse_listener = mouse.Listener(on_move=self.on_activity,
                                            on_click=self.on_activity,
                                            on_scroll=self.on_activity)
        self.mouse_listener.start()
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity,
                                                  on_release=self.on_activity)
        self.keyboard_listener.start()
    
    def on_activity(self, *args):
        self.last_activity_time = time.time()
        if self.is_counting:
            self.reset_countdown()
    
    def button_clicked(self):
        self.reset_countdown()
        self.show_notification("Activity Confirmed", "Shutdown cancelled! Continue working.", "green")
    
    def reset_countdown(self):
        self.is_counting = False
        self.active_button.config(state=tk.DISABLED)
        self.countdown_var.set("System active")
        self.countdown_label.configure(foreground="green")
        self.status_var.set("Monitoring for inactivity...")
        
        # Close notification if open
        if self.notification_window:
            try:
                self.notification_window.destroy()
                self.notification_window = None
            except:
                pass
    
    def calculate_text_dimensions(self, text, font, max_width=400):
        """Calculate the required dimensions for text to fit properly"""
        # Create a temporary label to measure text
        temp_label = tk.Label(self.root, text=text, font=font, wraplength=max_width)
        temp_label.update()
        
        # Get the required width and height
        lines = text.count('\n') + 1
        width = temp_label.winfo_reqwidth() + 40  # Add padding
        height = temp_label.winfo_reqheight() + 80  # Add padding for title and button
        
        # Ensure minimum and maximum sizes
        width = max(300, min(width, 500))
        height = max(100, min(height, 300))
        
        temp_label.destroy()
        return width, height
    
    def show_notification(self, title, message, color="orange"):
        # Close previous notification if exists
        if self.notification_window:
            try:
                self.notification_window.destroy()
            except:
                pass
        
        # Create notification window
        self.notification_window = tk.Toplevel(self.root)
        self.notification_window.overrideredirect(True)  # Remove window decorations
        self.notification_window.attributes('-topmost', True)
        self.notification_window.attributes('-alpha', 0.95)  # Slight transparency
        
        # Calculate optimal size based on message content
        width, height = self.calculate_text_dimensions(message, ("Arial", 10))
        
        # Position in upper right corner
        screen_width = self.notification_window.winfo_screenwidth()
        self.notification_window.geometry(f"{width}x{height}+{screen_width-width-20}+20")
        
        # Style based on color
        if color == "red":
            bg_color = "#ffcccc"
            fg_color = "#990000"
            border_color = "#ff6666"
        elif color == "green":
            bg_color = "#ccffcc"
            fg_color = "#006600"
            border_color = "#66cc66"
        else:  # orange/default
            bg_color = "#fff0cc"
            fg_color = "#cc6600"
            border_color = "#ffcc66"
        
        self.notification_window.configure(bg=border_color)
        
        # Content frame with padding
        content_frame = tk.Frame(self.notification_window, bg=bg_color, padx=10, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Title
        title_label = tk.Label(content_frame, text=title, 
                              font=("Arial", 12, "bold"), fg=fg_color, bg=bg_color)
        title_label.pack(pady=(5, 10), anchor=tk.W)
        
        # Separator
        separator = tk.Frame(content_frame, height=2, bg=border_color)
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Message - with dynamic wrapping
        msg_label = tk.Label(content_frame, text=message, 
                            font=("Arial", 10), fg=fg_color, bg=bg_color,
                            justify=tk.LEFT, wraplength=width-40)
        msg_label.pack(pady=(0, 15), fill=tk.BOTH, expand=True)
        
        # Close button
        close_btn = tk.Button(content_frame, text="OK", 
                             command=self.notification_window.destroy,
                             bg=fg_color, fg="white", relief="flat",
                             font=("Arial", 10, "bold"))
        close_btn.pack(pady=(5, 5))
        
        # Auto-close after 5 seconds
        self.notification_window.after(5000, self.notification_window.destroy)
    
    def check_inactivity(self):
        if not self.running:
            return
            
        current_time = time.time()
        inactivity_period = current_time - self.last_activity_time
        
        if not self.is_counting:
            if inactivity_period >= self.inactivity_threshold:
                self.is_counting = True
                self.shutdown_time = current_time + self.shutdown_threshold
                self.active_button.config(state=tk.NORMAL)
                self.status_var.set("Warning: Inactivity detected! Click the button to prevent shutdown.")
                # Show notification
                self.show_notification("Inactivity Alert", 
                                      "No mouse or keyboard activity detected for 1 minute.\n\n"
                                      "Click the 'I'm Active!' button in the main window to prevent "
                                      "automatic shutdown in 3 minutes.")
        
        if self.is_counting:
            time_remaining = self.shutdown_time - current_time
            if time_remaining <= 0:
                self.shutdown_computer()
            else:
                # Format time as MM:SS
                minutes, seconds = divmod(int(time_remaining), 60)
                self.countdown_var.set(f"Time until shutdown: {minutes:02d}:{seconds:02d}")
                self.countdown_label.configure(foreground="red")
                
                # Show urgent notification when less than 30 seconds remain
                if time_remaining < 30 and int(time_remaining) % 5 == 0:
                    self.show_notification("URGENT: Shutdown Imminent", 
                                         f"Only {int(time_remaining)} seconds until shutdown!\n\n"
                                         "Click the 'I'm Active!' button immediately to cancel.", "red")
        
        # Check again after 1 second
        self.root.after(1000, self.check_inactivity)
    
    def shutdown_computer(self):
        self.running = False
        # Show final warning
        self.show_notification("SYSTEM SHUTDOWN", 
                              "Computer is shutting down now due to inactivity.\n\n"
                              "All unsaved work will be lost.", "red")
        self.root.update()
        time.sleep(2)  # Brief delay to show the message
        self.root.destroy()
        os.system("shutdown /s /t 1" if os.name == 'nt' else "shutdown -h now")
    
    def on_close_attempt(self):
        # Show message that the program cannot be closed normally
        messagebox.showwarning("Cannot Close", 
                              "This program is designed to prevent accidental shutdowns.\n"
                              "It cannot be closed through the window controls.\n\n"
                              "To terminate the program, you need to use Task Manager\n"
                              "or force quit through your system's process manager.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InactivityShutdownApp(root)
    root.mainloop()
