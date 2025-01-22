import requests
import websockets
from time import time

import websockets.sync
import websockets.sync.client
import websockets.sync.connection

url = 'http://127.0.0.1:8080'
ws_url = 'ws://127.0.0.1:8080/ws'
data = 'Test message from client'

requested_time = 0

# def http client->server funcs
def clear_record():
    requested_time = 0

def client_get_server(data=data):
    try:
        response = requests.get(url=url, timeout=1)
        assert response.status_code == 200
    except AssertionError as e:
        print(f'Unexpected error on http client:{e}')

# def websocket client
def client_ws(ws: websockets.sync.connection.Connection):
    ws.send(data)
    msg = ws.recv()
    # print(msg)

# http connect to server
start_time = time()
while 1:
    client_get_server()
    requested_time += 1
    stop_time = time()
    if stop_time - start_time >= 1:
        print(f'Client -> Server, HTTP = {requested_time} times in {stop_time-start_time} second')
        break

# websocket connect to server
with websockets.sync.client.connect(ws_url) as ws:
    clear_record()
    start_time = time()
    while 1:
        client_ws(ws)
        requested_time += 1
        stop_time = time()
        if stop_time - start_time >= 1:
            print(f'Client -> Server, WebSocket = {requested_time} times in {stop_time-start_time} second')
            break

    