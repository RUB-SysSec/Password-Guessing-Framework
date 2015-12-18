#!/usr/bin/env python
import threading
from os import chdir
from signal import signal, SIGINT
from sys import exit
from time import sleep

# Constants
PORT = 31338
DOMAIN = 'localhost'
DOCUMENTROOT = '../../../'

# Global variable
myserver= None

def start_server(DOCUMENTROOT, DOMAIN, PORT):
    try:
      from http.server import HTTPServer, BaseHTTPRequestHandler # Python 3
    except ImportError: 
      import SimpleHTTPServer
      from BaseHTTPServer import HTTPServer # Python 2
      from SimpleHTTPServer import SimpleHTTPRequestHandler as BaseHTTPRequestHandler
    global mythread, myserver
    myserver = HTTPServer((DOMAIN, PORT), BaseHTTPRequestHandler)
    mythread = threading.Thread(target = myserver.serve_forever)
    mythread.deamon = True
    mythread.start()
    print("Starting web server on http://"+str(DOMAIN)+":"+str(PORT))
    return myserver

def cleanup():
    myserver.shutdown()
    print('Stopping server on port {}'.format(myserver.server_port))

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    cleanup()
    exit(0)

def main():
    chdir(DOCUMENTROOT)
    myserver = start_server(DOCUMENTROOT, DOMAIN, PORT)
    signal(SIGINT, signal_handler)
    print("Press Ctrl+C to shutdown")
    while(True): # Keep it alive
        sleep(120)

if __name__ == '__main__':
    main()