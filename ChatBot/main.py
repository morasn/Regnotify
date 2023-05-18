from data import (
    DBAddCourse,
    DBDropCourse,
    UserRegCourses,
    DBUserLookup,
    CourseDataExtractor,
    AddLogin,
    SemDate,
)
import time
import datetime
import os
from fastapi import FastAPI, Request
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CommandHandler,
    ContextTypes,
)
from telegram.constants import ChatAction

BotToken = os.getenv("TOKEN")

(
    SERVICE,
    ADD_SEMESTER,
    ADD_CRN,
    CONFIRM_ADD_SELECTION,
    DROP_COURSES,
    CONFIRM_DROP_COURSE,
    FOLLOWUP,
    ADD_COURSE,
    CONFIRM_AUTO_SEMESTER,
    ADD_YEAR,
) = range(10)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id

    chat_id = str(update.message.chat_id)
    name = update.effective_chat.full_name

    UserLookup = DBUserLookup(chat_id=chat_id)
    if UserLookup == None:
        reply_keyboard = [["Add Course(s)"]]
        msg = f"""Aloha {name}!
Welcome to Regnotify AUC Bot, your gateway to course notification.
Please select your service from the list.

Select /help for guidance and /contact for sending errors and suggestions to my developer."""

    else:
        reply_keyboard = [["Add Course(s)"], ["Drop Course(s)"]]
        msg = f"""Aloha {name}!
Welcome to Regnotify AUC Bot, your gateway to course notification.
Please select your service from the list.

Select /help for guidance and /contact for sending errors and suggestions to my developer."""
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Add or Drop Courses",
        ),
    )
    return SERVICE


async def service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    service_choice = update.message.text
    if service_choice == "Add Course(s)":
        global Year
        global Semester

        # today = datetime.date.today()
        # start_spring = today.replace(today.year, 10, 1)
        # end_spring = today.replace(today.year + 1, 2, 1)

        # if today > start_spring and today < end_spring:
        #     Year = today.year + 1
        #     Semester = "Spring"
        # else:
        #     Year = today.year
        #     Semester = "Fall"
        Semester, Year = SemDate()

        msg = f"The current semester is {Semester} {Year}. If the semester is correct, please select 'Yes'. To change the semester, select 'Change Semester' ."
        keyboard = [["Yes"], ["Change Semester"]]
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Semester Chosen",
            ),
        )
        return CONFIRM_AUTO_SEMESTER
    elif service_choice == "Drop Course(s)":
        global UserDBCourses
        global drop_keyboard
        global drop_options
        global UserRow

        UserRow, UserDBCourses, CourseDetail = UserRegCourses(chat_id=chat_id)
        msg = "Please select the course you wish to drop. If you want to drop all, select Drop All"
        drop_keyboard = []
        drop_options = []
        drop_keyboard.append(["Drop All"])
        for n in range(len(UserDBCourses)):
            drop_keyboard.append(
                [
                    f"{n + 1}. {CourseDetail[n]['Title']} ({CourseDetail[n]['Course_ID']}) with {CourseDetail[n]['Instructor']}"
                ]
            )
            drop_options.append(
                f"{n + 1}. {CourseDetail[n]['Title']} ({CourseDetail[n]['Course_ID']}) with {CourseDetail[n]['Instructor']}"
            )
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                drop_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Course To Be Dropped",
            ),
        )

        return DROP_COURSES
    else:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        msg = "Please choose from the below list."
        reply_keyboard = [["Add Course(s)"], ["Drop Course(s)"]]
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Add Or Drop Courses",
            ),
        )
        return SERVICE


async def confirm_auto_semester(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    response = update.message.text
    if "Yes" in response:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        msg = "Please enter the CRNs of the courses separated by a comma. For ex: 357462,69451,54524"
        time.sleep(1)
        await update.message.reply_text(msg)
        return ADD_CRN
    else:
        msg = "Please select the semester from the list."
        reply_keyboard = [["Fall"], ["Summer"], ["Spring"], ["Winter"]]
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Semester",
            ),
        )
        return ADD_SEMESTER


async def add_semester(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global Semester
    Semester = update.message.text
    if (
        "Fall" in Semester
        or "Summer" in Semester
        or "Winter" in Semester
        or "Spring" in Semester
    ):
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)

        msg = "Please enter the year for the semester. (Spring and winter courses are in the new year)"
        time.sleep(1)
        await update.message.reply_text(msg)
        return ADD_YEAR

    else:
        msg = "Please select the semester from the list."
        reply_keyboard = [["Fall"], ["Summer"], ["Spring"], ["Winter"]]
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Semester",
            ),
        )
        return ADD_SEMESTER


