#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
© Bzhu-Noors, 2019
"""
import sys
import os
import re
import time
import tkinter
import socket
from conf import *
G = O()
G.nick='nameless'
G.IP=''

SEPARATOR=b'\n'




def get_color(i):
    return '#{:02x}{:02x}{:02x}'.format(
            0,
            (30 + i*60) % 255,
            (15 + i*90) % 255
            )

def main ():
    ''
    class ConnectDialog(tkinter.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.title = 'Connection informations'

            tkinter.Label(self, text='Server IP').pack()
            self.host_entry = tkinter.Entry(self)
            self.host_entry.pack()

            tkinter.Label(self, text='Nickname').pack()
            self.nick_entry = tkinter.Entry(self)
            self.nick_entry.pack()
            tkinter.Button(self, text='Connect', command=self.go).pack()
            self.bind('<Return>', lambda *w: self.go())
            self.host_entry.focus_set()
        def go(self):
            G.IP = self.host_entry.get().strip()
            G.nick = self.nick_entry.get().strip()
            self.destroy()
            connect(G.IP, conf.port)
            window.after(200, network_check)
    def show_connect_dialog():
        print('1')
        connect_dialog = ConnectDialog(window)
        connect_dialog.transient(window)
        connect_dialog.grab_set()
        window.wait_window(connect_dialog)

    def get_client_name(client_id):
        if client_id in G.clients:
            return G.clients[client_id]
        return '{:d}'.format(client_id)
    # G is just a storage object: its goal is to easily make
    # variables accessible (readable and writeable) in functions
    G.clients = {}
    G.client_styles = {}
    G.x = 0
    G.y = 0
    G.last_btn_move = 0
    G.lines = []
    G.out_buf = b''
    G.unsent_start = 0
    G.serialized = b''
    G.socket_buf = b''
    window = tkinter.Tk()
    window.after(100, show_connect_dialog)
    canvas = tkinter.Canvas(window, width=500, height=300, background='#ffe')
    #people_list = tkinter.Listbox(window)
    chat_display = tkinter.Text(window, state='disabled', width=50)
    chat_line_var = tkinter.StringVar()
    chat_line = tkinter.Entry(window, textvariable=chat_line_var)

    canvas.pack(      side='left',   fill='both', expand=True)
    chat_line.pack(   side='bottom', fill='x',    expand=True)
    chat_display.pack(side='bottom', fill='both', expand=True)

    def cb_btn_press(event):
        canvas.focus_set()
        G.x = event.x
        G.y = event.y
        G.out_buf = b'L:%d,%d'%(G.x, G.y)
    def cb_btn_move(event):
        # throttling this (to avoid stressing network)
        distance = ((event.x - G.x) ** 2 + (event.y - G.y) **2)**0.5
        if time.time() - G.last_btn_move < 0.06 and distance < 20:
            return
        G.last_btn_move = time.time()
        l = canvas.create_line(G.x, G.y, event.x, event.y, fill='red', width=1)
        G.lines.append((-1, l))
        G.out_buf += b'-%d,%d'%(event.x, event.y)
        if len(G.out_buf) > 40:
            G.socket.send(G.out_buf)
            G.out_buf = b''
        G.x = event.x
        G.y = event.y
    def cb_btn_release(event):
        G.out_buf += b'-%d,%d\n'%(event.x, event.y)
        G.socket.send(G.out_buf)
        G.out_buf = b''
        G.x = event.x
        G.y = event.y
    def cb_keypress(event):
        if event.char == ' ': # space key
            G.socket.send(b'CLEAR\n')
        print(event.char)
    def send_msg(event):
        #chat_line
        msg = chat_line_var.get()
        chat_line_var.set('')
        G.socket.send(b'MSG:' + msg.encode('utf-8') + SEPARATOR)
    def connect(host, port):
        G.socket = socket.socket()
        G.socket.connect((host, port))
        G.socket.settimeout(0)
        G.socket.send('MSG:/nick {:s}\n'.format(G.nick).encode('utf-8'))
    def network_check():
        try:
            G.socket_buf += G.socket.recv(255)
        except:
            # TODO: except BlockingIOError
            window.after(200, network_check)
            return
        commands = G.socket_buf.split(SEPARATOR)
        G.socket_buf = commands[-1]
        commands = commands[0:-1]
        for command in commands:
            client_id = int(command[0:5])
            handle_command(client_id, command[5:])
        window.after(200, network_check)
    def handle_command(client_id, command):
        client_tag = 'client{:d}'.format(client_id)
        chat_display.tag_config(
                client_tag,
                foreground=get_color(client_id))
        print('client_id = {}'.format(client_id))
        if command.startswith(b'MSG:'):
            msg = command[4:].decode('utf-8')
            print('Received from {:d}: {:s}'.format(client_id, msg))
            if msg.startswith('/nick '):
                nickname = msg[len('/nick '):][0:20]
                G.clients[client_id] = nickname
                msg = 'client#{:d} is now known as {}'.format(client_id, nickname)
            chat_display.config(state='normal')
            chat_display.insert('end', '{:s}'.format(get_client_name(client_id)), client_tag)
            chat_display.insert('end', ': {:s}\n'.format(msg))
            chat_display.config(state='disabled')
        elif command.startswith(b'L:'):
            start = True
            for x,y in re.findall(b'(\\d+),(\\d+)', command):
                x = int(x)
                y = int(y)
                if not start:
                    l = canvas.create_line(
                            prev_x, prev_y, x, y,
                            fill=get_color(client_id),
                            width=2
                        )
                    G.lines.append((client_id, l))
                prev_x, prev_y = x, y
                start = False
        elif command.startswith(b'CLEAR'):
            for (line_client_id, line) in list(G.lines):
                if client_id == line_client_id or line_client_id == -1:
                    G.lines.remove((line_client_id, line))
                    canvas.delete(line)


    def on_exit(e):
        G.socket.send(b'EXIT\n')
        G.socket.close()

    canvas.bind('<Button-1>', cb_btn_press)
    canvas.bind('<B1-Motion>', cb_btn_move)
    canvas.bind('<ButtonRelease-1>', cb_btn_release)
    canvas.bind('<Key>', cb_keypress)
    chat_line.bind('<Return>', send_msg)
    window.bind('destroy', on_exit)
    print('entering main loop')
    window.mainloop()

if __name__ == "__main__":
    try: main ()
    except KeyboardInterrupt: print("\033[31mLeaving: User typed Ctrl+C.\033[0m")
