#!/usr/bin/env python3

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def print_handler(address, *args):
    print(f"{address}: {args}")

dispatcher = Dispatcher()
dispatcher.set_default_handler(print_handler)

server = BlockingOSCUDPServer(('0.0.0.0', 1337), dispatcher)

print('OSC listen')
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
print('Bye.')
