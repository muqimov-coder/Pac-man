"""
Video Player Pro - Zamonaviy Media Player
Python 3.12+ va Tkinter yordamida yaratilgan professional video player

Kerakli kutubxonalar:
pip install opencv-python pillow numpy
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

# Video o'ynatish uchun kerakli kutubxonalar
try:
    import cv2
    from PIL import Image, ImageTk
    import numpy as np
except ImportError:
    print("Kerakli kutubxonalar yuklanmagan. Iltimos quyidagilarni o'rnating:")
    print("pip install opencv-python pillow numpy")
    sys.exit(1)


class ThemeType(Enum):
    """Mavzu turlari"""
    DARK = "dark"
    LIGHT = "light"
    MIDNIGHT = "midnight"


@dataclass
class ThemeColors:
    """Mavzu ranglari ma'lumotlar sinfi"""
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    text_primary: str
    text_secondary: str
    accent: str
    accent_hover: str
    progress_bg: str
    progress_fill: str
    button_bg: str
    button_hover: str
    playlist_bg: str
    playlist_selected: str
    slider_bg: str
    slider_fill: str


class ThemeManager:
    """Mavzu boshqaruvchisi"""

    THEMES = {
        ThemeType.DARK: ThemeColors(
            bg_primary="#1a1a2e",
            bg_secondary="#16213e",
            bg_tertiary="#0f3460",
            text_primary="#e0e0e0",
            text_secondary="#a0a0a0",
            accent="#e94560",
            accent_hover="#ff6b6b",
            progress_bg="#2a2a4a",
            progress_fill="#e94560",
            button_bg="#0f3460",
            button_hover="#1a5276",
            playlist_bg="#16213e",
            playlist_selected="#0f3460",
            slider_bg="#2a2a4a",
            slider_fill="#e94560"
        ),
        ThemeType.LIGHT: ThemeColors(
            bg_primary="#f5f5f5",
            bg_secondary="#ffffff",
            bg_tertiary="#e0e0e0",
            text_primary="#333333",
            text_secondary="#666666",
            accent="#2196f3",
            accent_hover="#1976d2",
            progress_bg="#e0e0e0",
            progress_fill="#2196f3",
            button_bg="#e3f2fd",
            button_hover="#bbdefb",
            playlist_bg="#ffffff",
            playlist_selected="#e3f2fd",
            slider_bg="#e0e0e0",
            slider_fill="#2196f3"
        ),
        ThemeType.MIDNIGHT: ThemeColors(
            bg_primary="#0d0d0d",
            bg_secondary="#1a1a1a",
            bg_tertiary="#2d2d2d",
            text_primary="#00ff00",
            text_secondary="#00cc00",
            accent="#00ff00",
            accent_hover="#33ff33",
            progress_bg="#2d2d2d",
            progress_fill="#00ff00",
            button_bg="#2d2d2d",
            button_hover="#404040",
            playlist_bg="#1a1a1a",
            playlist_selected="#2d2d2d",
            slider_bg="#2d2d2d",
            slider_fill="#00ff00"
        )
    }


