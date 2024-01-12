from data import (
    DBAddCourse,
    DBDropCourse,
    UserRegCourses,
    CourseDataExtractor,
    AddLogin,
    SemDate,
    DropCheck,
    Alt_Course_Finder,
    IsUser,
    IsWebUser,
    GetUsername,
    ResetPasswordToken,
)
import time
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
    WEB_SERVICE,
    ALT_CATEGORY,
    ALT_DAY,
    ALT_TIME,
) = range(14)


# ====================================================================================================
# This Section is for the Service Selection
# Includes the diversion to all sets of functions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id

    chat_id = str(update.message.chat_id)
    name = update.effective_chat.full_name
    IsUser(chat_id, name)

    try:
        DropCheck(chat_id)
        reply_keyboard = [
            ["Add Course(s)"],
            ["Drop Course(s)"],
            ["Alternative Core Course"],
        ]

    except RuntimeError:
        reply_keyboard = [["Add Course(s)"], ["Alternative Core Course"]]

    finally:
        msg = f"""Aloha {name}!
Welcome to Regnotify AUC Bot, your gateway to course notification.
Please select your service from the list.

Select /help for guidance and /contact for sending errors and suggestions to my developer.
To know more about the bot's privacy policy, select /privacy."""
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
        try:
            Semester, Year = SemDate()
        except RuntimeError:
            msg = "Please select the semester from the list."
            reply_keyboard = [["Fall"], ["Summer"], ["Spring"], ["Winter"]]
            await context.bot.send_chat_action(
                chat_id=chat_id, action=ChatAction.TYPING
            )
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
        global Courses
        global drop_keyboard
        global drop_options

        BannerDetails, Courses = UserRegCourses(chat_id=chat_id)
        msg = "Please select the course you wish to drop. If you want to drop all, select Drop All"

        drop_keyboard = []
        drop_options = []
        drop_keyboard.append(["Drop All"])

        for n, course in enumerate(BannerDetails):
            drop_keyboard.append(
                [
                    f"{n + 1}. {course['Title']} ({course['Course_ID']}) with {course['Instructor']}"
                ]
            )
            drop_options.append(
                f"{n + 1}. {course['Title']} ({course['Course_ID']}) with {course['Instructor']}"
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
    elif service_choice == "Alternative Core Course":
        categories = [
            ["Pathways 1 - Sci. Encounters"],
            ["Pathways 2 - Cult. Encounters"],
            ["Humanities and Social Sciences"],
            ["Arab World Studies"],
            ["Arab World Studies - Egypt"],
            ["Global Studies"],
            ["Core Capstone"],
        ]
        msg = "Please select the core course category."
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                categories,
                one_time_keyboard=True,
                input_field_placeholder="Core Course Category",
            ),
        )
        return ALT_CATEGORY

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


