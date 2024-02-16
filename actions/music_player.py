import pygame
import random
import os


def music_init():
    pygame.mixer.init()


def play_song(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    print("Playing song")


def play_playlist(folder_path):
    song_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]
    random_song = random.choice(song_files)
    file_path = os.path.join(folder_path, random_song)
    play_song(file_path)


def stop_song():
    pygame.mixer.music.stop()