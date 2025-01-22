import websockets
from time import time

import websockets.sync
import websockets.sync.client
import websockets.sync.connection

ws_url = 'ws://127.0.0.1:8080/ws'
fixed_data = 'Test message from client'

requested_time = 0

# def websocket client
def client_ws(ws: websockets.sync.connection.Connection) -> None:
    ws.send(fixed_data)
    msg = ws.recv()
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
    