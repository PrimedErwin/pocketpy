import libhv

url = 'http://127.0.0.1:8080'
ws_url = 'ws://127.0.0.1:8080/ws'
channel_id = 0

server = libhv.HttpServer('127.0.0.1', 8080)
server.ws_set_ping_interval(1000)
server.start()

# http dispatcher
def simple_dispatcher(req: libhv.HttpRequest) -> tuple[str | bytes, int]:
    return (req.data, 200)

print('Server started...')

while 1:
    server.dispatch(simple_dispatcher)
    ws_recv = server.ws_recv()
    if ws_recv is not None:
        WsMessageType, WsChannel = ws_recv
        if WsMessageType == 'onopen':
            channel_id, http_req = WsChannel
        elif WsMessageType == 'onclose':
            channel_id = WsChannel
        elif WsMessageType == 'onmessage':
            channel_id, msg = WsChannel
            server.ws_send(channel_id, msg)

