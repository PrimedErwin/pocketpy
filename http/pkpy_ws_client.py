import libhv
from time import time

ws_url = 'ws://127.0.0.1:8080/ws'
fixed_data = 'Test message from client'

requested_time = 0

def client_ws(ws: libhv.WebSocketClient) -> None:
    ws.send(fixed_data)
    msg = ws.recv()

client = libhv.WebSocketClient()
client.open(ws_url)
start_time = time()
while 1:
    client_ws(client)
    requested_time += 1
    stop_time = time()
    if stop_time - start_time >= 1:
        print(f'{requested_time}')
        break
