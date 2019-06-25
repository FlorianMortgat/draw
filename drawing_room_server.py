#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
© Bzhu, 2019
"""
import sys
import os
import re
import time
import socket
from conf import *

class Server (socket.socket):
    def __init__(self, port=conf.port):
        pass

def main ():
    ''

if __name__ == "__main__":
    try: main ()
    except KeyboardInterrupt: print("\033[31mLeaving: User typed Ctrl+C.\033[0m")
