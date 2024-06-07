from data import logger
from chat import get_application
from fastapi import FastAPI, Request
from telegram import Update
import os


BotToken = os.getenv("TOKEN")
application = get_application(BotToken)

app = FastAPI()


@app.post("/")
async def webhook_handler(req: Request):
    data = await req.json()
    try:
        logger(data)
    except:
        print(data)
        pass
    async with application:
        await application.start()
        await application.process_update(Update.de_json(data=data, bot=application.bot))
        await application.stop()
        return "Hello Deta, I am running with HTTP"
