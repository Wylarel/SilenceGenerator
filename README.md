# WORK IN PROGRESS - Silence Generator
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://wylarel.com/mit/)
[![Discord](https://img.shields.io/badge/Chat-Discord-blue)](https://discord.gg/7qvmeh2)
[![Python](https://img.shields.io/badge/Made%20with-Python-orange)](https://www.python.org/)
  
[Carykh](https://www.github.com/carykh)'s [jumpcutter](https://github.com/carykh/jumpcutter) with a tkinter interface made by [BatchSource](https://www.github.com/BatchSource/Jumpcutter-GUI) adapted by [Wylarel](https://www.github.com/Wylarel)

### Some heads-up:

It uses Python 3.

It works on Ubuntu 16.04 and Windows 10. (It might work on other OSs too, we just haven't tested it yet.)

This program relies heavily on ffmpeg. It will start subprocesses that call ffmpeg, so be aware of that!
As the program runs, it saves every frame of the video as an image file in a
temporary folder. If your video is long, this could take a LOT of space. I have processed 17-minute videos completely fine, but be wary if you're gonna go longer.

You can download a zip file that includes ffmpeg [here](https://i.pinimg.com/originals/50/a3/c2/50a3c2e7743a41f65fc3c366059bc1db.jpg).

---

# Getting Started

Download and install the latest version of Python for Windows from https://www.python.org/.
When installing, make sure you add Python to PATH.

Next, open up cmd any type the following command to install the required libraries:
```
pip install Pillow audiotsm scipy numpy pytube3 easygui
```

Next, download [this zip](https://i.pinimg.com/originals/50/a3/c2/50a3c2e7743a41f65fc3c366059bc1db.jpg) and extract it.

Run 'main.pyw' in the SAME FOLDER as 'ffmpeg.exe' or use the batch file. The program will now start.
