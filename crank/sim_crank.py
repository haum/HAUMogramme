#!/usr/bin/env python3

import argparse
from pythonosc.udp_client import SimpleUDPClient, OscMessageBuilder
import PySimpleGUI as sg
import datetime

parser = argparse.ArgumentParser(description='Crank communication')
parser.add_argument('tty', nargs='?', default='/dev/ttyACM0', help='TTY to use')
parser.add_argument('-c --count', dest='count', type=int, default=200, help="Warp count")

args = parser.parse_args()
osc = SimpleUDPClient('127.0.0.1', 1337)

layout = [  
            [sg.Slider(range=(0,100), default_value=0, orientation='h', k="slider", enable_events=True)],
          ]

# Create the Window
window = sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs
tick = 0

start= datetime.datetime.now()
speed = 0
TIMEOUT = 250
while True:
    event, values = window.read(timeout=TIMEOUT)

    if event == "slider":
        speed = values["slider"]
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    end = datetime.datetime.now()
    if (end-start).total_seconds()*1000 > TIMEOUT:
        tick += speed/10
        c = (tick % args.count) / args.count
        builder = OscMessageBuilder('/crank')
        builder.add_arg(c, OscMessageBuilder.ARG_TYPE_FLOAT)
        osc.send(builder.build())
        start = end

window.close()
