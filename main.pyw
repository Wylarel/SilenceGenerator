from contextlib import closing
from PIL import Image
import subprocess
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from scipy.io import wavfile
import numpy as np
import re
import math
from shutil import copyfile, rmtree
import os
import argparse
from pytube import YouTube
import easygui as e


def downloadFile(url):
    name = YouTube(url).streams.first().download()
    newname = name.replace(' ', '_')
    os.rename(name, newname)
    return newname


def getMaxVolume(s):
    maxv = float(np.max(s))
    minv = float(np.min(s))
    return max(maxv, -minv)


def copyFrame(inputFrame, outputFrame):
    src = TEMP_FOLDER + "/frame{:06d}".format(inputFrame + 1) + ".jpg"
    dst = TEMP_FOLDER + "/newFrame{:06d}".format(outputFrame + 1) + ".jpg"
    if not os.path.isfile(src):
        return False
    copyfile(src, dst)
    if outputFrame % 20 == 19:
        print(str(outputFrame + 1) + " time-altered frames saved.")
    return True


def inputToOutputFilename(filename):
    from random import randrange
    dotIndex = filename.rfind(".")
    return filename[:dotIndex] + f"_ALTERED-{randrange(10)}{randrange(10)}{randrange(10)}{randrange(10)}{randrange(10)}" + filename[dotIndex:]


def createPath(s):
    # assert (not os.path.exists(s)), "The filepath "+s+" already exists. Don't want to overwrite it. Aborting."

    try:
        os.mkdir(s)
    except OSError:
        print("Creation of the directory %s failed. (The TEMP folder may already exist. Delete or rename it, and try again.")
        tkadddata('Deleting old temp files...')
        deletePath(TEMP_FOLDER)
        createPath(TEMP_FOLDER)
        # messagebox.showerror("Error", "It looks like the program previously crashed. Try restarting the program and try again.")
        # sys.exit(1)


def deletePath(s):  # Dangerous! Watch out!
    try:
        rmtree(s, ignore_errors=False)
    except OSError:
        print("Deletion of the directory %s failed" % s)
        print(OSError)


###############


import tkinter as tk
from tkinter.filedialog import askopenfilename

root = tk.Tk()
varAsTxt = tk.StringVar()
os.system('title Silence Generator Console - Do not close.')
root.title('Silence Generator')
root.maxsize(350, 570)
root.minsize(350, 570)
root.resizable(False, False)
# root.attributes('-alpha', 0.9)

root.config(background="#f0f0f0")

from tkinter import messagebox
import sys


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        sys.exit()


root.protocol("WM_DELETE_WINDOW", on_closing)

# GLOBALS
args_sounded_speed = 1.0
args_silent_speed = 0.0
args_output_file = ''
args_input_file = None
args_url = None
args_frame_margin = 2
args_frame_rate = 30
args_frame_quality = 3
args_silent_threashold = 0.03
args_sample_rate = 44100
exportcolumn = 2


def globalize(): global exportcolumn, args_sounded_speed, args_silent_speed, args_output_file, args_input_file, args_url, args_frame_margin, args_frame_rate, args_frame_quality, args_silent_threashold, args_sample_rate


globalize()

tk.Label(root, text='Silence Generator', background="#f0f0f0", fg="black", font=("Arial Bold", 20)).grid(row=0, columnspan=2, pady=10)

tk.Label(root, text='Input File  ', background="#f0f0f0", fg="black", font=("Arial", 14)).grid(row=2, rowspan=2, column=0)


def setfile():
    def filereset():
        args_input_file = None
        filename_label.grid_forget()
        tk_filereset.grid_forget()
        tk_file = tk.Button(root, text='Choose File', background='#FFFFFF', width='20', fg='#000000', command=setfile)
        tk_file.grid(column=1, row=2)

        tk_fileyt = tk.Button(root, text='YouTube URL', background='#FFFFFF', width='20', fg='#000000', command=setyt)
        tk_fileyt.grid(column=1, row=3)

    global args_input_file
    args_input_file = askopenfilename()
    if args_input_file != "" and args_input_file is not None:
        if ' ' in args_input_file:
            args_input_file = None
            messagebox.showerror("Error", "There is a SPACE (\' \') character in the folder path to this file, and that breaks this program. Please move the file to a folder without a SPACE character and try again.")
        else:
            tk_file.grid_forget()
            tk_fileyt.grid_forget()
            args_input_file_view = ''
            for i in str(args_input_file)[::-1]:
                if i == '\\' or i == '/':
                    break
                else:
                    args_input_file_view += i
            args_input_file_view = args_input_file_view[::-1]

            filename_label = tk.Label(root, text=args_input_file_view, width='25', background="#f0f0f0", fg="black", font=("Arial", 10))
            filename_label.grid(row=2, column=1)

            tk_filereset = tk.Button(root, text='Reset', background='#FFFFFF', width='20', fg='#000000', command=filereset)
            tk_filereset.grid(column=1, row=3)


