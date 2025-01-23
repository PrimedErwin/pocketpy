import libhv
import json
from time import time

ws_url = 'ws://127.0.0.1:8080/ws'
ws_data: str

requested_time = 0

with open('ws_100b.txt', 'r') as f:
    line = f.read()
    ws_data = line

def client_ws(ws: libhv.WebSocketClient) -> None:
    passed = wrong = 0
    ws.send(ws_data)
    msg = ws.recv()
    while msg is None:
        msg = ws.recv()
    # print(requested_time, msg)
    if msg[1] is not None:
        assert msg[1] == ws_data

    

client = libhv.WebSocketClient()
client.open(ws_url)
start_time = time()
passed = wrong = 0
while 1:
    client_ws(client)
    requested_time += 1
    stop_time = time()
    if stop_time - start_time >= 1:
        print(f'{requested_time}')
        break
