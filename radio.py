#!/usr/bin/env python3

import threading
import os
import json
import time
import subprocess
import sys
import signal
import traceback
from mpris2 import get_players_uri
from mpris2 import Player
from http.server import HTTPServer, SimpleHTTPRequestHandler

def cmd(*args, check=True, print_it=True):
    args = [str(x) for x in args]
    if print_it:
        print('$', ' '.join(args))
    p = subprocess.run(args, check=check)
    return p.returncode == 0

def server():
    class CORSRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            return super(CORSRequestHandler, self).end_headers()

    httpd = HTTPServer(('0.0.0.0', 8000), CORSRequestHandler)
    httpd.serve_forever()

def now_playing():

    current = None
    history = []

    try:
        with open('playing.json', 'r') as f:
            j = json.loads(f.read())
            current = j['current']
            history = j['history']
    except:
        traceback.print_exc()

    while True:
        try:
            uri = next(get_players_uri())
            player = Player(dbus_interface_info={'dbus_uri': uri})
            track = player.Metadata
            if track['mpris:trackid'] and (current is None or track['mpris:trackid'] != current['mpris:trackid']):
                track['mpris:artUrl'] = track['mpris:artUrl'].replace('open.spotify.com', 'i.scdn.co')
                if current is not None:
                    history.insert(0, current)
                while len(history) > 100:
                    history.pop(len(history)-1)
                current = track

                with open('playing.json.tmp', 'w') as f:
                    f.write(json.dumps({
                        'current': track,
                        'history': history,
                    }))
                os.rename('playing.json.tmp', 'playing.json')
        except:
            traceback.print_exc()
        time.sleep(1)

def ffmpeg():
    cmd('ffmpeg',
        '-f', 'pulse', '-ac', '2', '-i', 'Radio.monitor',
        '-c:a', 'libopus', '-b:a', '320k',
        '-seg_duration', '1',
        '-streaming', '1',
        '-use_timeline', '1',
        '-use_template', '1',
        '-window_size', '600',
        '-adaptation_sets', 'id=0,streams=a',
        '-f', 'dash',
        'stream/stream.mpd',
    )

cmd('pacmd', 'unload-module', 'module-null-sink', check=False)
cmd('pacmd', 'unload-module', 'module-loopback', check=False)
cmd('pacmd', 'load-module', 'module-null-sink', 'sink_name=Radio', 'sink_properties=device.description=Radio')
cmd('pacmd', 'load-module', 'module-loopback', 'latency_msec=1', 'source=Radio.monitor')
cmd('rm', '-rf', 'stream')
cmd('mkdir', '-p', 'stream')

server_thread = threading.Thread(target=server, daemon=True)
server_thread.start()

now_playing_thread = threading.Thread(target=now_playing, daemon=True)
now_playing_thread.start()

ffmpeg_thread = threading.Thread(target=ffmpeg, daemon=True)
ffmpeg_thread.start()

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
#    cmd('pacmd', 'unload-module', 'module-null-sink', check=False)
#    cmd('pacmd', 'unload-module', 'module-loopback', check=False)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
