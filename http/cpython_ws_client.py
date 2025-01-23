import websockets
from time import time

import websockets.sync
import websockets.sync.client
import websockets.sync.connection

ws_url = 'ws://127.0.0.1:8080/ws'
ws_data: str

requested_time = 0

with open('ws_100b.txt', 'r', encoding='utf-8') as f:
    line = f.readline()
    ws_data = line

# def websocket client
def client_ws(ws: websockets.sync.connection.Connection) -> None:
    ws.send(ws_data)
    msg = ws.recv()
    assert msg == ws_data
    # print(msg)

# websocket connect to server
with websockets.sync.client.connect(ws_url, close_timeout=1) as ws:
    start_time = time()
    while 1:
        client_ws(ws)
        requested_time += 1
        stop_time = time()
        if stop_time - start_time >= 1:
            print(f'{requested_time}')
            break
    