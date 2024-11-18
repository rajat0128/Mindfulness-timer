import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import pandas
import random
import textwrap
import pygame


class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Mindfulness and focus timer")
        self.master.configure(bg="#f7f5dd")
        self.master.geometry("500x700")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        pygame.mixer.init()
        self.df = pandas.read_excel("C:/Users/rajat/Downloads/Python project/Python project/Motivational Quotes Database.xlsx")
        self.shown_before = []
        self.timer_type = "Work"
        self.timer_running = False
        self.timer_paused = False
        self.timer_after_id = None
        self.work_max_minutes = 25
        self.break_max_minutes = 5
        self.minutes = self.work_max_minutes
        self.seconds = 0
        self.time_left = self.minutes * 60
        self.sound_enabled = True
        self.main_frame = tk.Frame(self.master, bg="#f7f5dd")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.motivation_label = tk.Label(self.main_frame, font=("Arial", 12, "italic"), bg="#f7f5dd", fg="#333", wraplength=400)
        self.motivation_label.grid(column=0, row=0, columnspan=3, pady=10)
        self.change_quote()
        self.timer_type_label = tk.Label(self.main_frame, text=self.timer_type, font=("Arial", 16, "bold"), bg="#f7f5dd", fg="#333")
        self.timer_type_label.grid(column=1, row=1)
        self.frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(Image.open("C:/Users/rajat/Downloads/Python project/Python project/images/200.gif"))]
        self.frame_index = 0
        self.tomato_label = tk.Label(self.main_frame, bg="#f7f5dd")
        self.tomato_label.grid(column=0, row=2, columnspan=3, pady=10)
        self.animate_tomato()
        self.timer_label = tk.Label(self.main_frame, text=f"{self.minutes:02d}:{self.seconds:02d}", font=("Arial", 24), bg="#f7f5dd", fg="#333")
        self.timer_label.grid(column=0, row=3, columnspan=3)
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", length=300)
        self.progress.grid(column=0, row=4, columnspan=3, pady=10, sticky="ew")
        self.progress["maximum"] = self.work_max_minutes * 60
        self.start_button = tk.Button(self.main_frame, text="Start", bg="#5a9", fg="white", font=("Arial", 12, "bold"), command=self.start_timer)
        self.start_button.grid(column=0, row=5, pady=10)
        self.stop_button = tk.Button(self.main_frame, text="Stop", bg="#c00", fg="white", font=("Arial", 12, "bold"), command=self.stop_timer)
        self.stop_button.grid(column=2, row=5, pady=10)
        self.switch_mode_button = tk.Button(self.main_frame, text="Switch Mode", bg="#036", fg="white", font=("Arial", 12, "bold"), command=self.switch_mode)
        self.switch_mode_button.grid(column=1, row=5, pady=10)
        self.timer_entry_label = tk.Label(self.main_frame, text="Set Timer (mm:ss):", bg="#f7f5dd", fg="#333", font=("Arial", 10))
        self.timer_entry_label.grid(column=0, row=6, columnspan=3)
        self.timer_entry = tk.Entry(self.main_frame)
        self.timer_entry.grid(column=0, row=7, columnspan=2, padx=10, sticky="ew")
        self.set_timer_button = tk.Button(self.main_frame, text="Set Timer", bg="#036", fg="white", font=("Arial", 10), command=self.set_timer)
        self.set_timer_button.grid(column=2, row=7)
        self.mute_button = tk.Button(self.main_frame, text="🔇 Mute", bg="#5a9", fg="white", font=("Arial", 10), command=self.toggle_sound)
        self.mute_button.grid(column=1, row=8)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def animate_tomato(self):
        frame = self.frames[self.frame_index]
        self.tomato_label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.master.after(100, self.animate_tomato)

    def change_quote(self):
        rand_num = random.randint(0, len(self.df) - 1)
        if rand_num in self.shown_before:
            self.change_quote()
        else:
            self.shown_before.append(rand_num)
            quote, author, _ = self.df.iloc[rand_num]
            full_text = f"{quote.strip('.')} - {author}"
            self.motivation_label.config(text=textwrap.fill(full_text, width=50))

    def play_sound(self, sound_path):
        if self.sound_enabled:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play(-1)

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            pygame.mixer.music.stop()
            self.mute_button.config(text="🔊 Unmute")
        else:
            if self.timer_type == "Work":
                self.play_sound("C:/Users/rajat/Downloads/Python project/Python project/sounds/work_bell.wav")
            else:
                self.play_sound("C:/Users/rajat/Downloads/Python project/Python project/sounds/minsfulness timer.mp3")
            self.mute_button.config(text="🔇 Mute")

    def set_timer(self):
        try:
            timer_input = self.timer_entry.get()
            minutes, seconds = map(int, timer_input.split(":"))
            if 0 <= minutes <= 60 and 0 <= seconds <= 59:
                self.work_max_minutes = minutes
                self.minutes = minutes
                self.seconds = seconds
                self.time_left = minutes * 60 + seconds
                self.timer_label.config(text=f"{self.minutes:02d}:{self.seconds:02d}")
                self.progress["maximum"] = self.time_left
            else:
                messagebox.showerror("Error", "Invalid time range!")
        except ValueError:
            messagebox.showerror("Error", "Invalid format! Use mm:ss.")

    def start_timer(self):
        if self.timer_type == "Work":
            pygame.mixer.music.stop()
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_after_id:
            self.master.after_cancel(self.timer_after_id)

    def update_timer(self):
        if self.timer_running and self.time_left > 0:
            self.minutes = self.time_left // 60
            self.seconds = self.time_left % 60
            self.timer_label.config(text=f"{self.minutes:02d}:{self.seconds:02d}")
            self.progress["value"] = (self.work_max_minutes * 60 - self.time_left) if self.timer_type == "Work" else (self.break_max_minutes * 60 - self.time_left)
            self.time_left -= 1
            self.timer_after_id = self.master.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.timer_running = False
            self.switch_mode()


    def switch_mode(self):
        if self.timer_type == "Work":
            self.timer_type = "Break"
            self.time_left = self.break_max_minutes * 60
            self.play_sound("C:/Users/rajat/Downloads/Python project/Python project/minsfulness timer.mp3")
        else:
            self.timer_type = "Work"
            self.time_left = self.work_max_minutes * 60
            self.play_sound("C:/Users/rajat/Downloads/Python project/Python project/sounds/work_bell.wav")
        self.timer_type_label.config(text=self.timer_type)
        self.change_quote()
        self.timer_label.config(text=f"{self.time_left // 60:02d}:{self.time_left % 60:02d}")
        self.timer_running = False 


    def on_closing(self):
        if self.timer_after_id:
            self.master.after_cancel(self.timer_after_id)
        pygame.mixer.music.stop()
        self.master.destroy()


root = tk.Tk()
app = TimerApp(root)
root.mainloop()