def setyt():
    def filereset2():
        args_url = None
        filename_label.grid_forget()
        tk_filereset.grid_forget()
        tk_file = tk.Button(root, text='Choose File', background='#FFFFFF', width='20', fg='#000000', command=setfile)
        tk_file.grid(column=1, row=2)

        tk_fileyt = tk.Button(root, text='YouTube URL', background='#FFFFFF', width='20', fg='#000000', command=setyt)
        tk_fileyt.grid(column=1, row=3)

    global args_url
    args_url = e.enterbox('Please Paste the YouTube Link:', 'YouTube Link')

    if args_url is not None and args_url != '':
        tk_file.grid_forget()
        tk_fileyt.grid_forget()
        filename_label = tk.Label(root, text=args_url, width='25', background="#f0f0f0", fg="black", font=("Arial", 10))
        filename_label.grid(row=3, column=1)

        tk_filereset = tk.Button(root, text='Reset', background='#FFFFFF', width='20', fg='#000000', command=filereset2)
        tk_filereset.grid(column=1, row=2)


tk_file = tk.Button(root, text='Choose File', background='#FFFFFF', width='20', fg='#000000', command=setfile)
tk_file.grid(column=1, row=2)

tk_fileyt = tk.Button(root, text='YouTube URL', background='#FFFFFF', width='20', fg='#000000', command=setyt)
tk_fileyt.grid(column=1, row=3)

tk.PanedWindow(root, orient="horizontal", width=350, background="black", height=2).grid(row=4, columnspan=2, pady=10)
tk.Label(root, text='Options', background="#f0f0f0", fg="black", font=("Arial", 14)).grid(row=5, columnspan=2)


# TOGGLE START
def setstart():
    global args_output_file, args_input_file
    # args_output_file = tk_outputfile.get("1.0",'end-1c')
    if args_input_file is None and args_url is None:
        messagebox.showerror("Error", "Please select an a File/URL to export.")
    else:
        root.destroy()
    # root.destroy()


tk_start = tk.Button(root, text='Export', width=50, background='white', fg='#000000', command=setstart)
tk_start.grid(columnspan=2, row=150)

# OUTPUT FILE NAME

'''
tk.Label(root, text='Output Name   \n(Optional)', background="#f0f0f0", justify='left', fg="black", font=("Arial", 10)).grid(row=10,column=0)
tk_outputfile = tk.Text(root, height=1, width=25)
tk_outputfile.grid(row=10,column=1,pady='10')
'''


# SOUNDED SPEED
def setsoundspeed(x):
    global args_sounded_speed
    args_sounded_speed = x


tk_soundedspeed = tk.Scale(root,
                           orient="horizontal",
                           from_=0.0,  # MVC-Model-Part value-min-limit
                           width=10,
                           to=10.0,  # MVC-Model-Part value-max-limit
                           length=210,  # MVC-Visual-Part layout geometry [px]
                           digits=3,  # MVC-Visual-Part presentation trick
                           resolution=0.1,  # MVC-Controller-Part stepping
                           command=setsoundspeed,
                           )
tk_soundedspeed.set(1)
tk_soundedspeed.grid(row=11, column=1, padx='10')
tk.Label(root, text='Sounded Speed', background="#f0f0f0", fg="black", font=("Arial", 10)).grid(row=11, column=0)


# SILENT SPEED
def setsilentspeed(x):
    global args_silent_speed
    args_silent_speed = x


tk_silentspeed = tk.Scale(root,
                          orient="horizontal",
                          from_=0.0,  # MVC-Model-Part value-min-limit
                          width=10,
                          to=10.0,  # MVC-Model-Part value-max-limit
                          length=210,  # MVC-Visual-Part layout geometry [px]
                          digits=3,  # MVC-Visual-Part presentation trick
                          resolution=0.1,  # MVC-Controller-Part stepping
                          command=setsilentspeed,
                          ).grid(row=12, column=1, padx='10')
tk.Label(root, text='Silent Speed    ', background="#f0f0f0", fg="black", font=("Arial", 10)).grid(row=12, column=0)