class VideoPlayer:
    """Asosiy Video Player klassi"""

    def __init__(self, root: tk.Tk):
        """Video Player konstruktori"""
        self.root = root
        self.root.title("Video Player Pro")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)

        # O'zgaruvchilar
        self.current_theme = ThemeType.DARK
        self.theme = ThemeManager.THEMES[self.current_theme]
        self.current_video_path = None
        self.playlist = []
        self.current_playlist_index = -1
        self.is_playing = False
        self.is_muted = False
        self.volume = 0.7
        self.previous_volume = 0.7
        self.video_duration = 0
        self.current_time = 0
        self.playback_speed = 1.0
        self.is_fullscreen = False
        self.last_frame = None

        # Threading
        self.play_thread = None
        self.stop_playback = False
        self.playback_lock = threading.Lock()

        # Video capture
        self.cap = None

        # GUI elementlarini yaratish
        self._setup_ui()
        self._setup_bindings()

        # Oyna yopilganda
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        """Asosiy UI elementlarini yaratish"""
        self.main_container = tk.Frame(self.root, bg=self.theme.bg_primary)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self._create_top_panel()
        self._create_main_content()
        self._create_progress_bar()
        self._create_bottom_panel()

    def _create_top_panel(self):
        """Yuqori panel"""
        self.top_panel = tk.Frame(self.main_container, bg=self.theme.bg_secondary, height=45)
        self.top_panel.pack(fill=tk.X, side=tk.TOP)
        self.top_panel.pack_propagate(False)

        # Chap tugmalar
        left_frame = tk.Frame(self.top_panel, bg=self.theme.bg_secondary)
        left_frame.pack(side=tk.LEFT, padx=5)

        self.btn_open = tk.Button(left_frame, text="📂 Fayl ochish", command=self.open_file,
                                  bg=self.theme.button_bg, fg=self.theme.text_primary,
                                  relief=tk.FLAT, cursor="hand2", font=("Arial", 10))
        self.btn_open.pack(side=tk.LEFT, padx=2, pady=8)

        self.btn_add = tk.Button(left_frame, text="📋 Pleylist qo'shish", command=self.add_to_playlist,
                                 bg=self.theme.button_bg, fg=self.theme.text_primary,
                                 relief=tk.FLAT, cursor="hand2", font=("Arial", 10))
        self.btn_add.pack(side=tk.LEFT, padx=2, pady=8)

        # Sarlavha
        self.title_label = tk.Label(self.top_panel, text="Video Player Pro",
                                    bg=self.theme.bg_secondary, fg=self.theme.accent,
                                    font=("Arial", 14, "bold"))
        self.title_label.pack(side=tk.LEFT, expand=True)

        # O'ng tugmalar
        right_frame = tk.Frame(self.top_panel, bg=self.theme.bg_secondary)
        right_frame.pack(side=tk.RIGHT, padx=5)

        # Mavzu tugmalari
        themes_frame = tk.Frame(right_frame, bg=self.theme.bg_secondary)
        themes_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(themes_frame, text="Mavzu:", bg=self.theme.bg_secondary,
                 fg=self.theme.text_secondary, font=("Arial", 9)).pack(side=tk.LEFT, padx=2)

        for theme_type in ThemeType:
            btn = tk.Button(themes_frame, text=theme_type.value.capitalize(),
                            command=lambda t=theme_type: self.change_theme(t),
                            bg=self.theme.button_bg, fg=self.theme.text_primary,
                            relief=tk.FLAT, cursor="hand2", font=("Arial", 9), width=8)
            btn.pack(side=tk.LEFT, padx=2)

        # Fullscreen
        self.btn_fullscreen = tk.Button(right_frame, text="⛶", command=self.toggle_fullscreen,
                                        bg=self.theme.button_bg, fg=self.theme.text_primary,
                                        relief=tk.FLAT, cursor="hand2", font=("Arial", 14), width=2)
        self.btn_fullscreen.pack(side=tk.LEFT, padx=5)

    def _create_main_content(self):
        """Asosiy kontent"""
        self.content_frame = tk.Frame(self.main_container, bg=self.theme.bg_primary)
        self.content_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.paned_window = tk.PanedWindow(self.content_frame, bg=self.theme.bg_primary,
                                           sashwidth=3, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Video frame
        self.video_frame = tk.Frame(self.paned_window, bg="black")
        self.paned_window.add(self.video_frame, stretch="always")

        self.video_canvas = tk.Canvas(self.video_frame, bg="black", highlightthickness=0)
        self.video_canvas.pack(fill=tk.BOTH, expand=True)

        # Pleylist frame
        self.playlist_frame = tk.Frame(self.paned_window, bg=self.theme.playlist_bg, width=250)
        self.paned_window.add(self.playlist_frame, stretch="never")

        playlist_header = tk.Frame(self.playlist_frame, bg=self.theme.bg_secondary, height=35)
        playlist_header.pack(fill=tk.X)
        playlist_header.pack_propagate(False)

        tk.Label(playlist_header, text="📋 Pleylist", bg=self.theme.bg_secondary,
                 fg=self.theme.text_primary, font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)

        tk.Button(playlist_header, text="🗑️ Tozalash", command=self.clear_playlist,
                  bg=self.theme.bg_secondary, fg=self.theme.text_primary,
                  relief=tk.FLAT, cursor="hand2", font=("Arial", 9)).pack(side=tk.RIGHT, padx=5)

        listbox_frame = tk.Frame(self.playlist_frame, bg=self.theme.playlist_bg)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.playlist_listbox = tk.Listbox(listbox_frame, bg=self.theme.playlist_bg,
                                           fg=self.theme.text_primary,
                                           selectbackground=self.theme.playlist_selected,
                                           selectforeground=self.theme.text_primary,
                                           font=("Arial", 10), relief=tk.FLAT,
                                           borderwidth=0, highlightthickness=0)
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.playlist_listbox.yview)

        self.playlist_listbox.bind('<<ListboxSelect>>', self._on_playlist_select)

    def _create_progress_bar(self):
        """Progress bar"""
        self.progress_frame = tk.Frame(self.main_container, bg=self.theme.progress_bg, height=6)
        self.progress_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.progress_canvas = tk.Canvas(self.progress_frame, bg=self.theme.progress_bg,
                                         height=6, highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X, expand=True)

        self.progress_canvas.bind('<Button-1>', self._on_progress_click)
        self.progress_canvas.bind('<B1-Motion>', self._on_progress_drag)

    def _create_bottom_panel(self):
        """Pastki panel"""
        self.bottom_panel = tk.Frame(self.main_container, bg=self.theme.bg_secondary, height=80)
        self.bottom_panel.pack(fill=tk.X, side=tk.BOTTOM)
        self.bottom_panel.pack_propagate(False)

        # Chap - ma'lumot
        info_frame = tk.Frame(self.bottom_panel, bg=self.theme.bg_secondary)
        info_frame.pack(side=tk.LEFT, padx=15, pady=8)

        self.file_name_label = tk.Label(info_frame, text="Fayl tanlanmagan",
                                        bg=self.theme.bg_secondary, fg=self.theme.text_primary,
                                        font=("Arial", 10, "bold"), anchor=tk.W, wraplength=300)
        self.file_name_label.pack(fill=tk.X)

        self.time_label = tk.Label(info_frame, text="00:00 / 00:00",
                                   bg=self.theme.bg_secondary, fg=self.theme.text_secondary,
                                   font=("Arial", 9))
        self.time_label.pack(fill=tk.X)

        # O'rta - boshqaruv
        control_frame = tk.Frame(self.bottom_panel, bg=self.theme.bg_secondary)
        control_frame.pack(side=tk.LEFT, expand=True, pady=8)

        btn_cfg = {'bg': self.theme.button_bg, 'fg': self.theme.text_primary,
                   'relief': tk.FLAT, 'cursor': 'hand2', 'font': ('Arial', 14), 'width': 3}

        self.btn_previous = tk.Button(control_frame, text="⏮", command=self.play_previous, **btn_cfg)
        self.btn_previous.pack(side=tk.LEFT, padx=3)

        self.btn_rewind = tk.Button(control_frame, text="⏪",
                                    command=lambda: self.seek_relative(-10), **btn_cfg)
        self.btn_rewind.pack(side=tk.LEFT, padx=3)

        self.btn_play = tk.Button(control_frame, text="▶", command=self.toggle_play,
                                  font=('Arial', 16), width=4, bg=self.theme.accent,
                                  fg='white', relief=tk.FLAT, cursor='hand2')
        self.btn_play.pack(side=tk.LEFT, padx=3)

        self.btn_stop = tk.Button(control_frame, text="⏹", command=self.stop, **btn_cfg)
        self.btn_stop.pack(side=tk.LEFT, padx=3)

        self.btn_forward = tk.Button(control_frame, text="⏩",
                                     command=lambda: self.seek_relative(10), **btn_cfg)
        self.btn_forward.pack(side=tk.LEFT, padx=3)

        self.btn_next = tk.Button(control_frame, text="⏭", command=self.play_next, **btn_cfg)
        self.btn_next.pack(side=tk.LEFT, padx=3)

        # O'ng - ovoz
        volume_frame = tk.Frame(self.bottom_panel, bg=self.theme.bg_secondary)
        volume_frame.pack(side=tk.RIGHT, padx=15, pady=8)

        self.btn_mute = tk.Button(volume_frame, text="🔊", command=self.toggle_mute,
                                  bg=self.theme.button_bg, fg=self.theme.text_primary,
                                  relief=tk.FLAT, cursor="hand2", font=("Arial", 14), width=3)
        self.btn_mute.pack(side=tk.LEFT, padx=3)

        self.volume_var = tk.DoubleVar(value=self.volume * 100)
        self.volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                      variable=self.volume_var, command=self._on_volume_change,
                                      bg=self.theme.bg_secondary, fg=self.theme.text_primary,
                                      troughcolor=self.theme.slider_bg, highlightthickness=0,
                                      length=120, cursor="hand2")
        self.volume_slider.pack(side=tk.LEFT, padx=3)

        self.volume_label = tk.Label(volume_frame, text=f"{int(self.volume * 100)}%",
                                     bg=self.theme.bg_secondary, fg=self.theme.text_primary,
                                     font=("Arial", 10), width=5)
        self.volume_label.pack(side=tk.LEFT, padx=3)

    def _setup_bindings(self):
        """Klaviatura yorliqlari"""
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<m>', lambda e: self.toggle_mute())
        self.root.bind('<M>', lambda e: self.toggle_mute())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.root.bind('<Left>', lambda e: self.seek_relative(-10))
        self.root.bind('<Right>', lambda e: self.seek_relative(10))
        self.root.bind('<Control-Right>', lambda e: self.play_next())
        self.root.bind('<Control-Left>', lambda e: self.play_previous())
        self.root.bind('<Up>', lambda e: self._change_volume(5))
        self.root.bind('<Down>', lambda e: self._change_volume(-5))

    def _is_video_file(self, file_path):
        """Video fayl tekshirish"""
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm'}
        return Path(file_path).suffix.lower() in video_extensions

    def _format_time(self, seconds):
        """Vaqt formatlash"""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _update_time_display(self):
        """Vaqt ko'rsatish"""
        current_str = self._format_time(self.current_time)
        duration_str = self._format_time(self.video_duration)
        self.time_label.config(text=f"{current_str} / {duration_str}")

    def _update_progress_bar(self):
        """Progress bar yangilash"""
        if not self.progress_frame.winfo_exists():
            return

        width = self.progress_canvas.winfo_width()
        if width <= 1:
            width = 100

        self.progress_canvas.delete("all")

        if self.video_duration > 0:
            progress = self.current_time / self.video_duration
            fill_width = int(width * progress)
            self.progress_canvas.create_rectangle(0, 0, fill_width, 6,
                                                  fill=self.theme.progress_fill, outline="")

    def _update_volume_display(self):
        """Ovoz ko'rsatish"""
        self.volume_label.config(text=f"{int(self.volume * 100)}%")

    def _on_progress_click(self, event):
        """Progress bar click"""
        if self.video_duration > 0 and self.cap:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                progress = event.x / width
                new_time = progress * self.video_duration
                self._seek_to_time(new_time)

    def _on_progress_drag(self, event):
        """Progress bar drag"""
        if self.video_duration > 0 and self.cap:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                progress = max(0, min(1, event.x / width))
                new_time = progress * self.video_duration
                self._seek_to_time(new_time)

    def _seek_to_time(self, target_time):
        """Vaqtga o'tish"""
        if not self.cap:
            return

        target_time = max(0, min(target_time, self.video_duration))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            frame_number = int(target_time * fps)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_time = target_time
            self._update_time_display()
            self._update_progress_bar()

    def _on_volume_change(self, value):
        """Ovoz o'zgarishi"""
        self.volume = float(value) / 100
        self.is_muted = (self.volume == 0)

        if self.is_muted:
            self.btn_mute.config(text="🔇")
        elif self.volume < 0.3:
            self.btn_mute.config(text="🔈")
        elif self.volume < 0.7:
            self.btn_mute.config(text="🔉")
        else:
            self.btn_mute.config(text="🔊")

        self._update_volume_display()

    def _change_volume(self, delta):
        """Ovoz o'zgartirish"""
        new_volume = min(100, max(0, self.volume * 100 + delta))
        self.volume_var.set(new_volume)
        self._on_volume_change(new_volume)

    def _on_playlist_select(self, event):
        """Pleylist tanlash"""
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.playlist):
                self.load_video(self.playlist[index])

    def _on_closing(self):
        """Oyna yopilishi"""
        self.stop()
        self.root.destroy()

    def change_theme(self, theme_type):
        """Mavzu o'zgartirish"""
        self.current_theme = theme_type
        self.theme = ThemeManager.THEMES[theme_type]

        for widget in self.root.winfo_children():
            widget.destroy()

        self._setup_ui()
        self._setup_bindings()

    def open_file(self):
        """Fayl ochish"""
        file_types = [("Video fayllar", "*.mp4 *.avi *.mkv *.mov *.wmv *.webm"),
                      ("Barcha fayllar", "*.*")]

        file_path = filedialog.askopenfilename(title="Video faylni tanlang", filetypes=file_types)

        if file_path:
            self.load_video(file_path)

    def add_to_playlist(self, file_path=None):
        """Pleylistga qo'shish"""
        if not file_path:
            file_types = [("Video fayllar", "*.mp4 *.avi *.mkv *.mov *.wmv *.webm"),
                          ("Barcha fayllar", "*.*")]

            files = filedialog.askopenfilenames(title="Pleylistga video qo'shish", filetypes=file_types)

            for file in files:
                if file not in self.playlist:
                    self.playlist.append(file)
        else:
            if file_path not in self.playlist:
                self.playlist.append(file_path)

        self._update_playlist_display()

        if len(self.playlist) >= 1 and not self.current_video_path:
            self.load_video(self.playlist[0])

    def clear_playlist(self):
        """Pleylist tozalash"""
        if self.playlist:
            if messagebox.askyesno("Tasdiqlash", "Pleylistni tozalashni xohlaysizmi?"):
                self.stop()
                self.playlist.clear()
                self.playlist_listbox.delete(0, tk.END)
                self.current_playlist_index = -1
                self.current_video_path = None

    def _update_playlist_display(self):
        """Pleylist ko'rinishi"""
        self.playlist_listbox.delete(0, tk.END)

        for i, video_path in enumerate(self.playlist):
            file_name = Path(video_path).name
            prefix = "▶ " if i == self.current_playlist_index else "  "
            self.playlist_listbox.insert(tk.END, f"{prefix}{file_name}")

    def load_video(self, file_path):
        """Video yuklash"""
        try:
            self.stop()

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Fayl topilmadi: {file_path}")

            if not self._is_video_file(file_path):
                raise ValueError(f"Noto'g'ri video formati: {file_path}")

            self.current_video_path = file_path
            self.cap = cv2.VideoCapture(file_path)

            if not self.cap.isOpened():
                raise Exception("Video faylni ochib bo'lmadi")

            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

            if fps > 0:
                self.video_duration = frame_count / fps
            else:
                self.video_duration = 0

            self.current_time = 0

            if file_path in self.playlist:
                self.current_playlist_index = self.playlist.index(file_path)
                self._update_playlist_display()

            self.file_name_label.config(text=Path(file_path).name)
            self._update_time_display()
            self._update_progress_bar()

            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame
                self._display_frame(frame)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            self.play()

        except Exception as e:
            messagebox.showerror("Xatolik", f"Video yuklashda xatolik:\n{str(e)}")
            self.current_video_path = None
            if self.cap:
                self.cap.release()
                self.cap = None

    def play(self):
        """Video o'ynatish"""
        if not self.current_video_path or not self.cap:
            return

        if not self.is_playing:
            self.is_playing = True
            self.stop_playback = False
            self.btn_play.config(text="⏸")

            self.play_thread = threading.Thread(target=self._play_video, daemon=True)
            self.play_thread.start()

    def pause(self):
        """Pauza"""
        self.is_playing = False
        self.btn_play.config(text="▶")

    def toggle_play(self):
        """Play/Pause"""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def stop(self):
        """To'xtatish"""
        self.is_playing = False
        self.stop_playback = True

        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)

        if self.cap:
            self.cap.release()
            self.cap = None

        self.current_time = 0
        self.last_frame = None
        self.btn_play.config(text="▶")
        self._update_time_display()
        self._update_progress_bar()

        self.video_canvas.delete("all")

    def _play_video(self):
        """Video o'ynatish thread"""
        try:
            while self.is_playing and not self.stop_playback and self.cap is not None:
                with self.playback_lock:
                    if not self.is_playing:
                        break

                    ret, frame = self.cap.read()

                    if not ret:
                        self.is_playing = False
                        self.root.after(0, self._on_video_end)
                        break

                    self.last_frame = frame.copy()

                    current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                    fps = self.cap.get(cv2.CAP_PROP_FPS)

                    if fps > 0:
                        self.current_time = current_pos / fps

                    self.root.after(0, self._display_frame, frame.copy())
                    self.root.after(0, self._update_time_display)
                    self.root.after(0, self._update_progress_bar)

                    if fps > 0:
                        time.sleep(1.0 / (fps * self.playback_speed))
                    else:
                        time.sleep(0.033)

        except Exception as e:
            print(f"Video o'ynatish xatosi: {e}")

    def _display_frame(self, frame):
        """Frame ko'rsatish"""
        try:
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 800
                canvas_height = 600

            frame_height, frame_width = frame.shape[:2]

            scale = min(canvas_width / frame_width, canvas_height / frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)

            if new_width > 0 and new_height > 0:
                frame_resized = cv2.resize(frame, (new_width, new_height))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(img)

                self.video_canvas.delete("all")
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.video_canvas.create_image(x, y, anchor=tk.NW, image=img_tk)
                self.video_canvas.image = img_tk

        except Exception as e:
            print(f"Frame ko'rsatish xatosi: {e}")

    def _on_video_end(self):
        """Video tugaganda"""
        self.is_playing = False
        self.btn_play.config(text="▶")

        if self.current_playlist_index < len(self.playlist) - 1:
            self.play_next()

    def seek_relative(self, seconds):
        """Nisbiy vaqtga o'tish"""
        if not self.cap:
            return

        new_time = self.current_time + seconds
        new_time = max(0, min(new_time, self.video_duration))
        self._seek_to_time(new_time)

    def play_next(self):
        """Keyingi video"""
        if self.current_playlist_index < len(self.playlist) - 1:
            next_index = self.current_playlist_index + 1
            self.load_video(self.playlist[next_index])

    def play_previous(self):
        """Oldingi video"""
        if self.current_playlist_index > 0:
            prev_index = self.current_playlist_index - 1
            self.load_video(self.playlist[prev_index])

    def toggle_mute(self):
        """Ovoz o'chirish/yoqish"""
        self.is_muted = not self.is_muted

        if self.is_muted:
            self.previous_volume = self.volume
            self.volume = 0
            self.volume_var.set(0)
            self.btn_mute.config(text="🔇")
        else:
            self.volume = self.previous_volume
            self.volume_var.set(int(self.volume * 100))
            if self.volume > 0.7:
                self.btn_mute.config(text="🔊")
            elif self.volume > 0.3:
                self.btn_mute.config(text="🔉")
            else:
                self.btn_mute.config(text="🔈")

        self._update_volume_display()

    def toggle_fullscreen(self):
        """To'liq ekran"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

    def exit_fullscreen(self):
        """To'liq ekrandan chiqish"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)


def main():
    """Asosiy funksiya"""
    root = tk.Tk()
    app = VideoPlayer(root)
    root.mainloop()


if __name__ == "__main__":
    main()