async def add_year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global Year
    Year = update.message.text
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    #         msg = """Please enter the year of the course.
    # Note that Spring courses are in the following year."""
    #         await update.message.reply_text(msg)
    msg = "Please enter the CRNs of the courses separated by a comma. For ex: 357462,69451,54524"
    time.sleep(1)
    await update.message.reply_text(msg)
    return ADD_CRN


async def add_crn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global CourseInfo
    global Year

    crns = update.message.text
    CourseInfo = CourseDataExtractor(
        crns=crns,
        Semester=Semester,
        Year=Year,
        chat_id=chat_id,
        name=update.effective_chat.full_name,
    )
    if "error1515" not in CourseInfo:
        for m in range(len(CourseInfo)):
            msg = f""" Course NO. {m+ 1}:
Course Name: {CourseInfo[m]['Title']}
Course ID: {CourseInfo[m]['Course_ID']}
Section: {CourseInfo[m]['Section']}
Instructor: {CourseInfo[m]['Instructor']}
Location: {CourseInfo[m]['Location']}
"""
            await update.message.reply_text(msg)
            await context.bot.send_chat_action(
                chat_id=chat_id, action=ChatAction.TYPING
            )
            time.sleep(0.5)
        msg = """Check the courses.
Are these the ones wanted? Please Select"""
        reply_keyboard = [["Yes"], ["No"]]
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes/No"
            ),
        )
        return CONFIRM_ADD_SELECTION

    else:
        i = CourseInfo.index("error1515")
        msg = f"""The following CRN is incorrect: {CourseInfo[i]}. Please enter all the CRNS again. 
If the issue is persistent, select /help for help & support."""
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(msg)
        return ADD_CRN


async def confirm_add_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    answer = update.message.text
    if answer in "Yes":
        stat = DBAddCourse(Course_Info=CourseInfo)
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        if stat == "Success":
            msg = """Thank you for using Regnotify AUC Bot. Your registration is completed successfully.
You will be notified once a change happens in the course seating.

If you wish to drop your courses or add additional courses; select /start """
            await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())

            return ConversationHandler.END
        else:
            msg = """Sorry. I faced an internal error. Please Try again later.
If the issue persists, kindly select /contact to contact my developer.

If you wish to drop your courses or add additional courses; select /start """
            await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())

            return ConversationHandler.END

    else:
        msg = "Please enter the CRNs of the courses separated by a comma. For ex: 357462,69451,54524"
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(msg)
        return ADD_CRN


async def drop_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dropped_course
    dropped_course = update.message.text
    if dropped_course == "Drop All":
        msg = f"Are you sure you want to drop all registered courses?"
        reply_keyboard = [["Yes"], ["No"]]
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes/No"
            ),
        )
        return CONFIRM_DROP_COURSE

    elif dropped_course in drop_options:
        msg = f"Are you sure you want to drop {dropped_course[2:]}"
        reply_keyboard = [["Yes"], ["No"]]
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Yes/No"
            ),
        )
        return CONFIRM_DROP_COURSE
    else:
        msg = "Please select the course you wish to drop. If you want to drop all, select Drop All"
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                drop_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Course To Be Dropped",
            ),
        )

        return DROP_COURSES


