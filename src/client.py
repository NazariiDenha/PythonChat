#!/usr/bin/env python3

import socket
import argparse
import tkinter
from threading import Thread
from tkinter import messagebox



def message_handler(msg):
    if msg.startswith("HAS LEFT THE CHAT "):
        nname = msg[18:]
        names = user_list.get(0, tkinter.END)
        pos = -1
        for i in range(len(names)):
            if names[i] == nname:
                pos = i
                break
        if pos != -1:
            if len(user_list.curselection()) > 0 and user_list.curselection()[0] == pos:
                user_list.activate(0)
            user_list.delete(pos)
            print(user_list.curselection())
        return
    if msg.startswith("HAS JOINED THE CHAT "):
        if msg[20:] != name:
            user_list.insert(tkinter.END, msg[20:])
        return
    msg_list.insert(tkinter.END, msg)
    msg_list.yview_moveto(1)


def receive():
    while True:
        try:
            msg = sock.recv(CHUNK).decode("utf8")
            while len(msg) > 0:
                pos = msg.find(";;")
                top.after(0, message_handler, msg[:pos])
                msg = msg[pos + 2:]
        except OSError:
            break

def socksend(msg):
    try:
        sock.send(msg)
    except Exception as e:
        print(e)

def send(event = None):
    try:
        global name_setted
        global name
        msg = my_msg.get()
        if len(msg) == 0:
            messagebox.showinfo("Message", "You can not send empty message")
            return
        if not name_setted:
            name_setted = True
            name = msg
            my_msg.set("")

            socksend(bytes(msg, "utf8"))
            return
        print(name + " => " + user_list.get(tkinter.ACTIVE) + ": " + msg)
        my_msg.set("")
        socksend(bytes(name + " => " + user_list.get(tkinter.ACTIVE) + ": " + msg, "utf8"))
    except Exception as e:
        print(e)

def on_closing(event = None):
    print("Closing...")
    socksend(bytes("exit", "utf8"))
    try:
        sock.close()
    except Exception as e:
        print(e)
    top.quit()

if __name__ == "__main__":
    CHUNK = 1024

    name = ""
    name_setted = False

    HOST = 'localhost'
    PORT = 50007
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default=HOST)
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()

    top = tkinter.Tk()
    #top.geometry("800x600")
    top.title("Chat")
    messages_frame = tkinter.Frame(top)
    my_msg = tkinter.StringVar()

    history_frame = tkinter.Frame(messages_frame, height = 400)
    scrollbar = tkinter.Scrollbar(history_frame)
    msg_list = tkinter.Listbox(history_frame, height = 29, width = 90, yscrollcommand = scrollbar.set)
    scrollbar.config(command = msg_list.yview)
    scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
    msg_list.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
    history_frame.pack()



    entry_field = tkinter.Entry(messages_frame, textvariable=my_msg, width = 93)
    entry_field.bind("<Return>", send)
    entry_field.pack()
    send_button = tkinter.Button(messages_frame, text = "Send", command = send, width = 79, height = 7)
    send_button.pack()

    messages_frame.pack(side = tkinter.LEFT, anchor = "sw")

    user_frame = tkinter.Frame(top)
    user_list = tkinter.Listbox(user_frame, height = 30, width = 54, selectmode = tkinter.SINGLE, exportselection = tkinter.FALSE)
    exit_button = tkinter.Button(user_frame, text = "Exit", command = on_closing, width = 47, height = 7)
    user_frame.pack(side = tkinter.RIGHT)
    user_list.insert(tkinter.END, "ALL")
    user_list.activate(0)
    user_list.pack()
    exit_button.pack()


    top.protocol("WM_DELETE_WINDOW", on_closing)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.host, args.port))
    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()
