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


class O:''

def main ():
    ''

    # G is just a storage object: its goal is to easily make
    # variables accessible (readable and writeable) in functions
    G = O()
    G.x = 0
    G.y = 0
    G.last_btn_move = 0
    G.lines = []
    window = tkinter.Tk()
    canvas = tkinter.Canvas(window, width=500, height=300, background='#ffe')
    #people_list = tkinter.Listbox(window)
    chat_display = tkinter.Text(window, state='disabled', width=50)
    chat_line_var = tkinter.StringVar()
    chat_line = tkinter.Entry(window, textvariable=chat_line_var)

    canvas.pack(      side='left',   fill='both', expand=True)
    chat_line.pack(   side='bottom', fill='x',    expand=True)
    chat_display.pack(side='bottom', fill='both', expand=True)

    def cb_btn_press(event):
        print('button 1 pressed', event.x, event.y)
        canvas.focus_set()
        G.x = event.x
        G.y = event.y
    def cb_btn_move(event):
        # throttling this (to avoid stressing network)
        distance = ((event.x - G.x) ** 2 + (event.y - G.y) **2)**0.5
        if time.time() - G.last_btn_move < 0.06 and distance < 20:
            return
        G.last_btn_move = time.time()
        print('button 1 moved', event.x, event.y)
        l = canvas.create_line(G.x, G.y, event.x, event.y, fill='black')
        G.lines.append(l)
        G.x = event.x
        G.y = event.y
    def cb_btn_release(event):
        print('button 1 released', event.x, event.y)
        G.x = event.x
        G.y = event.y
    def cb_keypress(event):
        if event.char == ' ': # space key
            while G.lines:
                canvas.delete(G.lines.pop())
        print(event.char)
    def send_msg(event):
        #chat_line
        x = chat_line_var.get()
        chat_line_var.set('hello')
        print(x)
    canvas.bind('<Button-1>', cb_btn_press)
    canvas.bind('<B1-Motion>', cb_btn_move)
    canvas.bind('<ButtonRelease-1>', cb_btn_release)
    canvas.bind('<Key>', cb_keypress)
    chat_line.bind('<Return>', send_msg)
    window.mainloop()

if __name__ == "__main__":
    try: main ()
    except KeyboardInterrupt: print("\033[31mLeaving: User typed Ctrl+C.\033[0m")