tk.Label(root, text='*0 for instant', background="#f0f0f0", fg="black", font=("Arial", 8)).grid(row=13, column=0)

tk.PanedWindow(root, orient="horizontal", width=350, background="black", height=2).grid(row=14, columnspan=2, pady=10)
tk.Label(root, text='Advanced Options', background="#f0f0f0", fg="black", font=("Arial", 14)).grid(row=15, columnspan=2)


# FRAME MARGIN
def setframemargin(x):
    global args_frame_margin
    args_frame_margin = x


tk_framemargin = tk.Scale(root,
                          orient="horizontal",
                          from_=0,  # MVC-Model-Part value-min-limit
                          width=10,
                          to=10,  # MVC-Model-Part value-max-limit
                          length=210,  # MVC-Visual-Part layout geometry [px]
                          resolution=1,  # MVC-Controller-Part stepping
                          command=setframemargin,
                          )
tk_framemargin.set(2)
tk_framemargin.grid(row=16, column=1, padx='10')
tk.Label(root, text='Frame Margin   ', background="#f0f0f0", fg="black", font=("Arial", 10)).grid(row=16, column=0)


# FRAME RATE
def setframerate(x):
    global args_frame_rate
    args_frame_rate = x


tk_framerate = tk.Scale(root,
                        orient="horizontal",
                        from_=1,  # MVC-Model-Part value-min-limit
                        width=10,
                        to=90,  # MVC-Model-Part value-max-limit
                        length=210,  # MVC-Visual-Part layout geometry [px]
                        resolution=1,  # MVC-Controller-Part stepping
                        command=setframerate,
                        )
tk_framerate.set(30)
tk_framerate.grid(row=17, column=1, padx='10')
tk.Label(root, text='Frame Rate      ', background="#f0f0f0", fg="black", font=("Arial", 10)).grid(row=17, column=0)


# FRAME QUALITY
def setframequality(x):
    global args_frame_quality
    args_frame_quality = x


tk_framequality = tk.Scale(root,
                           orient="horizontal",
                           from_=1,  # MVC-Model-Part value-min-limit
                           width=10,
                           to=31,  # MVC-Model-Part value-max-limit
                           length=210,  # MVC-Visual-Part layout geometry [px]
                           resolution=1,  # MVC-Controller-Part stepping
                           command=setframequality,
                           )
tk_framequality.set(3)
tk_framequality.grid(row=18, column=1, padx='10')
tk.Label(root, text='Frame Quality   \n(1 = Best)   ', background="#f0f0f0", justify='left', fg="black", font=("Arial", 10)).grid(row=18, column=0)


# SILENT THREASHOLD
def setsilent_threashold(x):
    global args_silent_threashold
    args_silent_threashold = x


tk_silent_threashold = tk.Scale(root,
                                orient="horizontal",
                                from_=0.01,  # MVC-Model-Part value-min-limit
                                width=10,
                                to=1,  # MVC-Model-Part value-max-limit
                                length=210,  # MVC-Visual-Part layout geometry [px]
                                resolution=0.01,  # MVC-Controller-Part stepping
                                command=setsilent_threashold,
                                )
tk_silent_threashold.set(0.03)
tk_silent_threashold.grid(row=19, column=1, padx='10')
tk.Label(root, text='Silent Threashold', background="#f0f0f0", justify='left', fg="black", font=("Arial", 10)).grid(row=19, column=0)

# SAMPLE RATE
sample_rate_view = '44100hz'


def toggle_samplerate():
    global sample_rate_view
    if sample_rate_view == '44100hz':
        sample_rate_view = '48000hz'
        args_sample_rate = 48000
    elif sample_rate_view == '48000hz':
        sample_rate_view = '44100hz'
        args_sample_rate = 44100
    tk_sample_rate.config(text=sample_rate_view)


tk_sample_rate = tk.Button(root, text=sample_rate_view, width=28, background='#FFFFFF', fg='#000000', command=toggle_samplerate)
tk_sample_rate.grid(row=20, column=1, pady='10')
tk.Label(root, text='Sample Rate    ', background="#f0f0f0", justify='left', fg="black", font=("Arial", 10)).grid(row=20, column=0)

tk.PanedWindow(root, orient="horizontal", width=300, background="#f0f0f0", height=2).grid(row=21, columnspan=2, pady=10)

tk.Label(root, text='© Original by carykh  -  GUI by BatchSource', background="#f0f0f0", justify='left', fg="#787878", font=("Arial Bold", 10)).grid(row=200, columnspan=2)

root.mainloop()

