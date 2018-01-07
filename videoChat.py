from socket import *
import threading
import cv2
import sys
import struct
import pickle
import time
import zlib
import numpy as np
import beautyFace
from PyQt5.QtCore import QObject, QThread

class Video_Server(QThread):
    def __init__(self, port) :
        QThread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        self.sock = socket(AF_INET ,SOCK_STREAM)

    def __del__(self):
        self.sock.close()
        try:
            cv2.destroyAllWindows()
        except:
            pass

    def run(self):
        print("VEDIO server starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("remote VEDIO client success connected...")
        data = "".encode("utf-8")
        payload_size = struct.calcsize("L")
        cv2.namedWindow('Remote', cv2.WINDOW_NORMAL)
        while True:
            while len(data) < payload_size:
                data += conn.recv(81920)
            packed_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while len(data) < msg_size:
                data += conn.recv(81920)
            zframe_data = data[:msg_size]
            data = data[msg_size:]
            frame_data = zlib.decompress(zframe_data)
            frame = pickle.loads(frame_data)
            cv2.imshow('Remote', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyWindow('Remote')
                break

class Video_Client(QThread):
    def __init__(self ,ip, port, level):
        QThread.__init__(self)
        self.ADDR = (ip, port)
        if level == 0:
            self.interval = 0
        elif level == 1:
            self.interval = 1
        else:
            self.interval = 2
        self.fx = 1 / (self.interval + 1)
        if self.fx < 0.3:
            self.fx = 0.3
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.cap = cv2.VideoCapture(0)
        print("VEDIO client starts...")

    def __del__(self) :
        self.sock.close()
        self.cap.release()
        try:
            cv2.destroyAllWindows()
        except:
            pass

    def run(self):
        while True:
            try:
                self.sock.connect(self.ADDR)
                break
            except:
                time.sleep(3)
                continue

        cv2.namedWindow('You', cv2.WINDOW_NORMAL)
        print("VEDIO client connected...")
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            cv2.imshow('You', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyWindow('You')
            frame = beautyFace.beautyFace(frame)
            sframe = cv2.resize(frame, (0,0), fx=self.fx, fy=self.fx)
            data = pickle.dumps(sframe)
            zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            try:
                self.sock.sendall(struct.pack("L", len(zdata)) + zdata)
            except:
                break
            for i in range(self.interval):
                self.cap.read()
