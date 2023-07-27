import pygame.mixer as pymix
import time

class SoundPlayer:
    def __init__(self) -> None:
        self.tracks = [
            pymix.Sound("../../wubwub/wubwub/SAMPLES/drums/808/kick1.wav"),
            pymix.Sound("../../wubwub/wubwub/SAMPLES/drums/808/snare.wav"),
            pymix.Sound("../../wubwub/wubwub/SAMPLES/drums/808/hi_conga.wav"),
            pymix.Sound("../../wubwub/wubwub/SAMPLES/drums/808/maracas.wav"),
            pymix.Sound("../../wubwub/wubwub/SAMPLES/drums/808/handclap.wav"),
        ]

    def play(self, index: int, track: int):
        if track >= len(self.tracks):
            print(f"No track {track}")
            return
        pymix.Sound.play(self.tracks[track])