if args_input_file is not None: args_input_file = str(args_input_file)
if args_url is not None: args_url = str(args_url)
if args_output_file is not None and args_output_file != '': args_output_file = str(args_output_file).replace(' ', '_') + '.mp4'

args_silent_threashold = float(args_silent_threashold)

args_sounded_speed = float(args_sounded_speed)
if args_sounded_speed == 0.0: args_sounded_speed = float(999999)
args_silent_speed = float(args_silent_speed)
if args_silent_speed == 0.0: args_silent_speed = float(999999)

args_frame_margin = int(args_frame_margin)
args_sample_rate = int(args_sample_rate)
args_frame_rate = int(args_frame_rate)
args_frame_quality = int(args_frame_quality)

###############

root = tk.Tk()
root.title('Jumpcutter GUI - Exporting...')
root.maxsize(350, 510)
root.minsize(350, 510)
root.resizable(False, False)
root.attributes('-alpha', 0.9)
root.config(background="#f0f0f0")


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        sys.exit()


root.protocol("WM_DELETE_WINDOW", on_closing)

tk.Label(root, text='Exporting...', background="#f0f0f0", fg="black", font=("Arial Bold...", 20)).pack()
tk.Label(root, text='(Don\'t try to close out!)', background="#f0f0f0", fg="black", font=("Arial Bold", 10)).pack(side='top')

tk.PanedWindow(root, orient="horizontal", width=300, background="#000000", height=2).pack(pady=10)
tk.Label(root, text='© Original by carykh  -  GUI by BatchSource', background="#f0f0f0", justify='left', fg="#787878", font=("Arial Bold", 10)).pack(side='bottom')


def tkadddata(x):
    global exportcolumn
    exportcolumn += 1
    tk.Label(root, text=x, background="#f0f0f0", fg="black", font=("Arial", 10)).pack(side='top', anchor='w', padx='20')
    root.update()


root.update()

tkadddata('Setting variables...')

frameRate = args_frame_rate
SAMPLE_RATE = args_sample_rate
SILENT_THRESHOLD = args_silent_threashold
FRAME_SPREADAGE = args_frame_margin
NEW_SPEED = [args_silent_speed, args_sounded_speed]
if args_url != None:
    INPUT_FILE = downloadFile(args_url)
else:
    INPUT_FILE = args_input_file
URL = args_url
FRAME_QUALITY = args_frame_quality

assert INPUT_FILE != None, "why u put no input file, that dum"

if len(args_output_file) >= 1:
    OUTPUT_FILE = args_output_file
else:
    OUTPUT_FILE = inputToOutputFilename(INPUT_FILE)

TEMP_FOLDER = "TEMP"
AUDIO_FADE_ENVELOPE_SIZE = 400  # smooth out transitiion's audio by quickly fading in/out (arbitrary magic number whatever)

createPath(TEMP_FOLDER)

tkadddata('Extracting frames... (may take a while)')

command = "ffmpeg -i " + INPUT_FILE + " -qscale:v " + str(FRAME_QUALITY) + " " + TEMP_FOLDER + "/frame%06d.jpg -hide_banner"
subprocess.call(command, shell=True)

tkadddata('Extracting audio...')

command = "ffmpeg -i " + INPUT_FILE + " -ab 160k -ac 2 -ar " + str(SAMPLE_RATE) + " -vn " + TEMP_FOLDER + "/audio.wav"

subprocess.call(command, shell=True)

tkadddata('Setting parameters...')

command = "ffmpeg -i " + TEMP_FOLDER + "/input.mp4 2>&1"
f = open(TEMP_FOLDER + "/params.txt", "w")
subprocess.call(command, shell=True, stdout=f)

tkadddata('Getting audio data...')

sampleRate, audioData = wavfile.read(TEMP_FOLDER + "/audio.wav")
audioSampleCount = audioData.shape[0]
maxAudioVolume = getMaxVolume(audioData)

tkadddata('Reading parameters...')

f = open(TEMP_FOLDER + "/params.txt", 'r+')
pre_params = f.read()
f.close()
params = pre_params.split('\n')

tkadddata('Calculating frame/sample rates...')

for line in params:
    m = re.search('Stream #.*Video.* ([0-9]*) fps', line)
    if m is not None:
        frameRate = float(m.group(1))

samplesPerFrame = sampleRate / frameRate

audioFrameCount = int(math.ceil(audioSampleCount / samplesPerFrame))

hasLoudAudio = np.zeros((audioFrameCount))

tkadddata(f'Looking for audio chucks louder than \"{args_silent_threashold}\"...')

