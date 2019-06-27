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
from uuid import uuid1 as uuid
from conf import *

SEPARATOR = b'\n'

class ClientRep:
    def __init__(self, socket, ip, port, client_id):
        self.socket = socket
        self.ip = ip
        self.port = port
        self.id = client_id
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
            client_id = uuid()
        except:
            return
        print('New client!')
        client_socket.setblocking(0)
        client_rep = ClientRep(
            client_socket,
            ip,
            port,
            client_id)
        self.clients[client_id] = client_rep

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

        for client_id, client in self.clients.items():
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
            ret.append(b'MSG:client left')
            client_id = 0
        elif command.startswith(b'MSG:'):
            ret.append(command)
        elif command.startswith(b'L:'):
            ret.append(command)
        return ret

    def play_queue_to_clients(self):
        while self.send_queue:
            command = self.send_queue.pop(0)
            for client_id, client in self.clients.items():
                try:
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

