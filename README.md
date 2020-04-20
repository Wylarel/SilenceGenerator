# Jumpcutter Tkinter GUI

Carykh's jumpcutter but with a homemade tkinter interface.
Automatically edits videos. Original explanation by carykh [here](https://www.youtube.com/watch?v=DQ8orIurGxw).


## Some heads-up:

It uses Python 3.

It works on Ubuntu 16.04 and Windows 10. (It might work on other OSs too, we just haven't tested it yet.)

This program relies heavily on ffmpeg. It will start subprocesses that call ffmpeg, so be aware of that!
As the program runs, it saves every frame of the video as an image file in a
temporary folder. If your video is long, this could take a LOT of space. I have processed 17-minute videos completely fine, but be wary if you're gonna go longer.


## Pyinstaller
Pyinstaller doesn't work when the script is creating temp files. Cxfreeze doesn't work with scipy. :/

## View the UI:

![View the Interface](https://github.com/BatchSource/Jumpcutter-GUI/blob/master/example.gif)
