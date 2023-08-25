import pyo

class SoundPlayer:
    def __init__(self) -> None:
        self.audio_server = pyo.Server(buffersize=1024).boot()
        self.audio_server.start()
        self.tracks = [
            pyo.SfPlayer("./samples/drums/808/kick1.wav"),
            pyo.SfPlayer("./samples/drums/808/snare.wav"),
            pyo.SfPlayer("./samples/drums/808/hi_conga.wav"),
            pyo.SfPlayer("./samples/drums/808/maracas.wav"),
            pyo.SfPlayer("./samples/drums/808/handclap.wav"),
        ]

    def play(self, track: int):
        if track >= len(self.tracks):
            print(f"No track {track}")
            return
        self.tracks[track].out()
