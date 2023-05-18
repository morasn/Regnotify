from data import DBReader, BannerRetriever
from flask import Flask
from deta import Deta
from telegram import Bot
import os


app = Flask(__name__)


def get_application():
    BotToken = os.getenv("TOKEN")
    application = Bot(BotToken)
    return application


@app.route("/__space/v0/actions", methods=["POST"])
async def actions():
    try:
        deta = Deta()
        BannerDB = deta.Base("Banner")
        CoursesDB = DBReader("Courses")
        OldDB = DBReader("Banner")
        NewDB = BannerRetriever()

        old_db_dict = {old_dict["key"]: old_dict for old_dict in OldDB}
        new_db_changed = []
        new_db_added = []

        bot = get_application()
        async with bot:
            async with bot:
                for new_dict in NewDB:
                    old_dict = old_db_dict.get(new_dict["key"])
                    if old_dict is None:
                        new_db_added.append(new_dict)
                    elif str(old_dict["Remaining"]) != str(new_dict["Remaining"]):
                        new_db_changed.append(new_dict)
                        crnsRow = next(
                            (sub for sub in CoursesDB if sub["key"] == new_dict["key"]),
                            None,
                        )

                        if crnsRow is not None and "Chat_IDS" in crnsRow:
                            chat_ids = str(crnsRow["Chat_IDS"]).split(",")
                            for chat_id in chat_ids:
                                if int(new_dict["Remaining"]) == 0:
                                    msg = f"""Unfortunately there are no seats remaining in the course {new_dict["Title"]} ({new_dict["Course_ID"]}) with section number {new_dict["Section"]} . However, there is still hope do not worry."""
                                else:
                                    msg = f"""{new_dict["Remaining"]} Seats are now available in the course {new_dict["Title"]} ({new_dict["Course_ID"]}) with the instructor {new_dict["Instructor"]} and section number {new_dict["Section"]}. Hurry up to reserve the course.
                        CRN is {new_dict["CRN"]} """

                            await bot.send_message(chat_id=chat_id, text=msg)

                for m in range(0, len(new_db_added), 25):
                    BannerDB.put_many(new_db_added[m : m + 25])

                for c in range(0, len(new_db_changed), 25):
                    BannerDB.put_many(new_db_changed[c : c + 25])
    except Exception:
        pass

    return "CRON Done Successfully!"
