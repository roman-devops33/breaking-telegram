from pyrogram.raw.types import (
    UpdateNewMessage,
    MessageMediaPhoto,
    MessageMediaDocument,
    PeerUser,
    MessageService,
)
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

session_string = os.environ['TG_SESSION_STRING']
api_id = os.environ['TG_API_ID']
api_hash = os.environ['TG_API_HASH']

app = Client(name="default", session_string=session_string, api_id=api_id, api_hash=api_hash)


@app.on_raw_update(group=-100)
async def handler(app, update, users, chats):
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
            message = await app.get_messages(update.message.peer_id.user_id, update.message.id)
            text = (
                f"__New Secret__\n__From__ {message.from_user.first_name} -"
                f" [{message.from_user.id}](tg://user?id={message.from_user.id}) \n\n"
                f"[Go to message](tg://openmessage?user_id={str(message.chat.id)}"
                f"&message_id={message.id})\n"
            )
            path = await message.download()
            if os.path.exists(path):
                await app.send_document("me", path, caption=text)
                os.remove(path)


async def job():
    await app.send_message("me", "Breaking telegram in work")

# interval seconds for tests
scheduler = AsyncIOScheduler()
scheduler.add_job(job, "interval", weeks=1)

scheduler.start()
app.run()
