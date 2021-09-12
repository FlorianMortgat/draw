#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
© Flo M, Scooter, 2021
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
G.nick = 'nameless'
G.IP = ''

SEPARATOR = b'\n'
# Scooter was here :D
defined_colors = OrderedDict([
    ('red', (255, 0, 0)),
    ('orange', (255, 70, 0)),
    ('yellow', (255, 255, 0)),
    ('green', (0, 255, 0)),
    ('blue', (0, 0, 255)),
    ('dark_blue', (0, 0, 150)),
    ('purple', (255, 0, 255)),
    ('white', (255, 255, 255)),
    ('black', (0, 0, 0)),
])


# basic colors in rgb

def get_color(i):
    return '#{:02x}{:02x}{:02x}'.format(
        0,
        (30 + i * 60) % 255,
        (15 + i * 90) % 255
    )


class Words():
    def __init__(self, words):
        print('')


class PygameClient:
    def __init__(self, host, port):
        self.window = pygame.display.set_mode((840, 480))
        pygame.display.set_caption('pygame client')
        pygame.init()
        self.textbox_img = pygame.image.load(sys.path[0] + '/images/textbox.png')
        self.drawing = pygame.Surface((640, 480))
        self.chat = pygame.Surface((200, 480))
        self.chat.fill((0, 40, 100))
        self.MAX_DRAW_SIZE = 20
        self.clock = pygame.time.Clock()
        self.over = False
        self.is_drawing = False
        self.history = []
        self.thickness_history = []
        self.polygon = []
        self.bg_color = defined_colors['white']
        self.draw_size = 4
        self.draw_color = defined_colors['red']
        self.help_text_collide = False
        (self.help_surface_width, self.help_surface_height) = (4, 1)
        self.help_surface_accel = 2
        self.help_surface_accel2 = 2
        self.help_surface_rect = pygame.Rect(0, 0, 540, 340)
        self.help_surface_rect.x = -100
        self.help_surface_rect.y = -100
        self.help_var = True
        self.last_motion = time.time()
        self.chat_text = ''
        self.chat_selected = False
        self.inp_text = ''
        self.inp_text2 = ''

        self.history.append({
            'type': 'color',
            'color': self.draw_color
        })
        self.history.append({
            'type': 'size',
            'size': 4
        })
        self.font = pygame.font.Font(None, 40)
        self.font2 = pygame.font.Font(None, 20)
        self.text = self.font2.render(self.chat_text, True, (50, 50, 50))
        self.chat_surface = pygame.Surface((200, 30))
        # self.chat_surface.blit(self.textbox_img, (0, 0))
        # self.chat_surface.blit(self.chat_text, (0, 0))
        self.chat_text = self.font2.render('', True, (0, 0, 0))
        self.chat_text2 = self.font2.render('', True, (0, 0, 0))
        self.help_text = self.font.render('Help', False, (200, 200, 200))
        self.load_text()
        self.help_text_rect = self.help_text.get_rect()
        self.help_text_rect = self.help_text_rect.move(550, 20)
        self.max_chat_num = 0
        self.max_chat_color1 = 0
        self.max_chat_color2 = 255
        self.max_chat_text = self.font2.render(str(self.max_chat_num) + '/50', True,
                                               ((self.max_chat_color1, self.max_chat_color2, 0)))
        self.textboxs = {}
        self.chat_boxs = {}
        self.chat_box_num = 0
        self.textbox_num = 0
        self.clear()

    def refresh(self):
        self.clock.tick(60)  # 60 fps max
        self.window.blit(self.drawing, (0, 0))
        self.window.blit(self.chat, (640, 0))
        draw_thickness_text = self.font.render('Draw Thickness: %d' % self.draw_size, False, ((20, 40, 100)))
        self.window.blit(draw_thickness_text, (20, 20))

        pygame.draw.rect(self.window, defined_colors['black'], pygame.Rect(296, 15, (len(defined_colors) * 24) + 5, 30))
        for n, color in enumerate(defined_colors):
            if self.draw_color == defined_colors[color]:
                pygame.draw.rect(self.window, defined_colors['white'],
                                 pygame.Rect((300 - 2 + n * 24, 20 - 2), (20 + 4, 20 + 4)))
            pygame.draw.rect(self.window, (defined_colors[color]), pygame.Rect((300 + n * 24, 20), (20, 20)))
        if self.help_text_rect.collidepoint(pygame.mouse.get_pos()):
            self.help_text = self.font.render('Help', False, (200, 255, 200))
        else:
            self.help_text = self.font.render('Help', False, (200, 200, 200))
        self.window.blit(self.help_text, (550, 20))

        # stuff for thehelp window
        # self.help_surface = pygame.Surface((self.help_surface_width, self.help_surface_height))
        # self.help_surface.fill((200, 200, 200))
        # pygame.draw.rect(self.help_surface, ((180, 180, 180)), pygame.Rect((0, 0), (540, 50)))
        # self.exit_help_button = pygame.draw.rect(self.help_surface, ((200, 0, 0)), pygame.Rect((505, 8), (30, 30)))
        self.window.blit(self.help_surface, (self.help_surface_rect.x, self.help_surface_rect.y),
                         pygame.Rect(0, 0, self.help_surface_width, self.help_surface_height))

        if not self.chat_selected:
            self.chat_box = pygame.draw.rect(self.window, (150, 150, 150), (640, 420, 200, 60))
        elif self.chat_selected:
            self.chat_box = pygame.draw.rect(self.window, (150, 255, 150), (640, 420, 200, 60))
        pygame.draw.rect(self.window, ((100, 100, 100)), (640, 420, 200, 5))

        self.max_chat_text = self.font2.render(str(self.max_chat_num) + '/50', True,
                                               ((self.max_chat_color1, self.max_chat_color2, 0)))

        self.window.blit(self.max_chat_text, (800, 410))
        self.window.blit(self.chat_text, (650, 435))
        self.window.blit(self.chat_text2, (650, 450))

        for n, boxes in enumerate(self.chat_boxs):
            self.window.blit(self.chat_boxs[1 + n], (640, 0 + n * 30))

        pygame.display.update()

    def load_text(self):
        self.help_surface = pygame.Surface((540, 340))
        self.help_surface.fill((200, 200, 200))
        pygame.draw.rect(self.help_surface, ((180, 180, 180)), pygame.Rect((0, 0), (540, 50)))
        self.exit_help_button = pygame.draw.rect(self.help_surface, ((200, 0, 0)), pygame.Rect((505, 8), (30, 30)))
        self.text_lines = ['1-9 number keys select your color', 'left click to draw',
                           'scroll wheel to change size',
                           'spacebar to clear the window',
                           'CTRL+Z to undo your last action', 'undoing may have the occasional bug']
        for n, text in enumerate(self.text_lines):
            self.help_surface.blit(self.font.render(text, False, (0, 0, 0)), (20, 60 + n * 40))
        # self.window.blit(self.help_surface, (self.help_surface_rect.x, self.help_surface_rect.y))

    def on_chat(self, who, text1, text2):  # who is whos sending the message (unused for now)
        self.textbox_num += 1
        self.chat_box_num += 1
        self.textboxs[self.textbox_num] = 400
        self.chat_boxs[self.chat_box_num] = self.textbox_img
        send_line1 = self.font2.render(str(text1), True, (0, 255, 255))
        if text2 != '':
            send_line2 = self.font2.render(str(text2), True, (0, 255, 255))

        self.chat_boxs[self.chat_box_num].blit(send_line1, (0, 0))
        if text2 != '':
            self.chat_boxs[self.chat_box_num].blit(send_line2, (0, 15))

    def help(self, bool):
        var = True
        if bool == False:
            (self.help_surface_width, self.help_surface_height) = (540, 340)
            # self.help_surface = pygame.Surface((self.help_surface_width, self.help_surface_height))
            self.help_surface_accel = 2
            self.help_surface_accel2 = 2
            self.help_surface_rect = self.help_surface.get_rect()
            self.help_surface_rect.x = 59
            self.help_surface_rect.y = 35
            while var:
                # print(bool)
                self.refresh()
                self.handle_events()
                # print(self.help_surface_accel, self.help_surface_width, self.help_surface_height, self.help_surface_rect.y)
                if self.help_surface_accel2 < 10:
                    self.help_surface_accel2 += 0.05
                    self.help_surface_accel = int(self.help_surface_accel2)
                if self.help_surface_width > 4:
                    if not self.help_surface_width - self.help_surface_accel < 4:
                        self.help_surface_width -= self.help_surface_accel
                    elif self.help_surface_width - self.help_surface_accel < 4:
                        self.help_surface_width = 4
                    if not self.help_surface_rect.x - self.help_surface_accel < 4:
                        self.help_surface_rect.x += self.help_surface_accel / 1.75
                    elif self.help_surface_rect.x - self.help_surface_accel < 4:
                        self.help_surface_rect.x = 4
                if self.help_surface_width <= 4 and self.help_surface_height > 2:
                    if not self.help_surface_height - self.help_surface_accel < 1:
                        self.help_surface_height -= self.help_surface_accel
                    if self.help_surface_height - self.help_surface_accel < 1:
                        self.help_surface_height = 1
                    self.help_surface_rect.y += (self.help_surface_accel / 2)
                elif self.help_surface_width <= 4 and self.help_surface_height <= 2:
                    self.help_surface_accel = 2
                    self.help_var = True
                    (self.help_surface_rect.x, self.help_surface_rect.y) = (-100, -100)
                    var = False

        if bool == True:
            (self.help_surface_width, self.help_surface_height) = (4, 1)
            # self.help_surface = pygame.Surface((self.help_surface_width, self.help_surface_height))
            self.help_surface_accel = 2
            self.help_surface_accel2 = 2
            self.help_surface_rect = self.help_surface.get_rect()
            self.help_surface_rect.x = 310
            self.help_surface_rect.y = 209
            while var:
                # print(bool)
                self.refresh()
                self.handle_events()
                # print(self.help_surface_accel, self.help_surface_width, self.help_surface_height, self.help_surface_rect.y)
                if self.help_surface_accel2 < 20:
                    self.help_surface_accel2 += 0.1
                    self.help_surface_accel = int(self.help_surface_accel2)
                if self.help_surface_width < 540:
                    if not self.help_surface_width + self.help_surface_accel > 540:
                        self.help_surface_width += self.help_surface_accel
                    elif self.help_surface_width + self.help_surface_accel > 540:
                        self.help_surface_width = 540
                    if self.help_surface_rect.x - self.help_surface_accel > 50:
                        self.help_surface_rect.x -= self.help_surface_accel / 2.5
                    elif self.help_surface_rect.x - self.help_surface_accel > 50:
                        self.help_surface_rect.x = 50
                if self.help_surface_width >= 540 and self.help_surface_height < 340:
                    if not self.help_surface_height + self.help_surface_accel > 340:
                        self.help_surface_height += self.help_surface_accel
                    if self.help_surface_height + self.help_surface_accel > 340:
                        self.help_surface_height = 340
                    self.help_surface_rect.y -= (self.help_surface_accel / 2)
                elif self.help_surface_width >= 540 and self.help_surface_height >= 340:
                    self.help_surface_accel = 2
                    self.help_var = False
                    var = False

    def handle_events(self):
        keys = pygame.key.get_pressed()  # the better way to get key presses
        chat_selected_var = True  # var for the toggling chat modes
        for event in pygame.event.get():
            if event.type == QUIT:
                self.over = True
                pygame.quit()
                exit()
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
                    if self.help_text_rect.collidepoint(event.pos) and self.help_var == True:
                        self.help_var = False
                        self.help(True)
                        hitbutton = True
                    if self.exit_help_button.move(60, 30).collidepoint(event.pos) and self.help_var == False:
                        self.help_var = True
                        self.help(False)
                        hitbutton = True
                    if self.chat_box.collidepoint(event.pos):
                        if not self.chat_selected:
                            self.chat_selected = True
                            chat_selected_var = False
                        if self.chat_selected and chat_selected_var:
                            self.chat_selected = False
                        if not chat_selected_var:
                            chat_selected_var = True
                    if not hitbutton:
                        self.is_drawing = True
                    # self.polygon.append((event.x, event.y))
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.is_drawing:
                        self.is_drawing = False
                        # pygame.draw.circle(self.window, ((255,0,0)), event.pos, self.draw_size // 2) #4 wide, because 2 both ways
                        self.history.append({
                            'type': 'polygon',
                            'polygon': self.polygon,
                            'size': self.draw_size,
                            'color': self.draw_color,
                        })
                        # self.history.append({
                        #     'type': 'size',
                        #     'size': self.draw_size
                        # })
                        self.polygon = []
                elif event.button == 4:  # mouse wheel up/down (button 4/5)
                    self.draw_size += 1
                    if self.draw_size > self.MAX_DRAW_SIZE:
                        self.draw_size -= 1
                elif event.button == 5:
                    self.draw_size -= 1
                    if self.draw_size < 1:
                        self.draw_size = 1
                    # self.polygon.append((event.x, event.y))
            elif event.type == MOUSEMOTION:
                if time.time() < self.last_motion + 0.01:
                    # throttling motions to avoid sending too much data over the network
                    return
                self.last_motion = time.time()
                if self.is_drawing:
                    self.polygon.append(event.pos)
                    # pygame.draw.circle(self.window, ((255, 0, 0)), event.pos, self.draw_size // 2)
                    if len(self.polygon) >= 2:
                        pygame.draw.line(self.drawing, self.draw_color, self.polygon[-2], self.polygon[-1],
                                         self.draw_size)
                    # if event.pos.collidepoint(self.help_text):
            elif event.type == KEYUP:
                if event.key == pygame.K_z and (
                        keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and not self.chat_selected:
                    self.polygon = []
                    if len(self.history) > 1: self.history.pop()
                    self.draw_history()
                elif event.key == pygame.K_SPACE:
                    if not self.chat_selected:
                        self.clear()
                elif event.key == pygame.K_ESCAPE:
                    self.over = True
                for n, defined_color in enumerate(defined_colors):
                    pygame_keypad_key = getattr(pygame, 'K_KP' + str(n + 1))
                    pygame_key = getattr(pygame, 'K_' + str(n + 1))

                    if event.key == pygame_key and not self.chat_selected or event.key == pygame_keypad_key and not self.chat_selected:  # 1-9 your selected color will be highlighted at top of screen
                        self.draw_color = defined_colors[defined_color]
                        # self.history.append({
                        #     'type': 'color',
                        #     'color': self.draw_color
                        # })
                        break
            if event.type == KEYDOWN:
                if self.chat_selected == True:
                    if event.key == pygame.K_BACKSPACE:
                        if len(self.inp_text) > 0 and not len(self.inp_text2) >= 1:
                            self.inp_text = self.inp_text[:-1]
                            self.max_chat_num -= 1
                            self.max_chat_color1 -= 4
                            self.max_chat_color2 += 4
                        elif len(self.inp_text) > 0 and len(self.inp_text2) >= 1:
                            self.inp_text2 = self.inp_text2[:-1]
                            self.max_chat_num -= 1
                            self.max_chat_color1 -= 4
                            self.max_chat_color2 += 4

                    elif event.key == pygame.K_RETURN:
                        self.chat_selected = False
                        self.max_chat_num = 0
                        self.max_chat_color1 = 0
                        self.max_chat_color2 = 255
                        if len(self.inp_text) < 1:
                            self.inp_text = ''
                        if len(self.inp_text2) < 1:
                            self.inp_text2 = ''
                        if len(self.inp_text) > 0:
                            self.on_chat("(you)", self.inp_text, self.inp_text2)
                        self.inp_text = ''
                        self.inp_text2 = ''
                    else:
                        if len(self.inp_text) + len(self.inp_text2) < 50:
                            self.max_chat_num += 1
                            self.max_chat_color1 += 4
                            self.max_chat_color2 -= 4
                        if len(self.inp_text) < 25:
                            self.inp_text += event.unicode
                        elif len(self.inp_text) >= 25:
                            if len(self.inp_text2) < 25:
                                self.inp_text2 += event.unicode
                    self.chat_text = self.font2.render(self.inp_text, True, (0, 0, 0))
                    self.chat_text2 = self.font2.render(self.inp_text2, True, (0, 0, 0))

    def run(self):
        while not self.over:
            time.sleep(0.01)
            self.handle_events()
            self.refresh()

    def clear(self):
        self.history.append({
            'type': 'clear',
        })
        self.drawing.fill(self.bg_color)

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
                        pygame.draw.line(self.drawing, history_event['color'], dot1, dot2,
                                         history_event['size'])  # history_event['size'] ?
                        dot1 = dot2
            elif history_event['type'] == 'clear':
                self.drawing.fill(self.bg_color)


def main():
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

    app = PygameClient('localhost', 15132136)  # TODO change that
    app.run()
    return

    def cb_btn_press(event):
        canvas.focus_set()
        G.x = event.x
        G.y = event.y
        G.out_buf = b'L:%d,%d' % (G.x, G.y)

    def cb_btn_move(event):
        # throttling this (to avoid stressing network)
        distance = ((event.x - G.x) ** 2 + (event.y - G.y) ** 2) ** 0.5
        if time.time() - G.last_btn_move < 0.06 and distance < 20:
            return
        G.last_btn_move = time.time()
        l = canvas.create_line(G.x, G.y, event.x, event.y, fill='red', width=1)
        G.lines.append((-1, l))
        G.out_buf += b'-%d,%d' % (event.x, event.y)
        if len(G.out_buf) > 40:
            G.socket.send(G.out_buf)
            G.out_buf = b''
        G.x = event.x
        G.y = event.y

    def cb_btn_release(event):
        G.out_buf += b'-%d,%d\n' % (event.x, event.y)
        G.socket.send(G.out_buf)
        G.out_buf = b''
        G.x = event.x
        G.y = event.y

    def cb_keypress(event):
        if event.char == ' ':  # space key
            G.socket.send(b'CLEAR\n')
        print(event.char)

    def send_msg(event):
        # chat_line
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
            for x, y in re.findall(b'(\\d+),(\\d+)', command):
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
    try:
        main()
    except KeyboardInterrupt:
        print("\033[31mLeaving: User typed Ctrl+C.\033[0m")
