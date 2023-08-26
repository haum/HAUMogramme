
use_pygame = False
if use_pygame:
    import pygame
else:
    import pyo


class Sound:
    def __init__(self, path):
        if use_pygame:
            self.sound = pygame.mixer.Sound(path)
        else:
            self.sound = pyo.SfPlayer(path)

    def stop(self):
        self.sound.stop()

    def play(self, speed=1.0, loop=False):
        if use_pygame:
            if loop:
                self.sound.play(-1)
            else:
                self.sound.play()
        else:
            self.sound.setLoop(loop)
            self.sound.setSpeed(speed)
            self.sound.out()


class Bank:
    def __init__(self, tracks, drone: Sound = None) -> None:
        self.tracks = tracks
        self.drone = drone

    def play(self, track_id: int, speed=1.0):
        if track_id >= len(self.tracks):
            print(f"No track {track_id}")
            return
        self.tracks[track_id].play(speed)

    def enable(self):
        if self.drone:
            if use_pygame:
                self.drone
            self.drone.play(loop=True)

    def disable(self):
        if self.drone:
            self.drone.stop()


class SoundPlayer:
    def __init__(self) -> None:
        if not use_pygame:
            self.audio_server = pyo.Server(buffersize=4096).boot()
            self.audio_server.start()
        self.banks = [
            Bank([
                Sound("./samples/drums/808/kick1.wav"),
                Sound("./samples/drums/808/snare.wav"),
                Sound("./samples/drums/808/hi_conga.wav"),
                Sound("./samples/drums/808/maracas.wav"),
                Sound("./samples/drums/808/handclap.wav"),
            ], drone = Sound("./samples/banks/0/drone.wav")),

            Bank([
                Sound("./samples/banks/0/t0.wav"),
                Sound("./samples/banks/0/t1.wav"),
                Sound("./samples/banks/0/t2.wav"),
                Sound("./samples/banks/0/t3.wav"),
                Sound("./samples/banks/0/t4.wav"),
            ], drone = Sound("./samples/banks/0/drone.wav")),

            Bank([
                Sound("./samples/banks/1/t0.wav"),
                Sound("./samples/banks/1/t1.wav"),
                Sound("./samples/banks/1/t2.wav"),
                Sound("./samples/banks/1/t3.wav"),
                Sound("./samples/banks/1/t4.wav"),
                Sound("./samples/banks/1/t5.wav"),
                Sound("./samples/banks/1/t6.wav"),
            ], drone = Sound("./samples/banks/1/drone.wav")),

            Bank([
                Sound("./samples/banks/2/t0.wav"),
                Sound("./samples/banks/2/t1.wav"),
                Sound("./samples/banks/2/t2.wav"),
                Sound("./samples/banks/2/t3.wav"),
                Sound("./samples/banks/2/t4.wav"),
            ], drone = Sound("./samples/banks/2/drone.wav")),

#            Bank([
#                Sound("./samples/synth/misc/note_ambience.wav"),
#                Sound("./samples/synth/misc/7thsweep_wave.wav"),
#                Sound("./samples/keys/hit1.wav"),
#                Sound("./samples/keys/hit2.wav"),
#                Sound("./samples/keys/hit2.wav"),
#            ], drone = Sound("./samples/banks/1/drone.wav"))

        ]
        self.bank_id = 0
        self.banks[0].enable()

    def change_bank(self):
        prev = self.bank_id
        self.bank_id += 1
        if self.bank_id >= len(self.banks):
            self.bank_id = 0
        if prev != self.bank_id:
            print(f"switch to bank {self.bank_id}")
            print(f"Disabling blank {prev}")
            self.banks[prev].disable()
            print(f"Enabling blank {self.bank_id}")
            self.banks[self.bank_id].enable()

    def play(self, track: int, index: int, speed: float = 1):
        bank = self.banks[self.bank_id]
        bank.play(track, speed)
