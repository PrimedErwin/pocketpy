import urllib3
import json
from time import time

url = 'http://127.0.0.1:8080'

requested_time = 0
http_data = {}

client = urllib3.PoolManager()

with open('http_1kb.txt', 'r', encoding='utf-8') as f:
    line = f.readline()
    http_data['data_recv'] = line

# def http client->server funcs
def client_get_server() -> None:
    response = client.request('POST', url, json=http_data)
    assert response.status == 200
    serv_ret = json.loads(response.data.decode()).values()
    serv_ret_iter = iter(serv_ret)
    assert next(serv_ret_iter) == http_data['data_recv']

# http connect to server
start_time = time()
while 1:
    client_get_server()
    requested_time += 1
    stop_time = time()
    if stop_time - start_time >= 1:
        print(f'{requested_time}')
        break


    