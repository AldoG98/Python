import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
from mutagen.mp3 import MP3

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Music Player")
        self.root.geometry("400x300")
        self.root.configure(bg="#f0f0f0")

        # Initialize pygame mixer
        pygame.mixer.init()

        # Create playlist
        self.playlist = []
        self.current_track = 0
        self.paused = False
        self.current_time = 0

        self.create_gui()

    def create_gui(self):
        # Music control buttons
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(pady=20)

        ttk.Button(controls_frame, text="⏮", command=self.prev_track).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="▶", command=self.play_music).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="⏸", command=self.pause_music).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="⏭", command=self.next_track).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="⏹", command=self.stop_music).pack(side=tk.LEFT, padx=5)

        # Volume slider
        self.volume_var = tk.DoubleVar(value=70)
        volume_frame = ttk.Frame(self.root)
        volume_frame.pack(pady=10)
        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT)
        volume_slider = ttk.Scale(volume_frame, from_=0, to=100, orient="horizontal",
                                variable=self.volume_var, command=self.set_volume)
        volume_slider.pack(side=tk.LEFT, padx=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var,
                                          maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=20, pady=10)

        # Time labels
        time_frame = ttk.Frame(self.root)
        time_frame.pack()
        self.current_time_label = ttk.Label(time_frame, text="0:00")
        self.current_time_label.pack(side=tk.LEFT, padx=10)
        self.total_time_label = ttk.Label(time_frame, text="0:00")
        self.total_time_label.pack(side=tk.LEFT, padx=10)

        # Playlist box
        self.playlist_box = tk.Listbox(self.root, width=45, height=5)
        self.playlist_box.pack(pady=10)

        # Add music button
        ttk.Button(self.root, text="Add Music", command=self.add_music).pack(pady=5)

        # Initialize volume
        self.set_volume(70)

        # Update timer
        self.root.after(1000, self.update_progress)

    def add_music(self):
        files = filedialog.askopenfilenames(
            filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")])
        for file in files:
            self.playlist.append(file)
            self.playlist_box.insert(tk.END, os.path.basename(file))

    def play_music(self):
        if not self.playlist:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            return

        try:
            pygame.mixer.music.load(self.playlist[self.current_track])
            pygame.mixer.music.play()
            self.update_time_label()
        except pygame.error:
            self.next_track()

    def pause_music(self):
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop_music(self):
        pygame.mixer.music.stop()
        self.progress_var.set(0)
        self.current_time_label.config(text="0:00")

    def next_track(self):
        if self.playlist:
            self.current_track = (self.current_track + 1) % len(self.playlist)
            self.play_music()

    def prev_track(self):
        if self.playlist:
            self.current_track = (self.current_track - 1) % len(self.playlist)
            self.play_music()

    def set_volume(self, val):
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)

    def update_progress(self):
        if pygame.mixer.music.get_busy() and not self.paused:
            current_time = pygame.mixer.music.get_pos() / 1000
            try:
                audio = MP3(self.playlist[self.current_track])
                total_length = audio.info.length
                progress = (current_time / total_length) * 100
                self.progress_var.set(progress)
                
                # Update time labels
                current_mins, current_secs = divmod(int(current_time), 60)
                total_mins, total_secs = divmod(int(total_length), 60)
                self.current_time_label.config(
                    text=f"{current_mins}:{str(current_secs).zfill(2)}")
                self.total_time_label.config(
                    text=f"{total_mins}:{str(total_secs).zfill(2)}")
            except:
                pass
        
        self.root.after(1000, self.update_progress)

    def update_time_label(self):
        try:
            audio = MP3(self.playlist[self.current_track])
            total_length = audio.info.length
            mins, secs = divmod(int(total_length), 60)
            self.total_time_label.config(text=f"{mins}:{str(secs).zfill(2)}")
        except:
            self.total_time_label.config(text="0:00")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()