async def drop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global Courses
    global drop_keyboard
    global drop_options

    global chat_id
    global name

    chat_id = str(update.message.chat_id)
    name = str(update.effective_chat.full_name)
    try:
        BannerDetails, Courses = UserRegCourses(chat_id=chat_id)
        msg = "Please select the course you wish to drop. If you want to drop all, select Drop All"

        drop_keyboard = []
        drop_options = []
        drop_keyboard.append(["Drop All"])

        for n, course in enumerate(BannerDetails):
            drop_keyboard.append(
                [
                    f"{n + 1}. {course['Title']} ({course['Course_ID']}) with {course['Instructor']}"
                ]
            )
            drop_options.append(
                f"{n + 1}. {course['Title']} ({course['Course_ID']}) with {course['Instructor']}"
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

    except RuntimeError:
        msg = """You have not registered any courses yet. Select /add to register a course."""
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global Year
    global Semester
    global chat_id
    global name

    chat_id = str(update.message.chat_id)
    name = update.effective_chat.full_name
    try:
        Semester, Year = SemDate()
    except RuntimeError:
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


# ====================================================================================================


# ====================================================================================================
# This Section is for Adding Courses to the Bot
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
    msg = "Please enter the CRNs of the courses separated by a comma. For ex: 357462,69451,54524"
    time.sleep(1)
    await update.message.reply_text(msg)
    return ADD_CRN


async def add_crn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global CourseInfo
    global Year

    crns = update.message.text
    try:
        CourseInfo = CourseDataExtractor(
            crns=crns,
            Semester=Semester,
            Year=Year,
            chat_id=str(update.message.chat_id),
            name=update.effective_chat.full_name,
        )

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

    except RuntimeError as e:
        CourseInfo = str(e).split(" -")[0]
        msg = f"""The following CRN is incorrect: {CourseInfo}.
Ensure that the CRN is written correctly and that the course is offered in {Semester} {Year}.
Please enter all the CRNS again. 
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
        try:
            DBAddCourse(Course_Info=CourseInfo)
            msg = """Thank you for using Regnotify AUC Bot. Your registration is completed successfully.
You will be notified once a change happens in the course seating.

If you wish to drop your courses or add additional courses; select /start """
            await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())

            return ConversationHandler.END

        except Exception as e:
            print(e)
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


# ====================================================================================================


# ====================================================================================================
# This Section is for Dropping Courses from the Bot
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
            try:
                DBDropCourse(type="all", Courses=Courses)

                msg = f"""All your courses are dropped. I hope that you have the registered all of them.
See you soon .
You could press /start to register new courses or drop the ones you added."""
                await context.bot.send_chat_action(
                    chat_id=chat_id, action=ChatAction.TYPING
                )
                time.sleep(0.5)
                await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
                return ConversationHandler.END

            except RuntimeError as e:
                print(str(e))
                msg = f"""Sorry. I faced an internal error. Please Try again later."""
                await update.message.reply_text(msg)

        else:
            dropped_course = dropped_course.split(". ")
            try:
                DBDropCourse(
                    type=int(int(dropped_course[0]) - 1),
                    Courses=Courses,
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

            except RuntimeError as e:
                print(str(e))
                msg = f"""Sorry. I faced an internal error. Please Try again later."""
                await update.message.reply_text(msg)
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


# ====================================================================================================


# ====================================================================================================
# This Section is for the Web Registration Service
# including the registration and reset password services


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.message.chat_id)
    name = update.effective_chat.full_name
    msg = AddLogin(chat_id=chat_id, name=name)
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def web(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global chat_id

    chat_id = str(update.message.chat_id)
    user = IsWebUser(chat_id=chat_id)
    if user == False:
        msg = "You are not registered. Please register by selecting /token"
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    msg = "Please select your service from the list."
    reply_keyboard = [["Get Username"], ["Reset Password"]]
    await update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Service",
        ),
    )
    return WEB_SERVICE


async def web_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    service = update.message.text
    if service == "Get Username":
        msg = GetUsername(chat_id=chat_id)
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif service == "Reset Password":
        msg = ResetPasswordToken(chat_id=chat_id)
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        msg = "Please select your service from the list."
        reply_keyboard = [["Get Username"], ["Reset Password"]]
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Service",
            ),
        )
        return WEB_SERVICE


# ====================================================================================================


# ====================================================================================================
# This Section is for the Other Bot Commands.
# Including the Privacy Policy, Ending the Chat, and the Help and Contact Services
async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = """This bot is created to help students to keep a track of the courses they want to register for.
The developer of the bot hold no responsibility for the data stored in the bot. This data includes the courses you add to the bot and your name and chat id (unique for each user). The chat id is used to send you messages about the courses you add to the bot. The data is stored in a database.
The data could be used in the future to improve the bot and to add more features to it along with being used in the research about the implications of the bot. In these scenarios, the data will be used anonymously.
Phone numbers are not seen by the bot, so you will not be contacted by the developer unless you contact him first.

To start the chat again, press /start"""

    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


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

In the case of suggesting features or submitting errors, please select /contact.

To start the chat again, press /start"""

    await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


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
    return ConversationHandler.END


# ====================================================================================================


# ====================================================================================================
# This Section is for the Alternative Core Course Finder Service
async def alt_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global core_course_category

    core_course_category = update.message.text

    if core_course_category in [
        "Pathways 1 - Sci. Encounters",
        "Humanities and Social Sciences",
        "Pathways 2 - Cult. Encounters",
        "Arab World Studies",
        "Arab World Studies - Egypt",
        "Global Studies",
        "Core Capstone",
    ]:
        Days_Keyboard = [["MR"], ["WU"]]
        msg = "Please select the days of the week you want to attend the course."
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                Days_Keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Days",
            ),
        )
        return ALT_DAY
    else:
        categories = [
            ["Pathways 1 - Sci. Encounters"],
            ["Humanities and Social Sciences"],
            ["Pathways 2 - Cult. Encounters"],
            ["Arab World Studies"],
            ["Arab World Studies - Egypt"],
            ["Global Studies"],
            ["Core Capstone"],
        ]
        msg = "Please select the core course category."
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                categories,
                one_time_keyboard=True,
                input_field_placeholder="Core Course Category",
            ),
        )
        return ALT_CATEGORY


