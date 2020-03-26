'use strict';

function init() {
    var url = "/stream/stream.mpd";

    var videoElement = document.querySelector(".videoContainer audio");
    var player = dashjs.MediaPlayer().create();

    player.updateSettings({
        'debug': {
            'logLevel': dashjs.Debug.LOG_LEVEL_INFO
        },
        'streaming': {
            'jumpGaps': true,
        },
    });


    player.initialize(videoElement, url, true);
    var controlbar = new ControlBar(player);
    controlbar.initialize();
}

document.addEventListener("DOMContentLoaded", function () {
    init();
});

var app = new Vue({
    el: '#app',
    data: {
        playing: {
            'now_playing': {},
            'previous': [],
        },
    },
    created() {
        this.refresh();
        setInterval(() => {
            this.refresh();
        }, 5000);
    },
    methods: {
        refresh() {
            fetch('/playing.json').then((response) => {
                return response.json();
            }).then((data) => {
                this.playing = data;
            })
        },
    },
});