for i in range(audioFrameCount):
    start = int(i * samplesPerFrame)
    end = min(int((i + 1) * samplesPerFrame), audioSampleCount)
    audiochunks = audioData[start:end]
    maxchunksVolume = float(getMaxVolume(audiochunks)) / maxAudioVolume
    if maxchunksVolume >= SILENT_THRESHOLD:
        hasLoudAudio[i] = 1

tkadddata(f'Adding a frame margin of \"{args_frame_margin}\"...')

chunks = [[0, 0, 0]]
shouldIncludeFrame = np.zeros((audioFrameCount))
for i in range(audioFrameCount):
    start = int(max(0, i - FRAME_SPREADAGE))
    end = int(min(audioFrameCount, i + 1 + FRAME_SPREADAGE))
    shouldIncludeFrame[i] = np.max(hasLoudAudio[start:end])
    if (i >= 1 and shouldIncludeFrame[i] != shouldIncludeFrame[i - 1]):  # Did we flip?
        chunks.append([chunks[-1][1], i, shouldIncludeFrame[i - 1]])

chunks.append([chunks[-1][1], audioFrameCount, shouldIncludeFrame[i - 1]])
chunks = chunks[1:]

outputAudioData = np.zeros((0, audioData.shape[1]))
outputPointer = 0

tkadddata('Altering audio and saving new time-altered frames...')

lastExistingFrame = None
for chunk in chunks:
    audioChunk = audioData[int(chunk[0] * samplesPerFrame):int(chunk[1] * samplesPerFrame)]

    sFile = TEMP_FOLDER + "/tempStart.wav"
    eFile = TEMP_FOLDER + "/tempEnd.wav"
    wavfile.write(sFile, SAMPLE_RATE, audioChunk)
    with WavReader(sFile) as reader:
        with WavWriter(eFile, reader.channels, reader.samplerate) as writer:
            tsm = phasevocoder(reader.channels, speed=NEW_SPEED[int(chunk[2])])
            tsm.run(reader, writer)
    _, alteredAudioData = wavfile.read(eFile)
    leng = alteredAudioData.shape[0]
    endPointer = outputPointer + leng
    outputAudioData = np.concatenate((outputAudioData, alteredAudioData / maxAudioVolume))

    # outputAudioData[outputPointer:endPointer] = alteredAudioData/maxAudioVolume

    # smooth out transitiion's audio by quickly fading in/out
    if leng < AUDIO_FADE_ENVELOPE_SIZE:
        outputAudioData[outputPointer:endPointer] = 0  # audio is less than 0.01 sec, let's just remove it.
    else:
        premask = np.arange(AUDIO_FADE_ENVELOPE_SIZE) / AUDIO_FADE_ENVELOPE_SIZE
        mask = np.repeat(premask[:, np.newaxis], 2, axis=1)  # make the fade-envelope mask stereo
        outputAudioData[outputPointer:outputPointer + AUDIO_FADE_ENVELOPE_SIZE] *= mask
        outputAudioData[endPointer - AUDIO_FADE_ENVELOPE_SIZE:endPointer] *= 1 - mask

    startOutputFrame = int(math.ceil(outputPointer / samplesPerFrame))
    endOutputFrame = int(math.ceil(endPointer / samplesPerFrame))
    for outputFrame in range(startOutputFrame, endOutputFrame):
        inputFrame = int(chunk[0] + NEW_SPEED[int(chunk[2])] * (outputFrame - startOutputFrame))
        didItWork = copyFrame(inputFrame, outputFrame)
        if didItWork:
            lastExistingFrame = inputFrame
        else:
            copyFrame(lastExistingFrame, outputFrame)

    outputPointer = endPointer
tkadddata('Saving new time-altered audio...')
wavfile.write(TEMP_FOLDER + "/audioNew.wav", SAMPLE_RATE, outputAudioData)

'''
outputFrame = math.ceil(outputPointer/samplesPerFrame)
for endGap in range(outputFrame,audioFrameCount):
    copyFrame(int(audioSampleCount/samplesPerFrame)-1,endGap)
'''
tkadddata('Building final video... (may take a while)')

command = "ffmpeg -framerate " + str(frameRate) + " -i " + TEMP_FOLDER + "/newFrame%06d.jpg -i " + TEMP_FOLDER + "/audioNew.wav -strict -2 " + OUTPUT_FILE
subprocess.call(command, shell=True)

tkadddata('Cleaning up temp files...')
deletePath(TEMP_FOLDER)

messagebox.showinfo("Complete", f"The process is complete. File name: {OUTPUT_FILE}")
