import libhv
from time import time

url = 'http://127.0.0.1:8080'

requested_time = 0

client = libhv.HttpClient()

def client_get_server() -> None:
    response = client.get(url, timeout=1)
    while not response.completed:
        pass
    assert response.status_code == 200

start_time = time()
while 1:
    client_get_server()
    requested_time += 1
    stop_time = time()
    if stop_time - start_time >= 1:
        print(f'{requested_time}')
        break

