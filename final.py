#import library
import numpy as np
import matplotlib.pyplot as plt
import sys, glob
import soundfile as sf # untuk membaca audio
import sofa # untuk membaca SOFA HTRFs
import librosa # mensampel ulang fungsi
from scipy import signal # fast convolution function
import IPython.display as ipd
from IPython.display import Audio # mendengarkan audio di notebook
import pathlib
import os
import wave
import threading
import sys
import time
import pydub 
from pydub.playback import play
import pyaudio
from math import floor
from rplidar import RPLidar

# Upload File
hrtf_dir_MIT = '3D Audio/elev0/*.wav'
# Global Variable
_MIT = glob.glob(hrtf_dir_MIT)
_MIT.sort()
print(_MIT)

# RPLidar scan loop
lidar = RPLidar('COM4')
scan_data = [0]*360
max_dist = 4000
angle_min = 0

# def lidar_scan():
try:
    for scan in lidar.iter_scans():
        max_dist = 4000
        angle_min = 0
        for (_, angle, distance) in scan:
            xx = min(359, floor(angle))
            scan_data[xx] = distance
                # if distance < max_dist:
                #     max_dist = distance
            if scan_data[xx] != 0:
                if scan_data[xx] < max_dist:
                    max_dist = scan_data[xx]
                    angle_min = xx
                    index = int(angle_min/5)
            # print (scan_data)
        print('\ndis: ', max_dist, ' | angle: ', angle_min)
            # print(' angle: ', angle_min)

        # min(scan_data)
except KeyboardInterrupt:print('Stoping.')

lidar.stop()
lidar.stop_motor()
lidar.disconnect()

# 3D Audio Loop
class WavePlayerLoop(threading.Thread):
    CHUNK = 1024

    def __init__(self, filepath, loop):
        """
        Initialize `WavePlayerLoop` class.
        PARAM:
            -- filepath (String) : File Path to wave file.
            -- loop (boolean)    : True if you want loop playback.
                                   False otherwise.
        """
        super(WavePlayerLoop, self).__init__()
        self.filepath = os.path.abspath(filepath)
        self.loop = loop

    def run(self):
        # Open Wave File and start play!
        # wf = wave.open(self.filepath, 'rb')
        player = pydub.AudioSegment.from_file(file = self.filepath, 
                                         format = "wav") 

        # Open Output Stream (based on PyAudio tutorial)
        # stream = player.open(format=player.get_format_from_width(wf.getsampwidth()),
        #                      channels=wf.getnchannels(),
        #                      rate=wf.getframerate(),
        #                      output=True)

        # PLAYBACK LOOP
        # data = wf.readframes(self.CHUNK)
        new_wav_file = player + self.map(600, 3000, 600, -50, 10)
        while self.loop:
            play(new_wav_file)
            time.sleep(0.1)
            index = int(angle_min/5)
            print('Using HRTF: ' + _MIT[index])
            [HRIR,fs_H] = sf.read(_MIT[index])
            

        # stream.close()

    def play(self):
        """
        Just another name for self.start()
        """
        self.start()

    def stop(self):
        """
        Stop playback.
        """
        self.loop = False
        
    def map (self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



index = int(angle_min/5)
# print('Using HRTF: ' + _MIT[index])
# [HRIR,fs_H] = sf.read(_MIT[index])

player = WavePlayerLoop(_MIT[index], True)
player.play()