from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
import uvicorn

url = 'http://127.0.0.1:8080'
ws_url = 'ws://127.0.0.1:8080'
fixed_data = 'Test message from server'

server = FastAPI()

# ---HTTP--

# define POST method from client
@server.post('/')
async def post_json(data_recv: str=Body(..., embed=True)):
    return {'data_recv': data_recv}

# define GET method from client
@server.get('/')
async def get():
    return fixed_data
@server.get('/client')
async def read_client():
    return 'Client subpage is empty now'

# ---WebSocket---

@server.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"{data}")
    except WebSocketDisconnect:
        pass

# run the server on uvicorn
uvicorn.run(server, port=8080)