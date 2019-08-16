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
import random
from conf import *

SEPARATOR = b'\n'

class ClientRep:
    N = 1
    def __init__(self, socket, ip, port):
        self.socket = socket
        self.ip = ip
        self.port = port
        self.id = ClientRep.N
        ClientRep.N += 1
        self.recv_part = b''
        self.send_part = b''
    def send(self, *args):
        return self.socket.send(*args)
    def recv(self, *args):
        return self.socket.recv(*args)

class Server(socket.socket):
    def __init__(self, port=conf.port):
        self.clients = {}
        self.port = port
        socket.socket.__init__(self)
        self.bind(('', port))
        self.listen(0)
        self.setblocking(0)
        self.history = []
        self.send_queue = []

    def check_new_client(self):
        try:
            client_socket, (ip, port) = self.accept()
        except:
            return
        print('New client!')
        client_socket.setblocking(0)
        client_rep = ClientRep(
            client_socket,
            ip,
            port)
        self.clients[client_rep.id] = client_rep
        self.send_queue.append((client_rep.id, b'MSG:New client'))

    def recv_client(self, client):
        try:
            part = client.recv(255)
        except BlockingIOError:
            return []
        client.recv_part += part
        commands = client.recv_part.split(SEPARATOR)
        client.recv_part = commands[-1]
        commands = commands[0:-1]
        return commands

    def main(self):
        self.check_new_client()

        for client_id, client in self.clients.copy().items():
            commands = self.recv_client(client)
            for command in commands:
                to_be_sent = self.handle_command(client_id, command)
                if to_be_sent:
                    self.send_queue.extend(to_be_sent)
        self.play_queue_to_clients()

    def handle_command(self, client_id, command):
        ret = []
        if command == b'EXIT':
            print('Client leaves.')
            leaving_client = self.clients.pop(client_id)
            leaving_client.socket.close()

            ret.append((client_id, b'MSG:client left'))
            client_id = 0
        elif command == b'CLEAR':
            ret.append((client_id, command))
        elif command.startswith(b'MSG:'):
            ret.append((client_id, command))
        elif command.startswith(b'L:'):
            ret.append((client_id, command))
        return ret

    def play_queue_to_clients(self):
        while self.send_queue:
            emitter_id, command = self.send_queue.pop(0)
            for client_id, client in self.clients.copy().items():
                try:
                    client.send('{:05d}'.format(emitter_id).encode('utf-8'))
                    client.send(command + SEPARATOR)
                except BrokenPipeError:
                    print('Broken pipe :(')
                    leaving_client = client
                    leaving_client.socket.close()
                    self.clients.pop(client.id)




def main ():
    ''
    print('starting')
    server = Server()
    while True:
        server.main()
        time.sleep(0.1)
    server.shutdown()
    server.close()

if __name__ == "__main__":
    try: main ()
    except KeyboardInterrupt: print("\033[31mLeaving: User typed Ctrl+C.\033[0m")

