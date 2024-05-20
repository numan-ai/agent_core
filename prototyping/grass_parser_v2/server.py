import asyncio
import copy
import json
import queue
import random
import threading
from uuid import uuid4
import websockets
        

client_list = []
updates = queue.Queue(maxsize=1)


with open("positions_cache.json", "r") as f:
    positions_cache = json.load(f)


def send_updates(data):
    updates.put(data)


async def _send_updates():
    while not client_list:
        await asyncio.sleep(0.1)

    main_data = None
    main_data_nodes = None

    while True:
        if updates.empty():
            # await asyncio.sleep(0.1)
            data = last_data
        else:
            data = updates.get()
            last_data = data

        nodes = {
            node['id']: node
            for node in data['nodes']
        }

        if main_data is None:
            main_data = data
            main_data_nodes = copy.deepcopy(nodes)

        need_update = False
        for node in main_data['nodes']:
            expected = nodes[node['id']]['weight']
            diff = node['weight'] - expected
            if abs(diff) > 0.01:
                node['weight'] -= diff * 0.2
                need_update = True
            node['label'] = f"{main_data_nodes[node['id']]['label']}\n{nodes[node['id']]['energy'] * 100:.0f}"

        if need_update:
            for client in client_list.copy():
                try:
                    await client.send(json.dumps(main_data))
                except websockets.exceptions.ConnectionClosedError:
                    client_list.remove(client)
                    print("Client disconnected")
                except websockets.exceptions.ConnectionClosedOK:
                    client_list.remove(client)
                    print("Client disconnected")

        await asyncio.sleep(0.02)


async def handle_client(websocket, path):
    # Handle incoming messages from the client
    client_list.append(websocket)
    async for message in websocket:
        data = json.loads(message)
        if data['action'] == 'move':
            positions_cache[data['data']['id']] = data['data']
            with open("positions_cache.json", "w") as f:
                json.dump(positions_cache, f)


async def _start_server():
    # Create a WebSocket server
    server = await websockets.serve(handle_client, '192.168.0.144', 8384)

    # Start the server
    print("Server started")
    await asyncio.gather(
        server.wait_closed(),
        _send_updates(),
    )


def _start_threaded_server():
    asyncio.run(_start_server())


def start_server():
    threading.Thread(target=_start_threaded_server).start()
