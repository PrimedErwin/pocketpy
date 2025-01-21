try:
    import libhv
except ImportError:
    print('libhv module is not enabled, please check CmakeLists.')
    exit()
import time
INTERACTIVE_TEST = True

remote_host = '127.0.0.1'
remote_port = 8080
url = 'http://' + remote_host + ':' + str(remote_port)
text_header = {"Connection": "keep-alive"}
ws_client_url = 'ws://' + remote_host + ':' + str(remote_port)
server_database = dict()

# ---HTTP TEST---

# def a simple dispatcher
def simple_dispatcher(req: libhv.HttpRequest) -> tuple[str, int]:
    status_code = 200
    ret_str = ''
    if req.method == 'POST' or req.method == 'PUT':
        server_database.update({req.path: req.data})
        ret_str = 'Successfully updated server database from client!'
    elif req.method == 'GET':
        try:
            ret_str = server_database[req.path]
        except KeyError:
            ret_str = '404 Not Found'
    elif req.method == 'DELETE':
        server_database.pop(req.path)
        ret_str = 'Successfully deleted content!'  
    return (ret_str, status_code)

# def a test func for client
def wait(resp: libhv.HttpResponse, serv: libhv.HttpServer) -> None:
    while not serv.dispatch(simple_dispatcher):
        pass
    while not resp.completed:
        pass

def http_client_test(client: libhv.HttpClient, serv: libhv.HttpServer, url='127.0.0.1:8080', params=None, headers=None, 
                     data='Post from client',json=None, timeout=10) -> None:
    resp = client.post(url+'/ping', params=params, headers=text_header, data=data, json=json, timeout=timeout)
    wait(resp, serv)
    resp = client.get(url+'/ping', params=params, headers=headers, timeout=timeout)
    wait(resp, serv)
    assert resp.text == data
    resp = client.put(url+'/ping', params=params, headers=headers, data='Updated post', json=json, timeout=timeout)
    wait(resp, serv)
    assert resp.text == 'Successfully updated server database from client!'
    resp = client.delete(url+'/ping', params=params, headers=headers, timeout=timeout)
    wait(resp, serv)
    assert resp.text == 'Successfully deleted content!'


# test server start/stop
a_server = libhv.HttpServer(remote_host, remote_port)
a_error = a_server.start()
assert libhv.strerror(a_error) == 'OK'
a_error = a_server.stop()
assert libhv.strerror(a_error) == 'OK'
a_server.start()

# test client
http_client_test(libhv.HttpClient(), a_server)
a_server.stop()

# --WebSocket TEST---

# def test funcs for server and client
def get_channel_id(serv: libhv.HttpServer) -> libhv.WsChannelId:
    recv_serv = serv.ws_recv()
    while recv_serv is None:
        recv_serv = serv.ws_recv()
    WsMessageType, WsChannel = recv_serv
    if WsMessageType == 'onopen':
        channel_id, http_req = WsChannel
    elif WsMessageType == 'onclose':
        channel_id = WsChannel
    elif WsMessageType == 'onmessage':
        channel_id, msg = WsChannel
    return channel_id

def ws_client_2_server_test(client: libhv.WebSocketClient, serv: libhv.HttpServer, channel: libhv.WsChannelId,
                            data='Hello from client') -> None:
    send_result = client.send(data)
    assert send_result > 0
    recv_serv = serv.ws_recv()
    while recv_serv is None:
        recv_serv = serv.ws_recv()
    if recv_serv[0] == 'onmessage':
        assert recv_serv[1][0] == channel
        assert recv_serv[1][1] == data
    elif recv_serv[0] == 'onclose':
        assert recv_serv[1] == channel
        serv.ws_close(channel)

def ws_server_2_client_test(serv: libhv.HttpServer, client: libhv.WebSocketClient, channel: libhv.WsChannelId,
                            data='Hello from server') -> None:
    send_result = serv.ws_send(channel, data)
    assert send_result > 0
    recv_client = client.recv()
    while recv_client is None:
        recv_client = client.recv()
    if recv_client[0] == 'onmessage':
        assert recv_client[1] == data

# def websocket ping interval and start
a_server.ws_set_ping_interval(1000)
a_server.start()

if INTERACTIVE_TEST:
    channel = get_channel_id(a_server)
    print('Connected channel = ',channel)
    start_time = time.time()
    trans_cnt = 0
    while 1:
        # mi = input()
        retval = a_server.ws_send(channel, 'Test')
        # print('server sent status = ',retval)
        retmsg = a_server.ws_recv()
        while retmsg is None:
            retmsg = a_server.ws_recv()
        # print(retmsg)
        end_time = time.time()
        trans_cnt += 1
        if end_time - start_time >= 1:
            print(trans_cnt)
            break
else:
    # test WebSocket client start
    a_client = libhv.WebSocketClient()
    a_error = a_client.open(ws_client_url)
    assert libhv.strerror(a_error) == 'OK'

    # test client to server msg
    channel = get_channel_id( a_server)
    ws_client_2_server_test(a_client, a_server, channel)
    # test server to client msg
    ws_server_2_client_test(a_server, a_client, channel)

    # close client and server
    a_error = a_client.close()
    assert libhv.strerror(a_error) == 'OK'
    a_error = a_server.stop()
    assert libhv.strerror(a_error) == 'OK'

    print(libhv.strerror(19))