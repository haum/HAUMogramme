import serial
import time
import datetime
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
prev = 0

def read():
    try:
        val = int(ser.readline().strip())
        return val
    except Exception as e:
        return 0

read()
prev = read()
print(prev)
prev_time = datetime.datetime.now()

acc = 0
while True:
    try:
        val = read()
#        print(val)
        inc = val - prev
        acc += inc
        prev = val
    except:
        pass
    current = datetime.datetime.now()
    if (current - prev_time).seconds >= 0.1:
        print(f"->{acc}")
        acc = 0
        prev_time = current

