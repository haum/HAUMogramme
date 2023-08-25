#!/usr/bin/env python3

import math
import time
import pygame
from pygame.locals import *
from sys import exit
from pythonosc import udp_client
import json
import sys
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import threading
from sound_player import SoundPlayer
import numpy as np
import datetime
import argparse


def roundPartial(value, resolution):
    return round(value / resolution) * resolution


MAX_CRANK_SPEED = 0.05
NUM_TAGS = 50
SCREEN_W = 1000
SCREEN_H = 700

ITEM_SIZE = 20
M_2PI = 2*math.pi
NUM_INTERVAL = 8
CIRCLE_CENTER = (520, 350)
CIRCLE_RADIUS = 300
NUM_TRACKS = 4
SNAP_GRID_INTERVAL = 32


class Scene:
    def __init__(self, sound_player: SoundPlayer, no_ui=False) -> None:
        self.no_ui = no_ui
        if not no_ui:
            self.my_font = pygame.font.SysFont('Corbel', 30)
            self.screen = pygame.display.set_mode((1000, 700))

        self.player = sound_player
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 4000)
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self.on_osc)
        self.osc_server = ThreadingOSCUDPServer(
            ("0.0.0.0", 1337), self.dispatcher)
        self.osc_server_thread = threading.Thread(
            target=self.osc_server.serve_forever)
        self.osc_server_thread.start()
        self.items = []
        self.items_in_circle = []
        self.played_per_round = []
        self.interval_angles = []
        self.running = False
        self.index_moving = -1
        for interval in range(NUM_INTERVAL):
            self.interval_angles.append((M_2PI/NUM_INTERVAL) * interval)
        self.populate_items()
        self.dec_speed_button = Rect(800, 20, 30, 30)
        self.inc_speed_button = Rect(835, 20, 30, 30)
        self.save_button = Rect(880, 20, 50, 30)
        self.tick = 0
        self.last_played_tick = 0
        self.bpm = 120
        self.start = datetime.datetime.now()
        self.score = {}
        self.tick_by_crank = False
        self.last_crank_val = 0
        self.crank_speed = 0

    def on_osc(self, address, *args):
        if address == '/crank':
            self.tick_by_crank = True
            self.tick = args[0] * SNAP_GRID_INTERVAL
            crank_speed = abs(self.last_crank_val - args[0])
            if crank_speed <= MAX_CRANK_SPEED:
                self.crank_speed = crank_speed
            self.last_crank_val = args[0]
        else:
            pad_id = args[1]
            pos_x = args[2]
            pos_y = args[3]
            left = (SCREEN_W/2 - pos_x*CIRCLE_RADIUS) + ITEM_SIZE/2
            right = (SCREEN_H/2 + pos_y*CIRCLE_RADIUS) - ITEM_SIZE/2
            if pad_id < NUM_TAGS:
                i = pad_id
                if address == "/pad/del":
                    self.items[i].left = 0
                    self.items[i].top = 0
                else:
                    self.items[i].left = left
                    self.items[i].top = right
                # print(f"{address} {pad_id} {pos_x} {pos_y} {self.items[0].left} {self.items[0].top}")
            else:
                print(f"pad id {pad_id} not < {NUM_TAGS}")
            # (1, 37, 59.75, 464.25, -0.6055446863174438)

    def populate_items(self):
        start_x = 10
        start_y = 10
        num_per_line = 4
        for i in range(NUM_TAGS):
            line_i = i % num_per_line
            col_i = int(i / num_per_line)
            px = start_x + line_i*(ITEM_SIZE + 5)
            py = start_y + col_i*(ITEM_SIZE + 5)
            self.items.append(Rect(px, py, ITEM_SIZE, ITEM_SIZE))

    def load_scene(self, path):
        print(f"loading file {path}")
        with open(path, "r") as f:
            saved = json.load(f)
            for i, item in enumerate(saved["items"]):
                self.items[i].left = item["x"]
                self.items[i].top = item["y"]
            self.bpm = saved["bpm"]

    def save_scene(self):
        ret = {}
        ret["bpm"] = self.bpm
        ret["items"] = []
        for item in self.items:
            ret["items"].append({"x": item.left, "y": item.top})

        with open("save.json", "w") as f:
            json.dump(ret, f)

    def run(self):

        self.running = True

        while self.running:
            self.update()
            time.sleep(0.01)

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                exit(0)
            elif event.type == MOUSEBUTTONDOWN:
                if self.dec_speed_button.collidepoint(event.pos):
                    self.tick_by_crank = False
                    self.bpm -= 10
                elif self.inc_speed_button.collidepoint(event.pos):
                    self.player.change_bank()
