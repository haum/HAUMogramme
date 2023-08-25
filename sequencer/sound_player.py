import pyo

class Sound(pyo.SfPlayer):
    def __init__(self, path):
        super().__init__(path)

    def play(self, speed=1.0):
        self.setSpeed(speed)
        self.out()

class SoundPlayer:
    def __init__(self) -> None:
        self.audio_server = pyo.Server(buffersize=4096).boot()
        self.audio_server.start()
        self.tracks = [
            Sound("./samples/drums/808/kick1.wav"),
            Sound("./samples/drums/808/snare.wav"),
            Sound("./samples/drums/808/hi_conga.wav"),
            Sound("./samples/drums/808/maracas.wav"),
            Sound("./samples/drums/808/handclap.wav"),
        ]

    def play(self, track: int, speed: float = 1):
        if track >= len(self.tracks):
            print(f"No track {track}")
            return
        self.tracks[track].play(speed)
