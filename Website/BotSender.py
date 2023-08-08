import os
from telegram import Bot
import deta
from datetime import datetime
import asyncio

BotToken = os.getenv("TOKEN")
# BotToken =

project = deta.Deta()

dbToken = project.Base("Token")


def current_time():
    time = datetime.now()
    time = time.strftime("%d/%m/%Y %H:%M:%S")
    return time


def get_application():
    application = Bot(BotToken)
    return application


def CreateToken(chat_id, name):
    token = generate_token(4)
    row = {
        "key": chat_id,
        "Chat_ID": chat_id,
        "Name": name,
        "Token": str(token),
        "Time": str(current_time()),
    }
    dbToken.put(row)
    asyncio.run(
        send_message(
            chat_id=chat_id,
            msg=f"""Your updated temporary token is {token}.
Please enter the updated token to complete the registration process.""",
        )
    )
    return token


def generate_token(length):
    import secrets
    import string

    alphabet = string.digits
    token = "".join(secrets.choice(alphabet) for i in range(length))
    return token


async def send_message(chat_id, msg):
    bot = get_application()
    async with bot:
        await bot.send_message(chat_id=chat_id, text=msg)