#                    self.tick_by_crank = False
#                    self.bpm += 10
                elif self.save_button.collidepoint(event.pos):
                    print("save scene")
                    self.save_scene()
                else:
                    self.index_moving = -1
                    for i, item in enumerate(self.items):
                        if item.collidepoint(event.pos):
                            self.index_moving = i
                            break
            elif event.type == MOUSEBUTTONUP:
                self.index_moving = -1
            elif event.type == MOUSEMOTION and self.index_moving != -1:
                self.items[self.index_moving].move_ip(event.rel)
        if not self.no_ui:
            self.screen.fill((127, 127, 127))

        # concentric 'tracks'
            for i in reversed(range(NUM_TRACKS)):
                i += 1
                color = (200, 200, 200) if i % 2 == 0 else (180, 180, 180)
                pygame.draw.circle(self.screen, color,
                                   CIRCLE_CENTER, (i/NUM_TRACKS)*CIRCLE_RADIUS)

        # sectors
            head_line_color = (0, 255, 0)
            for a in self.interval_angles:
                line_x = CIRCLE_CENTER[0] + math.cos(a) * CIRCLE_RADIUS
                line_y = CIRCLE_CENTER[1] + math.sin(a) * CIRCLE_RADIUS
                pygame.draw.line(self.screen, (90, 90, 90),
                                 CIRCLE_CENTER, (line_x, line_y), width=2)

        # items
        angle = (self.tick / SNAP_GRID_INTERVAL) * M_2PI
        line_x = CIRCLE_CENTER[0] + math.cos(angle) * CIRCLE_RADIUS
        line_y = CIRCLE_CENTER[1] + math.sin(angle) * CIRCLE_RADIUS
        self.items_in_circle = []
        for i, item in enumerate(self.items):
            dist_to_center = math.sqrt(
                (item.center[0] - CIRCLE_CENTER[0])**2 + (item.center[1] - CIRCLE_CENTER[1])**2)
            HIT_BOX_SIZE = ITEM_SIZE*(dist_to_center/CIRCLE_RADIUS)*4

            if dist_to_center <= CIRCLE_RADIUS:
                track_id = int(dist_to_center/(CIRCLE_RADIUS/NUM_TRACKS))
                self.items_in_circle.append((item, track_id))
            if not self.no_ui:
                pygame.draw.rect(self.screen, (255, 0, 0), item)
                text_surface = self.my_font.render(f"{i}", False, (0, 0, 0))
                self.screen.blit(text_surface, item.center)

        # highlight moving item
        #    if self.index_moving != -1:
        #        pygame.draw.rect(screen, (0, 0, 255), items[self.index_moving], 4)

        # moving line
        if not self.no_ui:
            pygame.draw.line(self.screen, head_line_color,
                             CIRCLE_CENTER, (line_x, line_y), width=5)

        # UI
            pygame.draw.rect(self.screen, (200, 200, 200),
                             self.dec_speed_button)
            text_surface = self.my_font.render("-", False, (255, 255, 255))
            self.screen.blit(text_surface, self.dec_speed_button)

            pygame.draw.rect(self.screen, (200, 200, 200),
                             self.inc_speed_button)
            text_surface = self.my_font.render("+", False, (255, 255, 255))
            self.screen.blit(text_surface, self.inc_speed_button)

            pygame.draw.rect(self.screen, (200, 200, 200), self.save_button)
            text_surface = self.my_font.render("save", False, (255, 255, 255))
            self.screen.blit(text_surface, self.save_button)

            text_surface = self.my_font.render(
                str(self.crank_speed), False, (0, 0, 255))
            self.screen.blit(text_surface, Rect(800, 60, 100, 30))

        end2 = datetime.datetime.now()
        diff_ms = 15000 / self.bpm
        if False:
            if (end2-self.start).total_seconds()*1000 > diff_ms:
                play_sound = True
                if not self.tick_by_crank:
                    self.tick += 1
                    if self.tick >= SNAP_GRID_INTERVAL:
                        self.tick = 0
                self.start = datetime.datetime.now()
        notes = self.generate_score()
        self.play_notes(notes)
        if not self.no_ui:
            self.draw_score(notes)
            pygame.display.flip()

    def generate_score(self):
        notes = {}
        item_index = 0
        for item, track_id in self.items_in_circle:
            a = np.arctan2(item.center[1] - CIRCLE_CENTER[1],
                           item.center[0] - CIRCLE_CENTER[0])
            if a < 0:
                a = M_2PI + a
            item_pos = (a / M_2PI) * SNAP_GRID_INTERVAL
            snapped_val = math.floor(roundPartial(
                item_pos, M_2PI / SNAP_GRID_INTERVAL))
            if snapped_val == M_2PI:
                snapped_val = 0
            note_pos = round(snapped_val)
            if note_pos not in notes:
                notes[note_pos] = []
            notes[note_pos].append(track_id)
            item_index += 1

        return notes

    def play_notes(self, notes):
        snapped_tick = math.floor(self.tick)
        if self.last_played_tick == snapped_tick:
            return
        num_ticks_to_play = snapped_tick - self.last_played_tick
        if num_ticks_to_play < 0:
            num_ticks_to_play = SNAP_GRID_INTERVAL + num_ticks_to_play
        audio_speed = self.crank_speed / MAX_CRANK_SPEED
        for t in reversed(range(num_ticks_to_play)):
            tick = (snapped_tick - t) % SNAP_GRID_INTERVAL
            if tick in notes:
                for track_id in notes[tick]:
                    self.player.play(track_id, audio_speed)
        self.last_played_tick = snapped_tick

    def draw_score(self, notes):
        start_x = 10
        start_y = 570
        score_width = 900
        score_height = 120
        pygame.draw.rect(self.screen, (255, 255, 255), Rect(
            start_x, start_y, score_width, score_height))
        interval_len = score_width / NUM_INTERVAL
        for i in range(0, NUM_INTERVAL):
            x = start_x+i*interval_len
            sub_interval_len = interval_len/4
            for ii in range(3):
                xx = x + sub_interval_len*(ii+1)
                pygame.draw.line(self.screen,
                                 (127, 127, 127),
                                 (xx, start_y),
                                 (xx, start_y+score_height), width=2)
            pygame.draw.line(self.screen,
                             (0, 0, 0),
                             (x, start_y),
                             (x, start_y+score_height), width=2)

        head_pos = (self.tick / SNAP_GRID_INTERVAL) * score_width

        track_size = score_height / NUM_TRACKS

        for note_pos, track_ids in notes.items():
            for track_id in track_ids:
                snapped_val = note_pos*score_width/SNAP_GRID_INTERVAL
                pygame.draw.circle(self.screen,
                                (0, 255, 0),
                                (start_x + snapped_val,
                                    start_y+track_size*track_id),
                                radius=10)
        pygame.draw.line(self.screen,
                         (255, 0, 0),
                         (start_x + head_pos, start_y),
                         (start_x + head_pos, start_y+score_height), width=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HAUMogramme sequencer')
    parser.add_argument('-s', dest='save_file', type=str,
                        default="", help="file to load")
    parser.add_argument('--no-ui', dest="no_ui", action='store_true')

    args = parser.parse_args()

    pygame.init()
    player = SoundPlayer()
    if args.no_ui:
        print("No ui")
    else:
        pygame.font.init()

    scene = Scene(player, args.no_ui)
    if args.save_file != "":
        scene.load_scene(args.save_file)
    scene.run()
    print("After running")
    del (scene.client)
    pygame.quit()
