import pygame.mixer as pymix

class SoundPlayer:
    def __init__(self) -> None:
        self.tracks = [
            pymix.Sound("./samples/drums/808/kick1.wav"),
            pymix.Sound("./samples/drums/808/snare.wav"),
            pymix.Sound("./samples/drums/808/hi_conga.wav"),
            pymix.Sound("./samples/drums/808/maracas.wav"),
            pymix.Sound("./samples/drums/808/handclap.wav"),
        ]

    def play(self, track: int):
        if track >= len(self.tracks):
            print(f"No track {track}")
            return
        pymix.Sound.play(self.tracks[track])
