# Radio

Stream music from your computer!

## Requirements
- PulseAudio
- python 3
- ffmpeg 4

Tested on Arch Linux. Ubuntu still has some problems related to PulseAudio I believe.

## Installation
- `pip3 install --user requirements.txt`

## Running
- `python3 radio.py`
- `pavucontrol`, and switch whatever app you want to play to the "radio" output
- go to `http://localhost:8000`