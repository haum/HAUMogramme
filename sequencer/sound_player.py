import pygame.mixer as pymix
import time

class SoundPlayer:
    def __init__(self) -> None:
        self.tracks = [
            pymix.Sound("./kick1.wav"),
            pymix.Sound("./snare.wav"),
            pymix.Sound("./hi_conga.wav"),
            pymix.Sound("./maracas.wav"),
            pymix.Sound("./handclap.wav"),
        ]

    def play(self, index: int, track: int):
        if track >= len(self.tracks):
            print(f"No track {track}")
            return
        pymix.Sound.play(self.tracks[track])
