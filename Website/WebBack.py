import deta
from datetime import datetime, timedelta

# import re
import bcrypt
from var import departments

from dotenv import load_dotenv

load_dotenv()
# Initialize the Deta project
project = deta.Deta()

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


# Authenticate the user
def authenticate(username, password):
    # Retrieve the user's credentials from the Credentials database
    user = dbCredentials.fetch({"Username": str(username)})
    if user.count != 0:
        user = user.items[0]
        passw = hasher_check(str(password), user["salt"])

        if passw == user["Password"]:
            return (user["Chat_ID"], user["Name"])
        else:
            return None, False
    else:
        return None, False


# Add a new user to the Credentials database
def add_user(username, password, chat_id):
    other = dbCredentials.fetch({"Username": username})
    if other.count != 0:
        return False
    else:
        user = dbUsers.get(chat_id)
        password, salt = hasher(password)
        dbCredentials.put(
            {
                "key": user["CHAT_ID"],
                "Password": str(password),
                "Name": user["UserName"],
                "Username": username,
                "Chat_ID": chat_id,
                "salt": salt,
            }
        )
        user["Username"] = username
        dbUsers.put(user)
        dbToken.delete(chat_id)
        return True


# Add a new course to the Courses database
def add_course(name, description):
    dbCourses.put({"name": name, "description": description})


# Delete a course from the Courses database
def delete_course(course_id):
    dbCourses.delete(course_id)


# Retrieve all courses from the Courses database
# def get_courses(chat_id):
#     user = dbUsers.get(str(chat_id))
#     crns = user["CRN"]
#     if crns == None:
#         return None
#     CoursesData = []
#     crns = crns.split(",")
#     for crn in crns:
#         course_data = dbBanner.get(crn)
#         # Semester = str(course_data["key"]).split("--")[0]
#         match = re.match(r"([A-Za-z]+)(\d+)(.*)", course_data["key"])
#         if match:
#             course_data["Semester"] = str(match.group(1)) + " " + match.group(2)
#         CoursesData.append(course_data)
#     return CoursesData


def get_courses(chat_id):
    courses = dbCourses.fetch({"Chat_ID": str(chat_id)}).items
    print(courses)
    if len(courses) == 0:
        return None
    else:
        CourseData = []
        for course in courses:
            # temp = dbBanner.get(course["CustomSemester"])
            # temp["key"] = course["key"]
            CourseData.append(dbBanner.get(course["CustomSemester"]))
            CourseData[-1]["key"] = course["key"]
        return CourseData


# Retrieve a temporary token from the Temp database
def get_token(token):
    row = dbToken.fetch({"Token": str(token)})

    today = datetime.now()

    if row.count == 0:
        return {"auth": False}
    elif today - datetime.strptime(
        row.items[0]["Time"], "%d/%m/%Y %H:%M:%S"
    ) > timedelta(days=1):
        auth = {
            "auth": "Old-Token",
            "Chat_ID": row.items[0]["Chat_ID"],
            "Name": row.items[0]["Name"],
            "Time": str(today),
        }
        return auth
    else:
        auth = {
            "auth": True,
            "Chat_ID": row.items[0]["Chat_ID"],
            "Name": row.items[0]["Name"],
            "Time": str(today),
        }

        return auth


def hasher(data):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(data.encode("utf-8"), salt).decode("utf-8")
    return hashed, salt.decode("utf-8")


def hasher_check(data, salt):
    new = bcrypt.hashpw(data.encode("utf-8"), salt.encode("utf-8")).decode("utf-8")
    return new


def DBDropCourse(key):
    dbCourses.delete(key)
    return True


def CourseDataExtractor(crns: str, Semester, Year, chat_id, name):
    # print(crns)
    # crns = crns.split(",")
    row = []

    for crn in crns:
        if crn != "":
            crn = crn.strip()
            CustomSemester = f"{Semester}{Year}--{crn}"
            print(CustomSemester)
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
            data["Platform"] = "Web"
            data["CRN"] = crn
            row.append(data)
    return row


def DBAddCourse(crns: str, Semester, Year, chat_id, name):
    Course_Info = CourseDataExtractor(crns, Semester, Year, chat_id, name)
    dbDumpData.put_many(Course_Info)
    print("Done")
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


def CoursesAPI(department):
    Departments = departments(False)
    if department in Departments:
        res = dbBanner.fetch({"Department": Departments[department]})
        courses = res.items

        # fetch until last is 'None'
        while res.last:
            res = dbBanner.fetch(last=res.last)
            courses += res.items
        return courses
    else:
        raise RuntimeError("Department Not Found")


def CoreAPI(core):
    Options = [
        "Pathways 1 - Sci. Encounters",
        "Humanities and Social Sciences",
        "Pathways 2 - Cult. Encounters",
        "Arab World Studies",
        "Arab World Studies - Egypt",
        "Global Studies",
        "Core Capstone",
    ]
    if core in Options:
        res = dbBanner.fetch({"Category": core})
        courses = res.items

        # fetch until last is 'None'
        while res.last:
            res = dbBanner.fetch(last=res.last)
            courses += res.items
        return courses
    else:
        raise RuntimeError("Department Not Found")


def SemDate():
    date = datetime.now()
    month = date.month
    year = date.year
    day = date.day

    if (month > 1 and day > 8) and month < 3:
        # Spring
        Semesters = [
            "Spring" + " " + str(year),
            "Summer" + " " + str(year),
            "Fall" + " " + str(year),
            "Winter" + " " + str(year + 1),
        ]
    elif month >= 12:
        # Winter
        year = year + 1
        Semesters = [
            "Winter" + " " + str(year),
            "Spring" + " " + str(year),
            "Summer" + " " + str(year),
            "Fall" + " " + str(year),
        ]
    elif month <= 1 and day <= 8:
        # Winter
        Semesters = [
            "Winter" + " " + str(year),
            "Spring" + " " + str(year),
            "Summer" + " " + str(year),
            "Fall" + " " + str(year),
        ]
    elif (month >= 6 and day > 6) or (month <= 9 and day <= 7):
        # Fall
        Semesters = [
            "Fall" + " " + str(year),
            "Winter" + " " + str(year + 1),
            "Spring" + " " + str(year + 1),
            "Summer" + " " + str(year + 1),
        ]

    elif (month == 5) or (month == 6 and day <= 6):
        # Summer
        Semesters = [
            "Summer" + " " + str(year),
            "Fall" + " " + str(year),
            "Winter" + " " + str(year + 1),
            "Spring" + " " + str(year + 1),
        ]

    return Semesters


def CRN_lookup(crn, semester):
    semester = str(semester).split(" ")
    semester = semester[0] + str(semester[1])
    key = semester + "--" + crn
    print(key)
    course = dbBanner.get(key)
    if course == None:
        raise RuntimeError("Course Not Found")
    else:
        msg = f'{course["Title"]} | {course["Section"]} | {course["Instructor"]}'
        return msg

    # fetch until last is 'None'
