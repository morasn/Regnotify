import os
from telegram import Bot
import deta
from datetime import datetime
import asyncio
import secrets
import string

BotToken = os.getenv("TOKEN")

project = deta.Deta()

dbToken = project.Base("Token")

# Initialize the Reset Password database
dbResetPassw = project.Base("PasswordReset")


def current_time():
    time = datetime.now()
    time = time.strftime("%d/%m/%Y %H:%M:%S:%f")
    return time


def generate_token(length):
    alphabet = string.digits
    token = "".join(secrets.choice(alphabet) for i in range(length))
    return token


async def send_message(chat_id, msg):
    bot = Bot(BotToken)
    async with bot:
        await bot.send_message(chat_id=chat_id, text=msg)


def CreateToken(chat_id, name, db):
    token = generate_token(4)
    row = {
        "key": chat_id,
        "Chat_ID": chat_id,
        "Name": name,
        "Token": str(token),
        "Time": str(current_time()),
    }
    if db == "passw":
        dbResetPassw.put(row)
        asyncio.run(
            send_message(
                chat_id=chat_id,
                msg=f"""Your updated temporary token is {token}.
Please enter the updated token to reset the password.""",
            )
        )
    elif db == "reg":
        dbToken.put(row)
        asyncio.run(
            send_message(
                chat_id=chat_id,
                msg=f"""Your updated temporary token is {token}.
Please enter the updated token to complete the registration process.""",
            )
        )
    return token
