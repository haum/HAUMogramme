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
# 31 arucos

indexes = [69, 23, 45, 85, 96, 190, 87, 41, 74, 43]

pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Corbel', 30)
SCREEN_W = 1000
SCREEN_H = 700
screen = pygame.display.set_mode((1000, 700))

ITEM_SIZE = 20
M_2PI = 2*math.pi
NUM_INTERVAL = 8
CIRCLE_CENTER = (520, 350)
CIRCLE_RADIUS = 300
NUM_TRACKS = 5


class Scene:
    def __init__(self, sound_player: SoundPlayer) -> None:
        self.player = sound_player
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 4000)
        self.dispatcher= Dispatcher()
        self.dispatcher.set_default_handler(self.on_osc)
        self.osc_server = ThreadingOSCUDPServer(("0.0.0.0",1337), self.dispatcher)
        self.osc_server_thread = threading.Thread(target=self.osc_server.serve_forever)
        self.osc_server_thread.start()
        self.items = []
        self.angle = 0
        self.angle_inc = 0.01
        self.start = time.time()
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

    def on_osc(self, address, *args):
        #print(f"{address}: {args}")
        pad_id = args[1]
        pos_x = args[2]
        pos_y = args[3]
        left = (SCREEN_W/2 - pos_x*CIRCLE_RADIUS) +ITEM_SIZE/2
        right = (SCREEN_H/2 + pos_y*CIRCLE_RADIUS) -ITEM_SIZE/2
        if pad_id in indexes:
            i = indexes.index(pad_id)
            self.items[i].left = left
            self.items[i].top = right            

            print(f"{pos_x} {pos_y} {self.items[0].left} {self.items[0].top}")
        # (1, 37, 59.75, 464.25, -0.6055446863174438)

    def populate_items(self):
        start_x = 10
        start_y = 10
        num_per_line = 4
        for i in range(16):
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
            self.angle_inc = saved["angle_inc"]

    def save_scene(self):
        ret = {}
        ret["angle_inc"] = self.angle_inc
        ret["items"] = []
        for item in self.items:
            ret["items"].append({"x": item.left, "y": item.top})

        with open("save.json", "w") as f:
            json.dump(ret, f)

    def run(self):

        self.running = True

        while self.running:
            self.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                exit(0)
            elif event.type == MOUSEBUTTONDOWN:
                if self.dec_speed_button.collidepoint(event.pos):
                    self.angle_inc -= 0.01
                    print(f"dec speed to {self.angle_inc}")
                elif self.inc_speed_button.collidepoint(event.pos):
                    self.angle_inc += 0.01
                    print(f"inc speed to {self.angle_inc}")
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

        screen.fill((127, 127, 127))
    # concentric 'tracks'
        for i in reversed(range(NUM_TRACKS)):
            i+=1
            color = (200,200,200) if i%2 == 0 else (180,180,180)
            pygame.draw.circle(screen, color, CIRCLE_CENTER, (i/NUM_TRACKS)*CIRCLE_RADIUS) 

    # sectors
        head_line_color = (0,255,0)
        for a in self.interval_angles:
            line_x = CIRCLE_CENTER[0] + math.cos(a) * CIRCLE_RADIUS
            line_y = CIRCLE_CENTER[1] + math.sin(a) * CIRCLE_RADIUS
            pygame.draw.line(screen, (90,90,90), CIRCLE_CENTER, (line_x, line_y), width=2)
            if math.isclose(a, self.angle, rel_tol=M_2PI/100):
                head_line_color = (0,0, 255)

    # items
        line_x = CIRCLE_CENTER[0] + math.cos(self.angle) * CIRCLE_RADIUS
        line_y = CIRCLE_CENTER[1] + math.sin(self.angle) * CIRCLE_RADIUS
        for i, item in enumerate(self.items):
            dist_to_center = math.sqrt((item.center[0] - CIRCLE_CENTER[0])**2 + (item.center[1] - CIRCLE_CENTER[1])**2)
            HIT_BOX_SIZE = ITEM_SIZE*(dist_to_center/CIRCLE_RADIUS)*4

            testRect = Rect(
                item.center[0]-HIT_BOX_SIZE/2,
                item.center[1]-HIT_BOX_SIZE/2,
                HIT_BOX_SIZE,
                HIT_BOX_SIZE
            )
            #pygame.draw.rect(screen, (0, 0, 255, 127), testRect)
            if dist_to_center <= CIRCLE_RADIUS and testRect.clipline(CIRCLE_CENTER, (line_x, line_y)):
                track_id = int(dist_to_center/(CIRCLE_RADIUS/NUM_TRACKS))
                pygame.draw.rect(screen, (0, 0, 255), item, 4)
                self.client.send_message("/ping", [i, track_id])
                if i not in self.played_per_round:
                    self.played_per_round.append(i)
                    self.player.play(i, track_id)
            pygame.draw.rect(screen, (255, 0, 0), item)
            text_surface = my_font.render(f"{i}", False, (0, 0, 0))
            screen.blit(text_surface, item.center)

    # highlight moving item
    #    if self.index_moving != -1:
    #        pygame.draw.rect(screen, (0, 0, 255), items[self.index_moving], 4)

    # moving line
        pygame.draw.line(screen, head_line_color, CIRCLE_CENTER, (line_x, line_y), width=5)


    #UI
        pygame.draw.rect(screen, (200, 200, 200), self.dec_speed_button)
        text_surface = my_font.render("-", False, (255, 255, 255))
        screen.blit(text_surface, self.dec_speed_button)

        pygame.draw.rect(screen, (200, 200, 200), self.inc_speed_button)
        text_surface = my_font.render("+", False, (255, 255, 255))
        screen.blit(text_surface, self.inc_speed_button)

        pygame.draw.rect(screen, (200, 200, 200), self.save_button)
        text_surface = my_font.render("save", False, (255, 255, 255))
        screen.blit(text_surface, self.save_button)

        pygame.display.flip()
        end = time.time()
        diff = end - self.start
        if diff > 0.1:
            self.angle += self.angle_inc
            if self.angle > M_2PI:
                self.angle = 0
                self.played_per_round = []
            self.start = time.time()


player = SoundPlayer()
scene = Scene(player)

if len(sys.argv) > 1:
    scene.load_scene(sys.argv[1])
scene.run()
print("After running")
del(scene.client)
pygame.quit()
