#!/usr/bin/env python3

import argparse
import serial
from pythonosc.udp_client import SimpleUDPClient, OscMessageBuilder

parser = argparse.ArgumentParser(description='Crank communication')
parser.add_argument('tty', nargs='?', default='/dev/ttyACM0', help='TTY to use')
parser.add_argument('-c --count', dest='count', type=int, default=200, help="Warp count")

args = parser.parse_args()
osc = SimpleUDPClient('127.0.0.1', 1337)

with serial.Serial(args.tty, 9600) as ser:
    line = ser.readline()
    while line != b'':
        line = ser.readline()
        try:
            c = (-int(line.strip()) % args.count) / args.count
            builder = OscMessageBuilder('/crank')
            builder.add_arg(c, OscMessageBuilder.ARG_TYPE_FLOAT)
            osc.send(builder.build())
            print(c)
        except ValueError:
            print('???:', line)
