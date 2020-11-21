import socket
from threading import Thread
from threading import  Lock
import argparse

CHUNK = 1024

HOST = ''
PORT = 50007
parser = argparse.ArgumentParser()
parser.add_argument('--host', default=HOST)
parser.add_argument('--port', type=int, default=PORT)
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((args.host, args.port))

clients = {}
clients_lock = Lock()

def sendall(msg, pref, dst = "ALL"):
    with clients_lock:
        for client in clients:
            if dst == "ALL" or dst == clients[client]:
                try:
                    client.send(bytes(pref, "utf8") + msg + bytes(";;", "utf8"))
                except Exception as e:
                    print(e)

def sendone(msg, pref, client):
    try:
        client.send(bytes(pref, "utf8") + msg + bytes(";;", "utf8"))
    except Exception as e:
        print(e)

def client_handler(client):
    name = client.recv(CHUNK).decode("utf8")
    if name == "exit":
        try:
            client.close()
        except Exception as e:
            print(e)
        return
    with clients_lock:
        for user in clients:
            sendone(bytes(clients[user], "utf8"), "HAS JOINED THE CHAT ", client)
    with clients_lock:
        clients[client] = name

    sendall(bytes(name, "utf8"), "HAS JOINED THE CHAT ")
    print(name)
    try:
        while True:
            msg = client.recv(CHUNK)
            if msg != bytes("exit", "utf8"):
                msg = msg.decode("utf8")
                pos1 = msg.find(" => ")
                pos2 = msg.find(":")
                dst = msg[pos1 + 4:pos2]
                print(msg)
                print(dst)
                sendall(bytes(msg, "utf8"), "", dst)
                if dst != "ALL":
                    sendone(bytes(msg, "utf8"), "", client)
            else:
                print("time to exit")
                client.send(bytes("exit", "utf8") + bytes(";;", "utf8"))
                client.close()
                with clients_lock:
                    if clients.get(client) is not None:
                        clients.pop(client)
                sendall(bytes(name, "utf8"), "HAS LEFT THE CHAT ")
                print("bye bye " + name)
                break
    except Exception as e:
        print(e)
        with clients_lock:
            if clients.get(client) is not None:
                clients.pop(client)
        print("byr bye " + name)
        sendall(bytes(name, "utf8"), "HAS LEFT THE CHAT ")

def accept_connections():
    while True:
        conn, addr = sock.accept()
        print(str(conn), str(addr), "connected")
        conn.send(bytes("Hello! Please, send your nickname in the first message", "utf8") + bytes(";;", "utf8"))
        Thread(target=client_handler, args = (conn, )).start()

if __name__ == "__main__":
    sock.listen(5)
    print("Waiting for connections")
    accept_thread = Thread(target=accept_connections)
    accept_thread.start()
    accept_thread.join()
    sock.close()
