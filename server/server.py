import asyncio
import json
import random
import secrets
from dataclasses import dataclass, field
from typing import Any, NamedTuple, Optional

import uvloop
from websockets import exceptions as ws_exceptions
from websockets import server


def encode_msg(msg: dict[str, Any]) -> str:
    return json.dumps(msg, ensure_ascii=False)


def decode_msg(msg: str | bytes) -> Any:
    return json.loads(msg)


PLAYER_SPEED = 2
BOARD_HEIGHT = 500
BOARD_WIDTH = 500


class Coords(NamedTuple):
    x: int
    y: int


def get_new_player_coordinates() -> Coords:
    return Coords(random.randint(0, 64), random.randint(0, 64))


@dataclass
class Client:
    socket: server.WebSocketServerProtocol
    id: str
    coords: Coords
    disconnected: bool = False


@dataclass
class Room:
    key: str
    clients: dict[str, Client] = field(default_factory=dict)
    new_clients: list[Client] = field(default_factory=list)
    msg_id: int = 0
    event_queue: asyncio.Queue[Optional[dict[str, Any]]] = field(
        default_factory=asyncio.Queue
    )
    listening: bool = False
    future: Any = None

    def client_count(self) -> int:
        return len(
            [client.id for client in self.clients.values() if not client.disconnected]
        )


clients: list[Client] = []

rooms: dict[str, Room] = {}


async def listen_room(room: Room) -> None:
    room.listening = True
    print(f"Listening room {room.key}")
    while True:
        qevent = await room.event_queue.get()
        if qevent is None:
            break

        # add any new clients to the room's known clients, then clear out new_clients.
        if len(room.new_clients) > 0:
            for client in room.new_clients:
                room.clients[client.id] = client
            room.new_clients = []

        # increment the msg_id for this msg and add it to the message before sending it
        room.msg_id += 1
        qevent["msg_id"] = room.msg_id
        count = 0
        disconnected: list[str] = []

        # Send message to all known clients
        for client in room.clients.values():
            # If this client is set to disconnected then add to disconnected list and don't send msg
            if client.disconnected:
                disconnected.append(client.id)
                continue
            count += 1

            # Send the message `qevent` to current client
            try:
                await client.socket.send(encode_msg(qevent))
            except ws_exceptions.ConnectionClosed:
                print("Lost client in send")
                client.disconnected = True

        # Remove disconnected clients from the list of clients in the room
        for d in disconnected:
            if room.clients[d]:
                del room.clients[d]

    # Runs if there are is a None event in the queue, tearing down the room.
    print(f"Unlisten room {room.key}")
    room.listening = False


async def handle_join(room_key: str, client: Client) -> Room:
    """
    Handle when a new client connects.

    If room_key is present in `rooms` already, we join the existing room.
    If room_key is not present in `rooms`, we create a new room with `room_key`
    """
    if room_key not in rooms:
        room = Room(key=room_key)
        rooms[room_key] = room

        room.future = asyncio.ensure_future(listen_room(room))
    else:
        room = rooms[room_key]

    room.new_clients.append(client)
    joined_msg = {"type": "joined", "client_id": client.id, "coords": client.coords}
    await room.event_queue.put(joined_msg)
    return room


async def listen_socket(websocket: server.WebSocketServerProtocol, path: str) -> None:
    """
    Listen for messages from a client and either join them to a room or forward the message to the room
    """
    print("connect", path)
    client_id = secrets.token_hex(16)
    room: Optional[Room] = None
    client = Client(id=client_id, socket=websocket, coords=get_new_player_coordinates())

    try:
        # For message we get from client, decode and then route to handler
        async for message_raw in websocket:
            message = decode_msg(message_raw)
            message["client_id"] = client.id
            # handle a join message from client
            if message["type"] == "join":
                room_key = message.get("room", "default")
                room = await handle_join(room_key, client)
            # If we're already in a room, put message in queue
            elif room:
                await room.event_queue.put(message)
            # We're not in a room yet so send the message directly back to the client
            else:
                await websocket.send(encode_msg(message))
    except ws_exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(e)
    client.disconnected = True
    # We don't keep empty rooms around
    if room is not None and room.client_count() == 0:
        # Put a None in the queue to cause the event loop to stop
        await room.event_queue.put(None)
        del rooms[room.key]
        await room.future
        print(f"Cleaned up room {room.key}")
    print("disconnect", rooms)


def main() -> int:
    uvloop.install()
    start_server = server.serve(
        listen_socket, "localhost", 31337, ping_interval=5, ping_timeout=5
    )
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