async def alt_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global day
    global core_course_category

    day = update.message.text
    if day in ["MR", "WU"]:
        time_keyboard = [
            ["08:30 am-09:45 am"],
            ["10:00 am-11:15 am"],
            ["11:30 am-12:45 pm"],
            ["02:00 pm-03:15 pm"],
            ["03:30 pm-04:45 pm"],
            ["05:00 pm-06:15 pm"],
        ]
        msg = "Please select the time of the course."
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                time_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Time",
            ),
        )
        return ALT_TIME
    else:
        Days_Keyboard = [["MR"], ["WU"]]
        msg = "Please select the days of the week you want to attend the course."
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                Days_Keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Days",
            ),
        )
        return ALT_DAY


async def alt_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global core_course_category
    global day

    user_time = update.message.text

    if user_time in [
        "08:30 am-09:45 am",
        "10:00 am-11:15 am",
        "11:30 am-12:45 pm",
        "02:00 pm-03:15 pm",
        "03:30 pm-04:45 pm",
        "05:00 pm-06:15 pm",
    ]:
        alt_course = Alt_Course_Finder(
            day=day, time=user_time, category=core_course_category
        )
        await update.message.reply_text(alt_course, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        msg = "Please select the time of the course."
        time_keyboard = [
            ["08:30 am-09:45 am"],
            ["10:00 am-11:15 am"],
            ["11:30 am-12:45 pm"],
            ["02:00 pm-03:15 pm"],
            ["03:30 pm-04:45 pm"],
            ["05:00 pm-06:15 pm"],
        ]
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        await update.message.reply_text(
            msg,
            reply_markup=ReplyKeyboardMarkup(
                time_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Time",
            ),
        )
        return ALT_TIME


# ====================================================================================================


# ====================================================================================================
# This Section is for The Conversation Handler Service, managing the follow of the conversation between the user and the bot
def get_application(BotToken: str):
    application = Application.builder().token(BotToken).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("help", help),
            CommandHandler("add", add),
            CommandHandler("drop", drop),
            CommandHandler("contact", contact),
            CommandHandler("token", token),
            CommandHandler("privacy", privacy),
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
            WEB_SERVICE: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), web_service)
            ],
            ALT_CATEGORY: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), alt_category)
            ],
            ALT_DAY: [MessageHandler(filters.TEXT & (~filters.COMMAND), alt_day)],
            ALT_TIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), alt_time)],
        },
        fallbacks=[
            CommandHandler("end", end),
            CommandHandler("help", help),
            CommandHandler("add", add),
            CommandHandler("drop", drop),
            CommandHandler("contact", contact),
            CommandHandler("token", token),
            CommandHandler("privacy", privacy),
            CommandHandler("web", web),
        ],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)

    return application
