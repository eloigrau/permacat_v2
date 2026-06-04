from bourseLibre import settings

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async

from .exceptions import ClientError
from .utils import get_room_or_error
from .models import Room, Profil, Message
from django.utils.timezone import now


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
                "username": str(self.scope["user"].username),
                "message": str(message),
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


import datetime
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Room, Message

class ChatConsumer2(AsyncJsonWebsocketConsumer):
    """
    A chat consumer is aware of:

    - The existing rooms: Only to existing rooms can the consumers
      be joined.
    - A map of (user.id) => channel for the users being logged in.
    """

    USERS = {}
    ROOMS = {}
    #
    # @classmethod
    # def _on_session_destroyed(cls, sender, **kwargs):
    #     """
    #     This handler is invoked when a token session is destroyed.
    #       The websocket that is connected to this channel server
    #       is popped out (closed).
    #     :param sender: The session token being destroyed.
    #     """
    #
    #     user = sender.user
    #     consumer = cls.USERS.get(user and user.id)
    #     if consumer:
    #         async_to_sync(consumer.send_json)({"type": "notification", "code": "logged-out"}, True)

    @classmethod
    def _on_room_destroyed(cls, sender, instance, using, **kwargs):
        """
        This handler is invoked when a room is destroyed.
        :param sender: Room class.
        :param instance: A Room instance.
        :param using: 'default'.
        """

        room_consumers = cls.ROOMS.pop(instance.titre, set())
        for consumer in room_consumers:
            async_to_sync(consumer.receive_part)(instance.titre)

    async def accept_user(self):
        """
        Accepts the current connection, provided it is authenticated
          and not already connected. Also the signal is setup for the
          first time to appropriately end the connection when a session
          ends.
        """

        # Set the signal for when the token sessions are destroyed.
        #session_destroyed.connect(self._on_session_destroyed, dispatch_uid='on_session_destroyed')

         #logger.info("New connection established")
        user = self.scope["user"]
        await self.accept()
        if not user or user.is_anonymous:
            #logger.info(">> It has no user - closing")
            await self.send_json({"type": "fatal", "code": "not-authenticated"}, True)
            return False
        elif user.id in self.USERS:
            #logger.info(">> It is already connected with user: %d " % user.id)
            return True
            #self.scope.pop("user", None)
            #await self.send_json({"type": "fatal", "code": "already-chatting"}, True)
            #return False
        else:
            #logger.info(">> It is connecting with user: %d - moving forward" % user.id)
            self.USERS[user.id] = self
            self.rooms = set()
            return True

    async def connect(self):
        """
        A connection lifecycle involves checking the user and then
          sending a greeting message (involving some help).
        """

        # Check the user and accept the connection.
        accepted = await self.accept_user()

        # Send a MOTD with help.
        if accepted:
            await self.send_json({
                "type": "notification",
                "code": "welcome",
                "content": 'Welcome to PermaChat!\n\nIf you see this message, this means you\'re using an API '
                           'instead of the given UI. Send a {"type": "help"} message for details about this '
                           'server\'s commands'
            })

    async def disconnect(self, close_code):
        """
        Ensures the connection's user is disconnected from each room,
          and from the server tracking.
        :param close_code: The close code of the connection.
        """

        user = self.scope.get("user")
        if user:
            for room_name in getattr(self, 'rooms', set()).copy():
                await self._notify_user_leaving_room(room_name)
                await self._remove_from_room(room_name)
            self.USERS.pop(user.id, None)

    async def receive_json(self, content, **kwargs):
        """
        Processes the incoming message from the client websocket.

        Allowed commands are:

         - {"type": "help"}
         - {"type": "list"}
         - {"type": "join", "room_name": "..."}
         - {"type": "part", "room_name": "..."}
         - {"type": "message", "room_name": "...", "content": "..."}
         - {"type": "custom", "code": "...", "payload": "..."}
           - These "custom" messages are not stored in log.
           - Special clients may attend these messages when sent
             to a room. One example is:
             {"type": "custom", "code": "stock", "payload": "aapl.us"}
        :param content: The message body.
        :param kwargs: Other arguments - unused.
        """

        # await self.channel_layer.group_send(room_name, ...)
        # ... = {"type": "on_broadcast",  ...more data}

        if not isinstance(content, dict):
            await self.send_json({"type": "error", "code": "invalid-format"})
        else:
            type_ = content.get('type')
            if type_ == "help":
                await self.receive_help()
            elif type_ == "list":
                await self.receive_list()
            elif type_ == "join":
                await self.receive_join(content.get('room_name'))
            elif type_ == "part":
                await self.receive_part(content.get('room_name'))
            elif type_ == "message":
                await self.receive_message(content.get('room_name'), content.get('body'))
            elif type_ == "custom":
                await self.receive_custom(content.get('room_name'), content.get('command'), content.get('payload'))
            else:
                await self.send_json({"type": "error", "code": "unsupported-command", "details": {"type": type_}})

    async def receive_help(self):
        """
        Processes a help command. This command will return
          the help text for this server.
        """

        await self.send_json({"type": "notification", "code": "help", "help": """
        This help is only meaningful if you're using the API directly instead of through the given UI.

        The following list of commands are allowed in this server:
        - {"type": "help"}
          - Display this help again.
        - {"type": "list"}
          - List all the available rooms in this server.
        - {"type": "message", "room_name": "making_friends", "body": "Hello everyone!"}
          - Sends "Hello everyone!" to the "making_friends" channel.
          - The channel must exist.
          - You must be already joined in the channel.
        - {"type": "message", "room_name": "making_friends", "command": "foo", "payload": "bar"}
          - Sends "a /foo=bar" command to the "making_friends" channel.
          - The channel must exist.
          - You must be already joined in the channel.
        - {"type": "join", "room_name": "making_friends"}
          - Joins the channel, if not already joined.
        - {"type": "part", "room_name": "making_friends"}
          - Leaves the channel, if already joined.
        """})

    async def receive_list(self):
        """
        Processes a list command. This command will return
          a list of all the available rooms in the server,
          also telling which one is the user joined to.
        """

        rooms = await database_sync_to_async(lambda: list(Room.objects.order_by('titre')))()
        await self.send_json({"type": "notification", "code": "list", "list": [{
            "name": room.slug, "perma": " *" if room.estPermanent else "", "joined": room.titre in self.ROOMS
           # "name": room.titre, "perma": " *" if room.estPermanent else "", "joined": room.titre in self.ROOMS
        } for room in rooms]})

    async def _expect_types(self, specs):
        """
        Tells whether the values/types are compatible.
        Notifies the user if there are incompatibilities.
        :param specs: The list of values to check.
        :return: Whether they're all compatible.
        """

        for spec in specs:
            if len(spec) == 2:
                value, type_ = spec
                if not isinstance(value, type_):
                    break
            elif len(spec) == 3:
                value, type_, optional = spec
                if not (optional and value is None) and not isinstance(value, type_):
                    break
        else:
            return True
        await self.send_json({"type": "error", "code": "invalid-format"})
        return False

    async def _add_to_room(self, room_name):
        """
        Adds the user to the room.
        :param room_name: The room to add the user to.
        """

        self.rooms.add(room_name)
        self.ROOMS.setdefault(room_name, set()).add(self)
        await self.channel_layer.group_add(room_name, self.channel_name)

    async def _remove_from_room(self, room_name):
        """
        Removes the user from the room.
        :param room_name: The room to remove the user from.
        """

        self.ROOMS.setdefault(room_name, set()).discard(self)
        self.rooms.discard(room_name)
        await self.channel_layer.group_discard(room_name, self.channel_name)

    async def _notify_user_joining_room(self, room_name):
        """
        Tells the room users about the incoming user. The
          current user will also receive the same message.
        :param room_name: The room the user is joining.
        """

        await self.channel_layer.group_send(room_name, {
            "type": "broadcast_joined",
            "user": self.scope["user"].username, "room_name": room_name,
            "stamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    async def _get_last_50_room_messages(self, room_name):
        """
        Gets the last 50 messages, of a room.
        :param room_name: The room to grab the last messages from.
        """

        return [
            {"stamp": message.date_creation.strftime("%Y-%m-%d %H:%M"),
             "user": message.user.username, "body": message.content,
             "you": message.user == self.scope["user"]}
            for message in await database_sync_to_async(lambda: list(
                Message.objects.select_related('user').filter(room__titre=room_name).order_by("-date_creation")[:50]))()
                #Message.objects.select_related('user').filter(room__name=room_name).order_by("-date_creation")[:50]))()
        ]

    async def _get_room_users(self, room_name):
        """
        Gets all the room users (including self).
        :param room_name: The room to get the users from.
        :return: The room users
        """

        return sorted([
            {"name": channel.scope["user"].username, "you": channel.scope["user"] == self.scope["user"], "url":channel.scope["user"].get_profil_url()} for channel in
            self.ROOMS[room_name]
        ], key=lambda d: d['name'])

    async def receive_join(self, room_name):
        """
        Processes a join command. If the user is not present
          in a room, we join it and notify the whole room.
        :param room_name: The name of the room to join.
        """

        if not await self._expect_types([(room_name, str)]):
            return

        try:
            await database_sync_to_async(lambda: Room.objects.get(slug=room_name))()
            self.rooms = getattr(self, 'rooms', set())
            if room_name in self.rooms:
                await self.send_json({"type": "error", "code": "room:already-joined", "details": {"name": room_name}})
            else:
                await self._add_to_room(room_name)
                await self._notify_user_joining_room(room_name)
        except Room.DoesNotExist:
            await self.send_json({"type": "error", "code": "room:invalid", "details": {"name": room_name}})

    async def _notify_user_leaving_room(self, room_name):
        """
        Tells the room users about the leaving user. The
          current user will also receive the same message.
        :param room_name: The room the user is leaving.
        """

        await self.channel_layer.group_send(room_name, {
            "type": "broadcast_parted",
            "user": self.scope["user"].username, "room_name": room_name,
            "stamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    async def receive_part(self, room_name):
        """
        Processes a part command. If the user is present in a
          room, we pop it and notify the whole room.
        :param room_name: The name of the room to part from.
        """

        if not await self._expect_types([(room_name, str)]):
            return

        self.rooms = getattr(self, 'rooms', set())
        if room_name in self.rooms:
            await self._notify_user_leaving_room(room_name)
            await self._remove_from_room(room_name)
        else:
            await self.send_json({"type": "error", "code": "room:not-joined", "details": {"name": room_name}})

    async def _store_message(self, room_name, body):
        """
        Stores the message, sent by the user, in database.
        :param room_name: The name of the room where the message
          was sent.
        :param body: The message body.
        :return: The stored message
        """

        try:
            perma = await Room.objects.aget(slug=room_name)
            if perma.estPermanent:
                return await database_sync_to_async(lambda: Message.objects.create(room=Room.objects.get(
                    titre=room_name
                ), content=body[:512], user=self.scope["user"]))()
            return await database_sync_to_async(Message.objects.none)()
        except Room.DoesNotExist:
            await self.send_json({"error": "messageNotStored Room.DoesNotExis"})
            await self.send_json({"type": "error", "code": "messageNotStored", "details": {"name": room_name}})
        except Exception as e:
            await self.send_json({"error": "messageNotStored" + str(e)})
            await self.send_json({"type": "error", "code": "messageNotStored", "details": {"name": room_name, "erreur":str(e)}})

    async def _broadcast_message(self, room_name, body, stamp):
        """
        Broadcasts the message in the channel.
        :param room_name: The room where the message was sent.
        :param body: The message body.
        :param stamp: The message timestamp.
        """

        await self.channel_layer.group_send(room_name, {
            "type": "broadcast_message",
            "user": self.scope["user"].username, "room_name": room_name, "body": body, "stamp": stamp
        })

    async def receive_message(self, room_name, body):
        """
        Processes a message command. If the user is present in the
          intended room, we broadcast the message. Messages are also
          stored in the database when the room exists.
        :param room_name: The name of the room to send the message to.
        :param body: The message body.
        """

        if not await self._expect_types([(room_name, str), (body, str)]):
            return

        if room_name in self.rooms:
            body = body.strip()
            if body:
                message = await self._store_message(room_name, body)
                if not hasattr(message, "date_creation"):
                    await self._broadcast_message(room_name, body, now().strftime("%Y-%m-%d %H:%M"))
                else:
                    await self._broadcast_message(room_name, body, message.date_creation.strftime("%Y-%m-%d %H:%M"))
            else:
                await self.send_json({"type": "error", "code": "room:empty-message"})
        else:
            await self.send_json({"type": "error", "code": "room:not-joined", "details": {"name": room_name}})

    async def _broadcast_custom(self, room_name, code, payload):
        """
        Broadcasts the message in the channel.
        :param room_name: The name of the room to send the custom command to.
        :param code: The payload code.
        :param payload: The payload data.
        """

        await self.channel_layer.group_send(room_name, {
            "type": "broadcast_custom",
            "user": self.scope["user"].username, "room_name": room_name, "command": code, "payload": payload,
            "stamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    async def receive_custom(self, room_name, command, payload):
        """
        Processes a custom command. If the user is present in the
          intended room, we broadcast the command. They are never
          stored in the database, and are only useful to bots that
          are also connected to the server.
        :param room_name: The name of the room to send the custom command to.
        :param command: The command code.
        :param payload: The payload data.
        """

        if not await self._expect_types([(room_name, str), (command, str), (payload, str)]):
            return

        if room_name in self.rooms:
            command = command.strip()
            if command != '' and payload != '':
                await self._broadcast_custom(room_name, command, payload)
            else:
                await self.send_json({"type": "error", "code": "room:empty-custom"})
        else:
            await self.send_json({"type": "error", "code": "room:not-joined", "details": {"name": room_name}})

    # From this point, the broadcast_* methods are listed. They
    # have a different logic depending on the user: whether the
    # same or different user broadcast it, how is a notification
    # sent to the client side.

    async def broadcast_joined(self, event):
        """
        Sends a message about a joining user, to the
          current user. If the user is the same, then
          a different message is sent.
        :param event: A {"user": ..., "room_name": ...} message.
        """

        username = event["user"]
        room_name = event["room_name"]
        stamp = event["stamp"]

        await self.send_json({
            "type": "room:notification",
            "code": "joined",
            "you": self.scope["user"].username == username,
            "status": None if self.scope["user"].username != username else {
                "users": await self._get_room_users(room_name),
                "messages": await self._get_last_50_room_messages(room_name)
            },
            "user": username,
            "room_name": room_name,
            "stamp": stamp
        })

    async def broadcast_parted(self, event):
        """
        Sends a message about a leaving user, to the
          current user. If the user is the same, then
          a different message is sent.
        :param event: A {"user": ..., "room_name": ...} packet.
        """

        username = event["user"]
        room_name = event["room_name"]
        stamp = event["stamp"]

        await self.send_json({
            "type": "room:notification",
            "code": "parted",
            "you": self.scope["user"].username == username,
            "user": username,
            "room_name": room_name,
            "stamp": stamp
        })

    async def broadcast_message(self, event):
        """
        Sends a message about an in-room message,
          by a particular user. If the user is
          the same, a different message is sent.
        :param event: A {"user": ..., "room_name": ...,
          "body": ..., "stamp": ...} packet.
        """

        username = event['user']
        room_name = event['room_name']
        body = event['body']
        stamp = event['stamp']

        await self.send_json({
            "type": "room:notification",
            "code": "message",
            "you": self.scope["user"].username == username,
            "user": username,
            "room_name": room_name,
            "body": body,
            "stamp": stamp
        })

    async def broadcast_custom(self, event):
        """
        Sends a message about an in-room command,
          by a particular user. If the user is
          the same, a different message is sent.
        :param event: A {"user": ..., "room_name": ...,
          "command": ..., "payload": ..., "stamp": ...}
          packet.
        """

        username = event['user']
        room_name = event['room_name']
        command = event['command']
        payload = event['payload']
        stamp = event['stamp']

        await self.send_json({
            "type": "room:notification",
            "code": "custom",
            "you": self.scope["user"].username == username,
            "user": username,
            "room_name": room_name,
            "command": command,
            "payload": payload,
            "stamp": stamp
        })