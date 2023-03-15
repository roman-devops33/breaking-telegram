from pyrogram.raw.types import (
    UpdateNewMessage,
    MessageMediaPhoto,
    MessageMediaDocument,
    PeerUser,
    MessageService,
)
from pyrogram import Client
import os

session_string = os.environ['TG_SESSION_STRING']
session_string_v2 = os.environ['TG_SESSION_STRING_UPD']
api_id = os.environ['TG_API_ID']
api_hash = os.environ['TG_API_HASH']

client = Client(name='test', api_id=api_id, api_hash=api_hash, session_string=session_string_v2, in_memory=True)


@client.on_raw_update(group=-100)
def handler(client, update, users, chats):
    if isinstance(update, UpdateNewMessage) and not isinstance(
        update.message, MessageService
    ):
        if (
            (
                isinstance(update.message.media, MessageMediaDocument)
                or isinstance(update.message.media, MessageMediaPhoto)
            )
            and isinstance(update.message.peer_id, PeerUser)
            and update.message.out is False
            and update.message.media.ttl_seconds is not None
        ):
            message = client.get_messages(update.message.peer_id.user_id, update.message.id)
            text = (
                f"__New Secret__\n__From__ {message.from_user.first_name} -"
                f" [{message.from_user.id}](tg://user?id={message.from_user.id}) \n\n"
                f"[Go to message](tg://openmessage?user_id={str(message.chat.id)}"
                f"&message_id={message.message_id})\n"
            )
            path = message.download()
            if os.path.exists(path):
                client.send_document("me", path, caption=text)
                os.remove(path)


client.run()
