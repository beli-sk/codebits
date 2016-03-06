#!/usr/bin/env python3

import time
import logging
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('sdpserver')

class StreamNotFoundError(Exception):
    pass

class StreamManager(object):
    streams = {
        'cam1': {
            'cmd': "sudo raspivid -n -w 960 -h 540 -awb sun -fps 15 -t 0 -rot 180 -o -"
                " | cvlc -v stream:///dev/stdin --sout"
                " '#rtp{mux=ts,dst=239.0.0.9,port=5004,name=cam1,sdp=file:///tmp/cam1.sdp}'"
                " :demux=h264 --h264-fps 15 --clock-jitter=0",
            'sdpfile': '/tmp/cam1.sdp',
            }
        }
    procs = {}

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('sdpserver.StreamManager')

    def get_sdp(self, stream_id):
        try:
            cmd = self.streams[stream_id]['cmd']
            sdpfile = self.streams[stream_id]['sdpfile']
        except KeyError:
            raise StreamNotFoundError('Stream ID [%s] not found.' % stream_id)
        if not self.stream_status(stream_id):
            self.start_stream(stream_id)
            time.sleep(2)
        with open(sdpfile, 'r') as f:
            data = f.read()
        return data

    def start_stream(self, stream_id):
        self.logger.info('Starting stream ID [%s].' % stream_id)
        self.logger.debug('Running command [%s].' % self.streams[stream_id]['cmd'])
        self.procs[stream_id] = subprocess.Popen(self.streams[stream_id]['cmd'], shell=True)

    def stream_status(self, stream_id):
        try:
            if self.procs[stream_id].poll() == None:
                return True
            else:
                del self.procs[stream_id]
                return False
        except KeyError:
            return False


class SdpHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('sdpserver.SdpHTTPRequestHandler')
        self.strmng = StreamManager()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.logger.info('Handling request for path [%s].', self.path)
        try:
            data = self.strmng.get_sdp(self.path[1:])
        except FileNotFoundError:
            self.logger.error('SDP file not found.')
            self.send_error(404)
            return
        except StreamNotFoundError:
            self.logger.error('Stream not found.')
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-type", "application/sdp")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(bytes(data, 'UTF-8'))


if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SdpHTTPRequestHandler)
    logger.info('Ready to serve requests at [%s:%d].', server_address[0], server_address[1])
    httpd.serve_forever()

