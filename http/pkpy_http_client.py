import libhv
import json
from time import time

url = 'http://127.0.0.1:8080'

requested_time = 0
http_data = {}

client = libhv.HttpClient()

with open('http_1kb.txt', 'r') as f:
    line = f.read()
    http_data['data_recv'] = line

def client_get_server() -> None:
    response = client.post(url, json=http_data, timeout=1)
    while not response.completed:
        pass
    assert response.status_code == 200
    serv_ret = response.json().values()
    serv_ret_iter = iter(serv_ret)
    assert next(serv_ret_iter) == http_data['data_recv']

start_time = time()
while 1:
    client_get_server()
    requested_time += 1
    stop_time = time()
    if stop_time - start_time >= 1:
        print(f'{requested_time}')
        break

