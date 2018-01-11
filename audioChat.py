from socket import *
import threading
import pyaudio
import wave
import sys
import zlib
import struct
import pickle
import time
import numpy as np
from PyQt5.QtCore import QObject, QThread

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.5

class Audio_Server(QThread):

    def __init__(self, port) :
        QThread.__init__(self)
        #self.setDaemon(True)
        self.ADDR = ('', port)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.p = pyaudio.PyAudio()
        self.stream = None

    def __del__(self):
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def run(self):
        print("AUDIO server starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("remote AUDIO client success connected...")
        data = "".encode("utf-8")
        payloadSize = struct.calcsize("L")
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer = CHUNK
                                  )
        while True:
            while len(data) < payloadSize:
                data += conn.recv(81920)
            recvSize = data[:payloadSize]
            data = data[payloadSize:]
            unpackedDataSize = struct.unpack("L", recvSize)[0]
            while len(data) < unpackedDataSize:
                data += conn.recv(81920)
            frameData = data[:unpackedDataSize]
            data = data[unpackedDataSize:]
            frames = pickle.loads(frameData)
            for frame in frames:
                self.stream.write(frame, CHUNK)

class Audio_Client(QThread):

    def __init__(self ,ip, port):
        QThread.__init__(self)
        #self.setDaemon(True)
        self.ADDR = (ip, port)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.p = pyaudio.PyAudio()
        self.stream = None

    def __del__(self) :
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def run(self):
        print("AUDIO client starts...")
        while True:
            try:
                self.sock.connect(self.ADDR)
                break
            except:
                time.sleep(3)
                continue
        print("AUDIO client connected...")
        self.stream = self.p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)
        while self.stream.is_active():
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            senddata = pickle.dumps(frames)
            try:
                self.sock.sendall(struct.pack("L", len(senddata)) + senddata)
            except:
                break
