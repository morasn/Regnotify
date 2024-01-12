from datetime import datetime
from deta import Deta
import os

project = Deta()

# Initialize the Credentials database
dbCredentials = project.Base("Credentials")

# Initialize the Users database
dbUsers = project.Base("Users")

# Initialize the Courses database
dbCourses = project.Base("Courses")

# Initialize the Temp database
dbToken = project.Base("Token")

# Initialize the Banner database
dbBanner = project.Base("Banner")

# Initialize the DumpData database
dbDumpData = project.Base("DumpData")


def current_time():
    time = datetime.now()
    time = time.strftime("%d/%m/%Y %H:%M:%S:%f")
    return time


def logger(data):
    dbLogger = project.Base("Logger")
    try:
        dbLogger.put(
            {
                "first_name": data["message"]["from"]["first_name"],
                "username": data["message"]["from"]["username"],
                "chat_id": data["message"]["from"]["id"],
                "key": current_time(),
                "text": data["message"]["text"],
            }
        )
    except:
        dbLogger.put(
            {
                "first_name": data["message"]["from"]["first_name"],
                "last_name": data["message"]["from"]["last_name"],
                "chat_id": data["message"]["from"]["id"],
                "key": current_time(),
                "text": data["message"]["text"],
            }
        )


def IsUser(chat_id, name):
    UserRow = dbUsers.get(chat_id)
    if UserRow == None:
        NewUser(chat_id, name)
        return False
    else:
        return True


def NewUser(chat_id, name):
    dbUsers.put(
        {
            "Chat_ID": chat_id,
            "Name": name,
            "Time": current_time(),
            "key": chat_id,
            "Username": None,
        }
    )


# ====================================================================================================
### The Three Functions below are used for course Dropping
def DropCheck(chat_id):
    UserRow = dbCourses.fetch({"Chat_ID": str(chat_id)})
    if len(UserRow.items) == 0:
        raise RuntimeError(f"User {chat_id} Has No Registered Courses to Drop")


def DBDropCourse(type, Courses):
    try:
        if type == "all":
            for course in Courses:
                dbCourses.delete(course["key"])
        else:
            dbCourses.delete(Courses[type]["key"])
    except Exception as e:
        raise RuntimeError(str(e))


def UserRegCourses(chat_id):
    UserRow = dbCourses.fetch({"Chat_ID": chat_id}).items
    if UserRow == None:
        raise RuntimeError(f"User {chat_id} Has No Registered Courses to Drop")

    BannerDetails = []
    for course in UserRow:
        BannerDetails.append(dbBanner.get(course["CustomSemester"]))
    return BannerDetails, UserRow


# ====================================================================================================


# ====================================================================================================
### The Two Functions below are used for course Adding
def CourseDataExtractor(crns: str, Semester, Year, chat_id, name):
    crns = crns.split(",")
    row = []
    for crn in crns:
        crn = crn.strip()
        CustomSemester = f"{Semester}{Year}--{crn}"

        # To check if CRN Exists or not
        temp = dbBanner.get(str(CustomSemester))
        if temp == None:
            raise RuntimeError(crn + " -Course Not Found")
        data = {}

        # Essential Variables Do not change for adding course. Again Do not change
        data["CustomSemester"] = CustomSemester
        data["key"] = str(current_time()) + "--" + temp["Course_ID"]
        data["Chat_ID"] = chat_id

        # Essential Vars for msg output. Again Do not change
        data["Title"] = temp["Title"]
        data["Course_ID"] = temp["Course_ID"]
        data["Instructor"] = temp["Instructor"]
        data["Section"] = temp["Section"]
        data["Location"] = temp["Location"]

        # Optional Variables that can be changed

        data["Name"] = name
        data["Semester"] = Semester
        data["Year"] = Year
        data["Platform"] = "ChatBot"
        data["CRN"] = crn
        row.append(data)
    return row


