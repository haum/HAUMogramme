#!/usr/bin/env python3

import argparse
import cv2
import cv2.aruco as aruco
import numpy as np
import time
import sys
from math import atan2, cos, pi
from pythonosc.udp_client import SimpleUDPClient, OscMessageBuilder

def compute_H(anchors):
    anchors_lst = []
    target = np.array((1, 1, -1, 1, -1, -1, 1, -1)) * cos(pi/4) 
    for a in anchors:
        anchors_lst.append(a[0])
        anchors_lst.append(a[1])
    if len(anchors_lst) != 8:
        anchors_lst = target
    H, _ = cv2.findHomography(np.float32(anchors_lst).reshape(4,2), np.float32(target).reshape(4,2), None)
    return H

def detect_forever(cap, fct):
    loopquit = 0
    show_fps = False
    fps_counter = 0

    H = compute_H([])
    landmarks = cv2.imread('homography_points.png', -1)
    if loopquit == 0:
        aruco_dict = cv2.aruco.getPredefinedDictionary(aruco.DICT_4X4_250)
        parameters =  cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        anchors = []
        def winevt(event, x, y, flags, userdata):
            nonlocal anchors, H
            if event == cv2.EVENT_LBUTTONDOWN:
                if flags & cv2.EVENT_FLAG_SHIFTKEY:
                    if len(anchors) == 4:
                        anchors = []
                        H = compute_H(anchors)
                    else:
                        anchors.append((x, y))
                        if len(anchors) == 4:
                            H = compute_H(anchors)
        cv2.namedWindow('HAUMogramme detection')
        cv2.setMouseCallback('HAUMogramme detection', winevt, None)

    fps_start = time.time()
    while loopquit == 0:
        key = cv2.waitKey(1)
        if key & 0xFF in (ord('q'), 27):
            cv2.destroyAllWindows()
            loopquit = 2
            break
        elif key & 0xFF in (ord('f'),):
            show_fps = not show_fps

        ret, frame = cap.read()
        fps_counter += 1
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)

            detections = []
            if not ids is None:
                for i, c in zip(ids, corners):
                    center = (
                        (c[0][0][0] + c[0][1][0] + c[0][2][0] + c[0][3][0]) / 4,
                        (c[0][0][1] + c[0][1][1] + c[0][2][1] + c[0][3][1]) / 4
                    )

                    nc = cv2.perspectiveTransform(np.float32(center).reshape(-1,1,2), H)
                    c1 = cv2.perspectiveTransform(np.float32((c[0][0][0], c[0][0][1])).reshape(-1,1,2), H)
                    center = (nc[0][0][0], nc[0][0][1])
                    angle = atan2(c1[0][0][1] - center[1], c1[0][0][0] - center[0])
                    detections.append((i[0], center, angle))
            fct(detections)

            if not corners is None:
                frame = aruco.drawDetectedMarkers(frame, corners)

            if len(anchors) < 4:
                y1, y2 = 10, 10 + landmarks.shape[0]
                x1, x2 = 10, 10 + landmarks.shape[1]
                a = landmarks[:, :, 3] / 255.0
                for c in range(0, 3):
                    frame[y1:y2, x1:x2, c] = (a * landmarks[:, :, c] + (1.0-a) * frame[y1:y2, x1:x2, c])

            for a in anchors:
                frame = cv2.circle(frame, tuple(map(int, a)), 5, (255,0,0), -1)

            cv2.imshow('HAUMogramme detection', frame)

        if fps_counter >= 30:
            t = time.time() - fps_start
            if show_fps: print('FPS:', fps_counter/t)
            fps_counter = 0
            fps_start = time.time()

    cap.release()
    cv2.destroyAllWindows()
    return loopquit

class DetectedList:
    def __init__(self):
        self.list = []
        self.osc = SimpleUDPClient('127.0.0.1', 1337)

    def evt(self, ev, n):
        tag, pos, angle, pad_id, timestamp = n
        builder = OscMessageBuilder('/pad/' + ev)
        builder.add_arg(pad_id, OscMessageBuilder.ARG_TYPE_INT)
        builder.add_arg(tag, OscMessageBuilder.ARG_TYPE_INT)
        builder.add_arg(pos[0], OscMessageBuilder.ARG_TYPE_FLOAT)
        builder.add_arg(pos[1], OscMessageBuilder.ARG_TYPE_FLOAT)
        builder.add_arg(angle, OscMessageBuilder.ARG_TYPE_FLOAT)
        self.osc.send(builder.build())

    def detected_item(self, tag, pos, angle):
        try:
            d = 0.01
            p = next(idx for idx, n in enumerate(self.list) if n[0] == tag and (n[1][0] - pos[0] < d) and (n[1][1] - pos[1] < d))
            n = (tag, pos, angle, self.list[p][3], time.time())
            da = min((2 * pi) - abs(angle - self.list[p][2]), abs(angle - self.list[p][2]))
            if da > pi / 90: self.evt('upd', n)
            self.list[p] = n
        except StopIteration:
            i = max((n[3] for n in self.list), default=0) + 1
            n = (tag, pos, angle, i, time.time())
            self.evt('add', n)
            self.list.append(n)

    def detected(self, lst):
        for tag, pos, angle in lst:
            self.detected_item(tag, pos, angle)
        now = time.time()
        def p(n):
            return now - n[4] < 0.2
        for n in self.list:
            if not p(n):
                self.evt('del', n)
        self.list = [n for n in self.list if p(n)]

parser = argparse.ArgumentParser(description='Webcam ARUco detection')
parser.add_argument('camera', nargs='?', default=0, help='Camera to use')
parser.add_argument('--w', dest='width', type=int, default=1280, help="Camera width")
parser.add_argument('--h', dest='height', type=int, default=720, help="Camera height")
parser.add_argument('--fps', dest='fps', type=int, default=25, help="Camera fps")

args = parser.parse_args()
cam = args.camera
try:
    cam = int(cam)
except:
    pass
cap = cv2.VideoCapture(cam, cv2.CAP_V4L2)
if not cap.isOpened():
    print('Camera not found')
    exit()
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FPS, args.fps)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
print('Capture:', cap.get(cv2.CAP_PROP_FRAME_WIDTH), 'x', cap.get(cv2.CAP_PROP_FRAME_HEIGHT), '@', cap.get(cv2.CAP_PROP_FPS))

dl = DetectedList()
detect_forever(cap, dl.detected)
