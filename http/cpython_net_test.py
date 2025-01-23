import subprocess
import time

#green and blue
green = (0, 222, 0)
blue = (173, 216, 230)

# run a process using shell command silently
def cmd_silent(command: str) -> subprocess.Popen:
    p = subprocess.Popen(command, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, encoding='utf-8')
    return p

# run a process using shell command
def cmd(command: str) -> subprocess.Popen:
    p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    return p

def ansi_fg(color: tuple[int, int, int], text: str):
    r, g, b = color
    return f'\x1b[38;2;{r};{g};{b}m{text}\x1b[0m'

client_list: list[subprocess.Popen] = []

def cpython_http_sync() -> int:
    cpython_http_client = cmd('python .\\cpython_http_client.py')
    client_list.append(cpython_http_client)
    outs, _ = cpython_http_client.communicate()
    return outs

def pkpy_http_sync() -> int:
    pkpy_http_client = cmd('..\\main.exe .\\pkpy_http_client.py')
    client_list.append(pkpy_http_client)
    outs, _ = pkpy_http_client.communicate()
    return outs

def cpython_ws_sync() -> int:
    cpython_ws_client = cmd('python .\\cpython_ws_client.py')
    client_list.append(cpython_ws_client)
    outs, _ = cpython_ws_client.communicate()
    return outs

def pkpy_ws_sync() -> int:
    pkpy_ws_client = cmd('..\\main.exe .\\pkpy_ws_client.py')
    client_list.append(pkpy_ws_client)
    outs, _ = pkpy_ws_client.communicate()
    return outs

def cpython_http_concurrent(thread_num: int) -> list[int]:
    ret_list: list[int] = []
    concurrent_list: list[subprocess.Popen] = []
    for i in range(thread_num):
        concurrent_list.append(cmd('python .\\cpython_http_client.py'))
    for i in range(thread_num):
        outs, _ = concurrent_list[i].communicate()
        ret_list.append(outs)
    return ret_list

def pkpy_http_concurrent(thread_num: int) -> list[int]:
    ret_list: list[int] = []
    concurrent_list: list[subprocess.Popen] = []
    for i in range(thread_num):
        concurrent_list.append(cmd('..\\main.exe .\\pkpy_http_client.py'))
    for i in range(thread_num):
        outs, _ = concurrent_list[i].communicate()
        ret_list.append(outs)
    return ret_list

def cpython_ws_concurrent(thread_num: int) -> list[int]:
    ret_list: list[int] = []
    concurrent_list: list[subprocess.Popen] = []
    for i in range(thread_num):
        concurrent_list.append(cmd('python .\\cpython_ws_client.py'))
    for i in range(thread_num):
        outs, _ = concurrent_list[i].communicate()
        ret_list.append(outs)
    return ret_list

def pkpy_ws_concurrent(thread_num: int) -> list[int]:
    ret_list: list[int] = []
    concurrent_list: list[subprocess.Popen] = []
    for i in range(thread_num):
        concurrent_list.append(cmd('..\\main.exe .\\pkpy_ws_client.py'))
    for i in range(thread_num):
        outs, _ = concurrent_list[i].communicate()
        ret_list.append(outs)
    return ret_list


# start cpython server
print('Starting server...', '#'*30, sep='\n')
print('SERVER MODE: ', ansi_fg(blue, 'CPYTHON'))
cpython_serv = cmd_silent('python .\\cpython_server.py')

outs = cpython_http_sync()
print(ansi_fg(blue, 'HTTP  CPYTHON'), 'client->server 1 sec: ', ansi_fg(green, outs))

outs = pkpy_http_sync()
print(ansi_fg(blue, 'HTTP  PKPY'), 'client->server 1 sec: ', ansi_fg(green, outs))

outs = cpython_ws_sync()
print(ansi_fg(blue, 'WebSocket  CPYTHON'), 'client->server 1 sec: ', ansi_fg(green, outs))

outs = pkpy_ws_sync()
print(ansi_fg(blue, 'WebSocket PKPY'), 'client->server 1 sec: ', ansi_fg(green, outs))

print(cpython_http_concurrent(4))
print(pkpy_http_concurrent(4))
print(cpython_ws_concurrent(4))
print(pkpy_ws_concurrent(4))

print('Waiting clients shutting down...\n')
while client_list:
    for i in client_list[:]:
        if i.poll() == 0:
            client_list.remove(i)

cmd('taskkill /pid '+str(cpython_serv.pid)+' /F')

assert len(client_list) == 0

time.sleep(3)

# start pkpy server
print('Starting server...', '#'*30, sep='\n')
print('SERVER MODE: ', ansi_fg(blue, 'PKPY'))
pkpy_serv = cmd_silent('..\\main.exe .\\pkpy_server.py')

outs = cpython_http_sync()
print(ansi_fg(blue, 'HTTP  CPYTHON'), 'client->server 1 sec: ', ansi_fg(green, outs))

outs = pkpy_http_sync()
print(ansi_fg(blue, 'HTTP  PKPY'), 'client->server 1 sec: ', ansi_fg(green, outs))

outs = cpython_ws_sync()
print(ansi_fg(blue, 'WebSocket  CPYTHON'), 'client->server 1 sec: ', ansi_fg(green, outs))

outs = pkpy_ws_sync()
print(ansi_fg(blue, 'WebSocket PKPY'), 'client->server 1 sec: ', ansi_fg(green, outs))

print(cpython_http_concurrent(4))
print(pkpy_http_concurrent(4))
print(cpython_ws_concurrent(4))
print(pkpy_ws_concurrent(4))

print('Waiting clients shutting down...')
while client_list:
    for i in client_list[:]:
        if i.poll() == 0:
            client_list.remove(i)

cmd('taskkill /pid '+str(pkpy_serv.pid)+' /F')

assert len(client_list) == 0

print(ansi_fg(green, 'TEST PASS'))