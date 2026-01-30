from bourseLibre import settings

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async

from .exceptions import ClientError
from .utils import get_room_or_error
from .models import Room, Profil, Message



class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    This chat consumer handles websocket connections for chat clients.

    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    ##### WebSocket event handlers

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
        # Store which rooms the user has joined on this connection
        self.rooms = set()

    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        command = content.get("command", None)
        try:
            if command == "join":
                # Make them join the room
                await self.join_room(content["room"])
            elif command == "leave":
                # Leave the room
                await self.leave_room(content["room"])
            elif command == "send":
                await self.send_room(content["room"], content["message"])
            elif command == "send_paint":
                await self.send_paint(content["room"], content["canvas"])
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        for roomName in list(self.rooms):
            try:
                await self.leave_room(roomName)
            except ClientError:
                pass

    ##### Command helper methods called by receive_json

    async def join_room(self, roomName):
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        room = await get_room_or_error(roomName, self.scope["user"])
        # Send a join message if it's turned on
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "roomName": roomName,
                    "username": self.scope["user"].username,
                }

            )
        # Store that we're in the room
        self.rooms.add(roomName)

        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish opening the room
        await self.send_json({
            "join": room.slug,
            "title": room.titre,
        })

    async def leave_room(self, roomName):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        room = await get_room_or_error(roomName, self.scope["user"])
        # Send a leave message if it's turned on
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.leave",
                    "roomName": roomName,
                    "username": self.scope["user"].username,
                }
            )
        # Remove that we're in the room
        self.rooms.discard(roomName)

        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": str(room.slug),
        })

    async def send_room(self, roomName, message):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        if roomName not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED")
        # Get the room and send to the group about it
        room = await get_room_or_error(roomName, self.scope["user"])
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "roomName": roomName,
                "username": self.scope["user"].username,
                "message": message,
            }
        )
        await self.save_message(self.scope["user"].username, room, message)

    @sync_to_async
    def save_message(self, username, room, message):
        user = Profil.objects.get(username=username)
        if room.estPermanent:
            Message.objects.create(user=user, room=room, content=message)


    async def send_paint(self, roomName, canvas):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        if roomName not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED + %s" %str(self.rooms))
        # Get the room and send to the group about it
        room = await get_room_or_error(roomName, self.scope["user"])
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.paint",
                "roomName": roomName,
                "username": self.scope["user"].username,
                "canvas": canvas,
            }
        )
    ##### Handlers for messages sent over the channel layer

    # These helper methods are named by the types we send - so chat.join becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        room = await get_room_or_error(event["roomName"], self.scope["user"])
        if room.estPermanent:
            await self.get_messages(room)

        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_ENTER,
                "room": event["roomName"],
                "username": event["username"],
            },
        )

    @sync_to_async
    def get_messages(self, room):
        print('get messagg ' + str(room))
        if room.estPermanent:
            for m in Message.objects.filter(room=room)[:30]:
                print('sendjsson ' + str(m))
                self.send_json(
                    {
                        "msg_type": settings.MSG_TYPE_MESSAGE,
                        "room": m.room.slug,
                        "username": m.user.username,
                        "message": m.content,
                    },
                )

    async def chat_leave(self, event):
        """
        Called when someone has left our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_LEAVE,
                "room": event["roomName"],
                "username": event["username"],
            },
        )

    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_MESSAGE,
                "room": event["roomName"],
                "username": event["username"],
                "message": event["message"],
            },
        )

    async def chat_paint(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_PAINT,
                "room": event["roomName"],
                "username": event["username"],
                "canvas": event["canvas"],
            },
        )
