import asyncio
import websockets
import json
import uuid

# Store connected clients: {room_id: {websocket}}
rooms = {}

async def handler(websocket):
    room_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")

            if action == "host":
                room_id = str(uuid.uuid4())[:6] # Simple 6 char code
                rooms[room_id] = {websocket}
                await websocket.send(json.dumps({
                    "type": "hosted",
                    "room_id": room_id
                }))
                print(f"Room created: {room_id}")

            elif action == "join":
                room_id = data.get("room_id")
                if room_id in rooms:
                    rooms[room_id].add(websocket)
                    await websocket.send(json.dumps({
                        "type": "joined",
                        "room_id": room_id
                    }))
                    print(f"Client joined room: {room_id}")
                else:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Room not found"
                    }))

            elif action == "update":
                # Broadcast update to other clients in the room
                if room_id and room_id in rooms:
                    for client in rooms[room_id]:
                        if client != websocket:
                            await client.send(json.dumps({
                                "type": "update",
                                "data": data.get("data")
                            }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if room_id and room_id in rooms:
            if websocket in rooms[room_id]:
                rooms[room_id].remove(websocket)
                if not rooms[room_id]:
                    del rooms[room_id]
                    print(f"Room closed: {room_id}")

async def main():
    # Listen on all interfaces (0.0.0.0) so other computers can connect
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Relay Server started on ws://0.0.0.0:8765 (Listening for external connections)")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