def DBAddCourse(Course_Info):
    dbDumpData.put_many(Course_Info)
    for course in Course_Info:
        dbCourses.put(
            {
                "CustomSemester": course["CustomSemester"],
                "key": course["key"],
                "Chat_ID": course["Chat_ID"],
                "CRN": course["CRN"],
            },
            expire_in=60 * 60 * 24 * 31 * 4,
        )
    return True


# ====================================================================================================


# ====================================================================================================
### The Functions below are used for course Web Registration
def IsWebUser(chat_id):
    UserRow = dbUsers.get(chat_id)
    if UserRow["Username"] == None:
        return False
    else:
        return UserRow


def AddLogin(chat_id, name):
    # try:
    UserRow = IsWebUser(chat_id)
    if UserRow == False:
        token = CreateToken(chat_id, name, dbToken)
        msg = f"""Your temporary token is {token}.
Please add it on --- to complete the registration process."""
        return msg
    else:
        msg = "You are already registered. If you wish to get your Username or reset your Password, select /Web"
        return msg


def GetUsername(chat_id):
    User = IsWebUser(chat_id)
    if User == False:
        msg = "You are not registered. Please register first."
        return msg
    else:
        msg = f"Your username is {User['Username']}."
        return msg


def ResetPasswordToken(chat_id):
    User = IsWebUser(chat_id)
    if User == False:
        msg = "You are not registered. Please register first."
        return msg
    else:
        dbPasswordReset = project.Base("PasswordReset")
        token = CreateToken(chat_id, User["Name"], dbPasswordReset)
        msg = f"""Your temporary token is {token}.
Note: It will expire in 24 hours."""
        return msg


def CreateToken(chat_id, name, db):
    token = generate_token(4)
    row = {
        "key": chat_id,
        "Chat_ID": chat_id,
        "Name": name,
        "Token": token,
        "Time": current_time(),
    }
    db.put(row)
    return token


def generate_token(length):
    import secrets
    import string

    alphabet = string.digits
    token = "".join(secrets.choice(alphabet) for i in range(length))
    return token


# ====================================================================================================


# ====================================================================================================
### The Functions below are used for course finding the alternative core courses
def Alt_Course_Finder(day, time, category):
    Courses = dbBanner.fetch({"Days": day, "Time": time, "Category": category}).items
    if len(Courses) == 0:
        msg = f"Sorry. I can not find any courses any {category} course at the requested time."
        return msg
    else:
        msg = ""
        alt = ""
        alt_count = 0
        index = 0
        for course in Courses:
            if int(course["Remaining"]) == 0:
                txt = f"""{alt_count + 1 }. {course["Title"]} - {course["Course_ID"]} with {course["Instructor"]} and CRN {course["CRN"]}."""
                alt_count += 1
                alt = alt + txt + "\n\n"
                continue
            txt = f"""{index + 1 }. {course["Title"]} - {course["Course_ID"]} with {course["Instructor"]} and CRN {course["CRN"]} has currently {course["Remaining"]} places available."""
            index += 1
            msg = msg + txt + "\n\n"
        if msg == "":
            msg = f"Sorry. I can not find any courses any {category} course at the requested time.\n However, these are all the courses that are available in that period.\n\n {alt}"

        return msg


# ====================================================================================================


# ====================================================================================================
### The Functions below are used for detecting the current semester
def SemDate():
    date = datetime.now()
    month = date.month
    year = date.year
    day = date.day

    if (month >= 1 and day >= 8) and month <= 3:
        # Spring
        Semester = "Spring"
    elif month >= 12:
        # Winter
        year = year + 1
        Semester = "Winter"
    elif month <= 1 and day <= 8:
        # Winter
        Semester = "Winter"
    elif (month >= 6 and day > 6) or (month <= 9 and day <= 7):
        # Fall
        Semester = "Fall"

    elif (month == 5) or (month == 6 and day <= 6):
        # Summer
        Semester = "Summer"
    else:
        raise RuntimeError("Auto Semester Detection Failed")
    return Semester, year
