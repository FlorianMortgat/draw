#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
© Flo M, Scooter5561, 2021
"""
import sys
import os
import re
import time
import pygame
from pygame.locals import *
import socket
from conf import *
from collections import OrderedDict
G = O()
G.nick='nameless'
G.IP=''

SEPARATOR=b'\n'
#scooter was here :D
defined_colors = OrderedDict([
    ('red', (255, 0, 0)),
    ('orange',(255, 70, 0)),
    ('yellow', (255, 255, 0)),
    ('green', (0, 255, 0)),
    ('blue', (0, 0, 255)),
    ('dark_blue', (0, 0, 150)),
    ('purple', (255, 0, 255))
])
#basic colors in rgb

def get_color(i):
    return '#{:02x}{:02x}{:02x}'.format(
            0,
            (30 + i*60) % 255,
            (15 + i*90) % 255
            )
class PygameClient:
    def __init__(self, host, port):
        self.window = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('pygame client')
        pygame.init()
        self.drawing = pygame.Surface((640, 480))
        self.MAX_DRAW_SIZE = 20
        self.clock = pygame.time.Clock()
        self.over = False
        self.is_drawing = False
        self.history = []
        self.thickness_history = []
        self.polygon = []
        self.clear()
        self.draw_size = 4
        self.draw_color = defined_colors['red']
        self.history.append({
            'type': 'color',
            'color': self.draw_color
        })
        self.history.append({
            'type': 'size',
            'size': 4
        })
        self.font = pygame.font.Font(None, 40)
    def refresh(self):
        self.clock.tick(60) #60 fps max
        self.window.blit(self.drawing, (0, 0))
        draw_thickness_text = self.font.render('Draw Thickness: %d'%self.draw_size, False, ((20,40,100)))
        self.window.blit(draw_thickness_text, (20, 20))

        for n, color in enumerate(defined_colors):
            if self.draw_color == defined_colors[color]:
                pygame.draw.rect(self.window, (255,255,255), pygame.Rect((300-2 + n * 24, 20-2), (20+4, 20+4)))
            pygame.draw.rect(self.window, (defined_colors[color]),  pygame.Rect((300 + n * 24, 20), (20, 20)))

        help_text = pygame.font.render('Help', False, )
        pygame.display.update()
    def handle_events(self):
        keys = pygame.key.get_pressed() #the better way to get key presses
        for event in pygame.event.get():
            if event.type == QUIT:
                self.over = True
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    hitbutton = False
                    for n, color in enumerate(defined_colors):
                        rectangle = pygame.Rect((300 + n * 24, 20), (20, 20))
                        if rectangle.collidepoint(event.pos):
                            self.draw_color = defined_colors[color]
                            # self.history.append({
                            #     'type': 'color',
                            #     'color': self.draw_color
                            # })
                            hitbutton = True
                            break
                    if not hitbutton:
                        self.is_drawing = True
                    #self.polygon.append((event.x, event.y))
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.is_drawing:
                        self.is_drawing = False
                        #pygame.draw.circle(self.window, ((255,0,0)), event.pos, self.draw_size // 2) #4 wide, because 2 both ways
                        self.history.append({
                            'type': 'polygon',
                            'polygon': self.polygon,
                            'size': self.draw_size,
                            'color': self.draw_color,
                        })
                        # self.history.append({
                        #     'type': 'size',
                        #     'size': self.draw_size
                        #})
                        self.polygon = []
                elif event.button == 4:#mouse wheel up/down (button 4/5)
                    self.draw_size += 1
                    if self.draw_size > self.MAX_DRAW_SIZE:
                        self.draw_size -= 1
                elif event.button == 5:
                    self.draw_size -= 1
                    if self.draw_size < 1:
                        self.draw_size = 1
                    #self.polygon.append((event.x, event.y))
            elif event.type == MOUSEMOTION:
                if self.is_drawing:
                    self.polygon.append(event.pos)
                    #pygame.draw.circle(self.window, ((255, 0, 0)), event.pos, self.draw_size // 2)
                    if len(self.polygon) >= 2:
                        pygame.draw.line(self.drawing, self.draw_color, self.polygon[-2], self.polygon[-1], self.draw_size)
            elif event.type == KEYUP:
                if event.key == pygame.K_z and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                    print('ctrl+z')
                    self.polygon = []
                    if len(self.history) > 1: self.history.pop()
                    self.draw_history()
                elif event.key == pygame.K_SPACE:
                    self.clear()
                elif event.key == pygame.K_ESCAPE:
                    self.over = True
                for n, defined_color in enumerate(defined_colors):
                    pygame_keypad_key = getattr(pygame, 'K_KP' + str(n + 1))
                    pygame_key = getattr(pygame, 'K_' + str(n + 1))

                    if event.key == pygame_key or event.key == pygame_keypad_key: #1-9 your selected color will be highlighted at top of screen
                        print(defined_color)
                        self.draw_color = defined_colors[defined_color]
                        # self.history.append({
                        #     'type': 'color',
                        #     'color': self.draw_color
                        # })
                        break
    def run(self):
        while not self.over:
            time.sleep(0.01)
            self.handle_events()
            self.refresh()
    def clear(self):
        self.history.append({
            'type': 'clear',
        })
        self.drawing.fill((50, 40, 200))
    def draw_history(self):
        for history_event in self.history:
            if history_event['type'] == 'size':
                self.draw_size = history_event['size']
            elif history_event['type'] == 'color':
                self.draw_color = history_event['color']
            elif history_event['type'] == 'polygon':
                polygon = list(history_event['polygon'])
                if len(polygon):
                    dot1 = polygon.pop(0)
                    while len(polygon):
                        dot2 = polygon.pop(0)
                        pygame.draw.line(self.drawing, history_event['color'], dot1, dot2, history_event['size']) #history_event['size'] ?
                        dot1 = dot2
            elif history_event['type'] == 'clear':
                self.drawing.fill((50, 40, 200))



def main ():
    ''
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

    app = PygameClient('localhost', 15132136) # TODO change that
    app.run()
    return

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
