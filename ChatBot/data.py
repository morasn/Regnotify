from datetime import datetime
from deta import Deta

deta = Deta()
dbBanner = deta.Base("Banner")
dbCourses = deta.Base("Courses")
dbUsers = deta.Base("Users")
dbToken = deta.Base("Token")


def current_time():
    time = datetime.now()
    time = time.strftime("%d/%m/%Y %H:%M:%S")
    return time


def CourseDataExtractor(crns: str, Semester, Year, chat_id, name):
    crns = crns.split(",")
    row = []
    for crn in crns:
        temp = dbBanner.get(f"{Semester}{Year}--{crn}")
        temp["Chat_ID"] = chat_id
        temp["UserName"] = name
        temp["Semester"] = Semester
        temp["Year"] = Year
        row.append(temp)
    return row


def current_time():
    time = datetime.now()
    time = time.strftime("%d/%m/%Y %H:%M:%S")
    return time


def DBCourseLookup(crn):
    CourseRow = dbCourses.get(crn)
    return CourseRow


def DBBannerLookup(crn):
    CourseRow = dbBanner.get(crn)
    return CourseRow


def DBUserLookup(chat_id):
    UserRow = dbUsers.get(str(chat_id))

    return UserRow


def DBAddCourse(Course_Info):
    time = current_time()
    deta = Deta()
    dbDumpData = deta.Base("DumpData")
    dbDumpData.put_many(Course_Info)

    crn = ""
    usercrn = Course_Info[0]["key"]
    UserRow = dbUsers.get(Course_Info[0]["Chat_ID"])
    for course in range(len(Course_Info)):
        CourseRow = DBCourseLookup(str(Course_Info[course]["key"]))
        if course != 0:
            usercrn = Course_Info[course]["key"] + "," + usercrn
        if CourseRow == None:
            dbCourses.put(
                {
                    "CRN": Course_Info[course]["CRN"],
                    # "Semester": Course_Info[course]["Semester"],
                    # "Year": Course_Info[course]["Year"],
                    "Chat_IDS": Course_Info[course]["Chat_ID"],
                    "key": Course_Info[course]["key"],
                    # "Title": Course_Info[course]["Title"],
                    # "Course_ID": Course_Info[course]["Course_ID"],
                    # "Section": Course_Info[course]["Section"],
                    "Time": time,
                }
            )

        else:
            crn = str(Course_Info[course]["key"]) + "," + str(crn)
            CourseChat_IDS = (
                str(CourseRow["Chat_IDS"]) + "," + str(Course_Info[course]["Chat_ID"])
            )
            dbCourses.put(
                {
                    "CRN": Course_Info[course]["CRN"],
                    # "Semester": Course_Info[course]["Semester"],
                    # "Year": Course_Info[course]["Year"],
                    "Chat_IDS": CourseChat_IDS,
                    "key": Course_Info[course]["key"],
                    # "Title": Course_Info[course]["Title"],
                    # "Course_ID": Course_Info[course]["Course_ID"],
                    # "Section": Course_Info[course]["Section"],
                    "Time": time,
                }
            )

    if UserRow == None:
        dbUsers.put(
            {
                "CHAT_ID": Course_Info[course]["Chat_ID"],
                "UserName": Course_Info[course]["UserName"],
                "CRN": usercrn,
                # "Semester": Course_Info[course]["Semester"],
                # "Year": Course_Info[course]["Year"],
                "Time": time,
                "key": Course_Info[course]["Chat_ID"],
            }
        )
    else:
        usercrn = usercrn + "," + UserRow["CRN"]
        dbUsers.put(
            {
                "CHAT_ID": Course_Info[course]["Chat_ID"],
                "UserName": Course_Info[course]["UserName"],
                "CRN": usercrn,
                # "Semester": Course_Info[course]["Semester"],
                # "Year": Course_Info[course]["Year"],
                "Time": time,
                "key": Course_Info[course]["Chat_ID"],
            }
        )

    stat = "Success"
    return stat


def UserRegCourses(chat_id):
    UserRow = DBUserLookup(chat_id=chat_id)
    crns = str(UserRow["CRN"]).split(",")
    UserCourses = []
    CourseDetail = []
    for crn in crns:
        UserCourses.append(DBCourseLookup(crn=crn))
        CourseDetail.append(DBBannerLookup(crn=crn))
    return UserRow, UserCourses, CourseDetail


def DBDropCourse(DropSelection: str, UserCourses):
    if "all" in DropSelection:
        DropSelection = DropSelection.split("---")[1]
        dbUsers.delete(DropSelection)
        for course in UserCourses:
            chat_ids = str(course["Chat_IDS"])
            chat_ids = chat_ids.split(",")
            NumIDS = len(chat_ids)
            if NumIDS == 1:
                dbCourses.delete(course["key"])
            else:
                chat_ids.remove(DropSelection)
                course["Chat_IDS"] = ",".join(chat_ids)
                dbCourses.put(course)
    else:
        # Remove Course CRN from User DB
        crn = str(DropSelection["CRN"])
        crn = crn.split(",")
        NumCRN = len(crn)
        if NumCRN == 1:
            dbUsers.delete(DropSelection["CHAT_ID"])
        else:
            crn.remove(UserCourses["key"])
            DropSelection["CRN"] = ",".join(crn)
            dbUsers.put(DropSelection)

        # Remove User Chat ID from Courses DB
        chat_ids = str(UserCourses["Chat_IDS"])
        chat_ids = chat_ids.split(",")
        NumIDS = len(chat_ids)
        if NumIDS == 1:
            dbCourses.delete(UserCourses["key"])
        else:
            chat_ids.remove(DropSelection["CHAT_ID"])
            UserCourses["Chat_IDS"] = ",".join(chat_ids)
            dbCourses.put(UserCourses)


def DBReader():
    res = dbCourses.fetch()
    CoursesDB = res.items

    # fetch until last is 'None'
    while res.last:
        res = dbCourses.fetch(last=res.last)
        CoursesDB += res.items

    return CoursesDB


def AddLogin(chat_id, name):
    UserRow = dbUsers.get(chat_id)
    if UserRow["WebUser"] == None:
        token = CreateToken(chat_id, name)
        msg = f"""Your temporary token is {token}.
Please add it on --- to complete the registration process."""
    else:
        # ResetPassword(chat_id)
        msg = ""
    return msg


def CreateToken(chat_id, name):
    token = generate_token(8)
    row = {"key": chat_id, "Chat_ID": chat_id, "Name": name, "Token": token}
    dbToken.put(row)
    return token


def generate_token(length):
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    token = "".join(secrets.choice(alphabet) for i in range(length))
    return token


def SemDate():
    date = datetime.now()
    month = date.month
    year = date.year
    day = date.day

    if (month > 0 and day > 8) and month < 3:
        # Spring
        Semester = "Spring"
    elif month >= 12:
        # Winter
        year = year + 1
        Semester = "Winter"
    elif month <= 1 and day <= 8:
        # Winter
        Semester = "Winter"
    elif (month == 6 and day > 6) or (month >= 8 and month <= 9):
        # Fall
        Semester = "Fall"
        year = year + 1

    elif month >= 5 or (month == 6 and day <= 6):
        # Summer
        Semester = "Summer"
    return Semester, year
