import os
from requests import post
from json import dumps
from deta import Deta
from datetime import datetime

project = Deta()


# def Semcode():
#     date = datetime.now()
#     month = date.month
#     year = date.year
#     day = date.day

#     if (
#         (month == 1 and day == 7)
#         or (month == 1 and day >= 10 and day <= 24)
#         or (month == 1 and day >= 29)
#         or (month == 2 and day <= 8)
#     ):
#         # Spring
#         SemesterCode = str(year) + "20"
#         Sem = f"Spring{year}--"
#     elif month == 12 and day >= 10 and day <= 14:
#         # Winter
#         SemesterCode = str(year + 1) + "15"
#         Sem = f"Winter{year+1}--"
#     elif month == 1 and day <= 3:
#         # Winter
#         SemesterCode = str(year) + "15"
#         Sem = f"Winter{year}--"
#     elif (
#         (month == 6 and day >= 13 and day < 27)
#         or (month == 8 and day >= 28)
#         or (month == 9 and day < 8)
#     ):
#         # Fall
#         SemesterCode = str(year + 1) + "10"
#         Sem = f"Fall{year}--"

#     elif (month >= 5 and day < 20) and (month == 6 and day <= 6):
#         # Summer
#         SemesterCode = str(year) + "30"
#         Sem = f"Summer{year}--"
#     else:
#         raise Exception("Not a regestration Period..!!")
#     return Sem, SemesterCode


def sender():
    # Sem, Semester = Semcode()
    Subjects = [
        "ACCT",
        "AIAS",
        "AMST",
        "ANTH",
        "APLN",
        "ARIC",
        "ALIN",
        "ALNG",
        "ALWT",
        "ARCH",
        "BIOL",
        "BIOT",
        "BADM",
        "CHEM",
        "CSCE",
        "CENG",
        "CORE",
        "DSCI",
        "ECON",
        "EDUC",
        "EGPT",
        "ECNG",
        "ENGR",
        "ECLT",
        "ENTR",
        "ENVE",
        "FILM",
        "FINC",
        "FLNG",
        "GWST",
        "GHHE",
        "DSGN",
        "HIST",
        "CEMS",
        "JRMC",
        "LAW",
        "LALT",
        "LING",
        "MGMT",
        "MOIS",
        "MKTG",
        "MACT",
        "MENG",
        "MEST",
        "MRS",
        "MUSC",
        "NANO",
        "OPMG",
        "PENG",
        "PHDS",
        "PHDE",
        "PHIL",
        "PHYS",
        "POLS",
        "PSYC",
        "PPAD",
        "RHET",
        "RCSS",
        "SCI",
        "SEMR",
        "SOC",
        "GREN",
        "THTR",
        "TVDJ",
        "ARTV",
    ]

    # last_updated_db = project.Base("Stats")
    # res = last_updated_db.fetch()
    # last_updated_data = res.items

    # while res.last:
    #     res = last_updated_db.fetch(last=res.last)
    #     last_updated_data += res.items

    z = 8  # Number of subjects to send at a time
    for m in range(0, len(Subjects), z):
        try:
            payload = dumps(Subjects[m : m + z])
            print(payload)
            res = post(
                "https://regnotifyfinal-1-b1004847.deta.app/notifier/A",
                data=payload,
                timeout=0.9,
            )

            # payload = dumps(Subjects[m + z : m + 2 * z])
            # res = post(
            #     "https://regnotifyfinal-1-b1004847.deta.app/notifier/B",
            #     data=payload,
            #     timeout=0.75,
            # )
        except:
            pass

    print("CRON Sent to Notifier Successfully")


def last_updated():
    stats = project.Base("Stats")
    data = stats.fetch().items
    return data


def db_stats():
    users_db = project.Base("Users")
    res = users_db.fetch()
    users_data = res.items
    while res.last:
        res = users_db.fetch(last=res.last)
        users_data += res.items
    num_users = len(users_data)
    web_users = len([i for i in users_data if i["Username"] != None])
    telegram_users = len([i for i in users_data if i["Username"] == None])

    # Registered Courses
    courses_db = project.Base("Courses")
    res = courses_db.fetch()
    courses_data = res.items
    while res.last:
        res = courses_db.fetch(last=res.last)
        courses_data += res.items

    num_courses = len(courses_data)

    Semesters = {}
    for course in courses_data:
        try:
            Semesters[str(course["CustomSemester"]).split("--")[0]] += 1
        except:
            Semesters[str(course["CustomSemester"]).split("--")[0]] = 1

    # Banner Courses
    banner_db = project.Base("Banner")
    res = banner_db.fetch()
    banner_data = res.items
    while res.last:
        res = banner_db.fetch(last=res.last)
        banner_data += res.items
    num_banner_courses = len(banner_data)

    # Last Updated
    Unique_Semesters = Semesters.keys()
    last_updated_db = project.Base("Stats")
    res = last_updated_db.fetch()
    last_updated_data = res.items
    while res.last:
        res = last_updated_db.fetch(last=res.last)
        last_updated_data += res.items
    latest_update = {}
    for i in last_updated_data:
        if str(i["Semester"]).split("--")[0] in Unique_Semesters:
            try:
                if i["Time"] < latest_update[str(i["Semester"]).split("--")[0]]:
                    latest_update[str(i["Semester"]).split("--")[0]] = i["Time"]
            except:
                latest_update[str(i["Semester"]).split("--")[0]] = i["Time"]

    data = {
        "Total_Num_Users": num_users,
        "Web_Users": web_users,
        "Telegram_Only_Users": telegram_users,
        "Total_Courses_Registered": num_courses,
        "Num_Courses_Per_Semester": Semesters,
        "Total_Banner_Courses": num_banner_courses,
        "Latest_Update": latest_update,
    }
    # payload = dumps(data)
    return data
