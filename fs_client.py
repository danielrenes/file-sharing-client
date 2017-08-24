#!/usr/bin/env python

import getpass
import json
import os
import SocketServer
import sys
import urllib2

import requests

user = getpass.getuser()
server_ip = None
shared = []
download_dir = None

def list_files(directory):
    files = []
    for _basedir, _subdirs, _files in os.walk(directory):
        for _file in _files:
            files.append(os.path.join(_basedir, _file))
    return files

def configure():
    with open('config') as config:
        for line in config:
            splitted = line.split('=')
            if splitted[0] == 'SERVER_IP':
                global server_ip
                server_ip = splitted[1].strip()
            elif splitted[0] == 'SHARE':
                shared_directories = [item.strip() for item in splitted[1].split(';')]
            elif splitted[0] == 'EXCLUDE':
                non_shared = [item.strip() for item in splitted[1].split(';')]
            elif splitted[0] == 'DOWNLOAD':
                global download_dir
                download_dir = splitted[1].strip()
    _shared = []
    for shared_directory in shared_directories:
        _shared.extend(list_files(shared_directory))
    _exclude = []
    for _non_shared in non_shared:
        if os.path.isdir(_non_shared):
            _exclude.extend(list_files(_non_shared))
        else:
            _exclude.append(_non_shared)
    global shared
    shared = [item for item in _shared if item not in _exclude]

def advertise():
    filenames = [path.split('/')[-1] for path in shared]
    requests.post('http://' + server_ip + ':5000' + '/advertise', params={'owner': user, 'shared': json.dumps(filenames)})

class TcpHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            line = line.rstrip('\r\n')
            if not line:
                break
            splitted = line.split(' ')
            if splitted[0] == 'GET':
                method = 'GET'
                param = json.loads(urllib2.unquote(splitted[1])[2:])['file']
            elif splitted[0] == 'POST':
                method = 'POST'
                param = splitted[1].split('=')[1]
            elif splitted[0].rstrip(':') == 'Content-Length':
                size = int(splitted[1])
        if method == 'GET':
            self.upload(param)
        elif method == 'POST':
            self.download(self.rfile, param, size)
        self.wfile.write('HTTP/1.1 200 OK')

    def upload(self, filename):
        for path in shared:
            if path.split('/')[-1] == filename:
                _file = path
        with open(_file, 'rb') as f:
            requests.post('http://' + server_ip + ':5000' + '/upload', params={'owner': user, 'filename': filename}, files={'file': f})
        print '[INFO] {0} was uploaded to server'.format(filename)

    def download(self, _file_obj, filename, size):
        path = os.path.join(download_dir, filename)
        first_line = True
        _read = 0
        _buffer = 4096 if size > 4096 else size
        with open(path, 'wb+') as f:
            while _read < size:
                f.write(_file_obj.read(_buffer))
                _read += _buffer
                _remaining = size - _read
                if _remaining < _buffer:
                    _buffer = _remaining
                if first_line:
                    first_line = False
                else:
                    sys.stdout.write('\r')
                    sys.stdout.flush()
                sys.stdout.write('[INFO] Downloading {0} from server: {1} kilobytes'.format(filename, _read))
                sys.stdout.flush()
            sys.stdout.write('\n')
            sys.stdout.flush()
        print '[INFO] {0} was downloaded from server'.format(filename)

configure()
advertise()
server = SocketServer.TCPServer(('127.0.0.1', 12345), TcpHandler)
server.allow_reuse_address = True
try:
    server.serve_forever()
except KeyboardInterrupt:
    server.shutdown()
    server.server_close()
