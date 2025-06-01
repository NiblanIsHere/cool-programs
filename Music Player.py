# Imports
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json
from PIL import Image
import pygame

# Global variables
current_playlist = []
current_song_index = 0
is_paused = False
config_file = "config.json"
config = {
    "last_folder": "",
    "volume": 100
}

# Load config
def load_config():
    global config
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            try:
                config.update(json.load(f))
            except json.JSONDecodeError:
                pass

# Save config
def save_config():
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)

# Music playback functions
def play_sound(path=None, index=None):
    global current_song_index

    if index is not None:
        current_song_index = index
        path = current_playlist[current_song_index]
    elif path:
        if path in current_playlist:
            current_song_index = current_playlist.index(path)

    if not path.endswith(".mp3"):
        path += ".mp3"

    print("Now playing:", path)
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

def play_next_song():
    global current_song_index
    if not current_playlist:
        return

    current_song_index += 1
    if current_song_index >= len(current_playlist):
        current_song_index = 0  # Loop back to start

    play_sound(index=current_song_index)

def play_previous_song():
    global current_song_index
    if not current_playlist:
        return

    current_song_index -= 1
    if current_song_index < 0:
        current_song_index = len(current_playlist) - 1  # Loop to last

    play_sound(index=current_song_index)

def check_song_end():
    if not pygame.mixer.music.get_busy() and not is_paused:
        play_next_song()
    root.after(1000, check_song_end)

# GUI setup
def window_setup():
    global root, albums

    # Colors
    dark_background_color = "#212121"
    dark_forground_color = "#2c2c2c"
    dark_dark_color = "#000000"

    light_background_color = "#EFEFEF"
    light_forground_color = "#FFFFFF"
    light_dark_color = "#DDDDDD"

    # Theme setup
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    if ctk.get_appearance_mode() == "Dark":
        background_color = dark_background_color
        forground_color = dark_forground_color
        dark_color = dark_dark_color
        text_color = "#EEEEEE"
    else:
        background_color = light_background_color
        forground_color = light_forground_color
        dark_color = light_dark_color
        text_color = "#000000"

    # Root
    root = ctk.CTk()
    root.title('Music Player')
    root.geometry('800x600')

    # Load config and folder
    load_config()
    path = config.get("last_folder", "")
    if not path or not os.path.exists(path):
        path = filedialog.askdirectory()
        if not path:
            messagebox.showerror("Error", "No folder selected. Exiting.")
            root.destroy()
            return
        config["last_folder"] = path
        save_config()

    # Frames
    bot_frame = ctk.CTkFrame(root, height=0, fg_color=forground_color)
    bot_frame.pack(side="bottom", fill="x")

    select = ctk.CTkButton(root, width=120, height=30, text="Select Folder", command=lambda: handle_select_folder())
    select.pack(side="top", anchor="w", padx=10, pady=10)

    albums = ctk.CTkScrollableFrame(root, width=85, fg_color=forground_color)
    albums.pack(side="left", fill="y")

    playlist = ctk.CTkScrollableFrame(root, fg_color=background_color)
    playlist.pack(side="left", fill="both", expand=True)

    def update_volume(value):
        volume = value / 100
        pygame.mixer.music.set_volume(volume)
        config["volume"] = int(value)
        save_config()

    def toggle_pause():
        global is_paused
        if is_paused:
            pygame.mixer.music.unpause()
            is_paused = False
        else:
            pygame.mixer.music.pause()
            is_paused = True

    volume_slider = ctk.CTkSlider(bot_frame, height=10, width=100, from_=0, to=100, command=update_volume)
    volume_slider.pack(padx=10, pady=30, side="right")
    volume_slider.set(config.get("volume", 100))
    pygame.mixer.music.set_volume(config.get("volume", 100) / 100)

    prev_button = ctk.CTkButton(bot_frame, height=50, width=70, text="Prev", command=play_previous_song)
    prev_button.pack(pady=10, side="left", padx=10)

    pause_button = ctk.CTkButton(bot_frame, height=50, width=70, text="Pause", command=toggle_pause)
    pause_button.pack(pady=10, side="left", padx=10)

    next_button = ctk.CTkButton(bot_frame, height=50, width=70, text="Next", command=play_next_song)
    next_button.pack(pady=10, side="left", padx=10)

    def open_playlist(folder_path):
        global current_playlist

        playlist_files = os.path.join(folder_path, "list_data.txt")
        if os.path.exists(playlist_files):
            with open(playlist_files, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file if line.strip()]
        else:
            lines = []

        current_playlist = [os.path.join(folder_path, song) for song in lines]

        for widget in playlist.winfo_children():
            widget.destroy()

        for i, song in enumerate(lines):
            button = ctk.CTkButton(
                playlist,
                text=song,
                width=40,
                height=40,
                fg_color=forground_color,
                text_color=text_color,
                command=lambda idx=i: play_sound(index=idx)
            )
            button.pack(pady=2, padx=5, fill="x")

    def load_albums(folder_path):
        for widget in albums.winfo_children():
            widget.destroy()

        folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        if not folders:
            messagebox.showinfo("No Albums", "No albums found in the selected folder.")
            return

        # Auto-open first album later if any
        first_album_path = None

        for folder in folders:
            folder_full_path = os.path.join(folder_path, folder)
            img_path = os.path.join(folder_full_path, "album_icon.png")

            if not first_album_path:
                first_album_path = folder_full_path

            if os.path.exists(img_path):
                image = ctk.CTkImage(
                    light_image=Image.open(img_path),
                    dark_image=Image.open(img_path),
                    size=(60, 60)
                )

                button = ctk.CTkButton(
                    albums,
                    image=image,
                    text="",
                    width=75,
                    height=75,
                    fg_color="transparent",
                    hover_color=forground_color,
                    command=lambda path=folder_full_path: open_playlist(path)
                )
                button.pack(pady=5, padx=5, fill="x")

        if first_album_path:
            open_playlist(first_album_path)

    def handle_select_folder():
        folder = filedialog.askdirectory()
        if folder:
            config["last_folder"] = folder
            save_config()
            load_albums(folder)

    load_albums(path)
    check_song_end()
    root.mainloop()

# Pygame init
pygame.mixer.init()

# Run the app
window_setup()