async def confirm_drop_course(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    global dropped_course
    answer = update.message.text
    if answer in "Yes":
        if dropped_course == "Drop All":
            DBDropCourse(DropSelection=f"all---{chat_id}", UserCourses=UserDBCourses)
            msg = f"""All your courses are dropped. I hope that you have the registered all of them.
See you soon .
You could press /start to register new courses or drop the ones you added."""
            await context.bot.send_chat_action(
                chat_id=chat_id, action=ChatAction.TYPING
            )
            time.sleep(0.5)
            await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        else:
            dropped_course = dropped_course.split(". ")
            DBDropCourse(
                DropSelection=UserRow,
                UserCourses=UserDBCourses[int(dropped_course[0]) - 1],
            )
            msg = f"""The course {dropped_course[1]} is dropped.
I hope that you have the registered the course.
See you soon. You could press /start to register new courses or drop the ones you added."""
            await context.bot.send_chat_action(
                chat_id=chat_id, action=ChatAction.TYPING
            )
            time.sleep(0.5)
            await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    else:
        msg = "Please select the course you wish to drop. If you want to drop all, select Drop All"
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                drop_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Course To Be Dropped",
            ),
        )

        return DROP_COURSES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = """Thank You. I hope I successfully performed your requests.
You could press /start to register new courses or drop the ones you added."""
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = """Regnotify Bot is the easiest way to keep a track of the courses on your wishlist. 
You could start a chat with me anytime by selecting /start from the menu. 

Or, you could select /add to add a course to be monitored. Kindly note that you will be notified once any change occurs in the remaining seats in your selected courses.

However, if you have already reserved your seat in a course, you could drop it using /drop. Kindly note that once a course is dropped, you will not be receiving any more messages about it. 
 
However, you have to keep in mind that the bot updates every 20 minutes, so you will be notified after that period only if a change occurs in the remaining seats (not the waitlist).

Wishing you all the best.

In the case of suggesting features or submitting errors, please select /contact"""

    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = """ If you faced an error while performing your request or have suggestion to improve the bot, do not hesitate to contact my developer. The following message you will send will be forwarded to my developer.
Please add your suggest/error/problem in a single message along with your mobile number (to be contacted through WhatsApp or Telegram). My developer will contact you in the shortest time."""
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return FOLLOWUP


async def followup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sug = update.message.text
    sug = sug + f"\n {chat_id}"
    await context.bot.send_message(chat_id="1261937220", text=sug)
    msg = """Your message has been forwarded to my developer successfully. He will reach you as soon as possible.
Thank You !
To start the chat again, press /start"""
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())


async def drop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global UserDBCourses
    global drop_keyboard
    global drop_options
    global UserRow

    UserRow, UserDBCourses, CourseDetail = UserRegCourses(chat_id=chat_id)
    msg = "Please select the course you wish to drop. If you want to drop all, select Drop All"
    drop_keyboard = []
    drop_options = []
    drop_keyboard.append(["Drop All"])
    for n in range(len(UserDBCourses)):
        drop_keyboard.append(
            [
                f"{n + 1}. {CourseDetail[n]['Title']} ({CourseDetail[n]['Course_ID']}) with {CourseDetail[n]['Instructor']}"
            ]
        )
        drop_options.append(
            f"{n + 1}. {CourseDetail[n]['Title']} ({CourseDetail[n]['Course_ID']}) with {CourseDetail[n]['Instructor']}"
        )
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(
            drop_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Course To Be Dropped",
        ),
    )

    return DROP_COURSES


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id

    chat_id = update.message.chat_id

    msg = "Please select the semester from the list."
    reply_keyboard = [["Fall"], ["Summer"], ["Spring"], ["Winter"]]
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Semester"
        ),
    )
    return ADD_SEMESTER


async def web(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    name = update.effective_chat.full_name
    msg = AddLogin(chat_id=chat_id, name=name)
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


app = FastAPI()


@app.post("/webhook")
def get_application():
    application = Application.builder().token(BotToken).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("help", help),
            CommandHandler("add", add),
            CommandHandler("drop", drop),
            CommandHandler("contact", contact),
            CommandHandler("web", web),
        ],
        states={
            SERVICE: [MessageHandler((~filters.COMMAND), service)],
            ADD_SEMESTER: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), add_semester)
            ],
            ADD_CRN: [MessageHandler(filters.TEXT & (~filters.COMMAND), add_crn)],
            CONFIRM_ADD_SELECTION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), confirm_add_selection)
            ],
            DROP_COURSES: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), drop_courses)
            ],
            CONFIRM_DROP_COURSE: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), confirm_drop_course)
            ],
            FOLLOWUP: [MessageHandler(filters.TEXT & (~filters.COMMAND), followup)],
            CONFIRM_AUTO_SEMESTER: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), confirm_auto_semester)
            ],
            ADD_YEAR: [MessageHandler(filters.TEXT & (~filters.COMMAND), add_year)],
        },
        fallbacks=[
            CommandHandler("end", end),
            CommandHandler("help", help),
            # CommandHandler("start", start),
            CommandHandler("add", add),
            CommandHandler("drop", drop),
            CommandHandler("contact", contact),
            CommandHandler("web", web),
        ],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)

    # application.run_polling()
    return application


get_application()
application = get_application()

app = FastAPI()


@app.post("/")
async def webhook_handler(req: Request):
    data = await req.json()
    async with application:
        await application.start()
        await application.process_update(Update.de_json(data=data, bot=application.bot))
        await application.stop()
        return "Hello Deta, I am running with HTTP"
