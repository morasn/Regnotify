from requests import post
from json import dumps
from deta import Deta
from datetime import datetime

project = Deta()


def sender(Sem,SemesterCode):
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

    if Sem is None:
        
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

            except:
                pass
    else:
        z = 8  # Number of subjects to send at a time
        for m in range(0, len(Subjects), z):
            try:
                data = {"Sem": Sem, "SemesterCode": SemesterCode, "data": Subjects[m : m + z]}
                payload = dumps(data)
                print(payload)
                res = post(
                    "https://regnotifyfinal-1-b1004847.deta.app/notifier/ManualUpdate",
                    data=payload,
                    timeout=0.9,
                )

            except:
                pass
    print("CRON Sent to Notifier Successfully")


def fetch_all_data(db):
    base = project.Base(db)
    res = base.fetch()
    data = res.items
    while res.last:
        res = base.fetch(last=res.last)
        data += res.items
    return data


def last_updated():
    data = fetch_all_data("DB_Update_Time")
    return data


def User_stats():
    users_data = fetch_all_data("Users")
    num_users = len(users_data)
    web_users = len([i for i in users_data if i["Username"] != None])
    telegram_users = len([i for i in users_data if i["Username"] == None])
    db = project.Base("Stats")
    db.put_many(
        [
            {
                "key": "Num_Users",
                "Category": "Total Number of User",
                "Value": num_users,
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "key": "Web_Users",
                "Category": "Web_Users",
                "Value": web_users,
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "key": "Telegram_Users",
                "Category": "Telegram_Users",
                "Value": telegram_users,
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        ]
    )

    return {"Done"}


def Courses_stats():
    courses_data = fetch_all_data("Courses")
    num_courses = len(courses_data)
    db = project.Base("Stats")
    db.put(
        {
            "key": "Num_Courses",
            "Category": "Total Number of Courses",
            "Value": num_courses,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    return {"Done"}


def Banner_stats():
    # Banner Courses
    banner_data = fetch_all_data("Banner")
    num_banner_courses = len(banner_data)

    Semesters = {}
    for banner in banner_data:
        try:
            Semesters[str(banner["Semester"]).split("--")[0]] += 1
        except:
            Semesters[str(banner["Semester"]).split("--")[0]] = 1

    # Last Updated
    Unique_Semesters = list(Semesters.keys())

    db = project.Base("Stats")
    db.put_many(
        [
            {
                "key": "Num_Banner_Courses",
                "Category": "Num_Banner_Courses",
                "Value": num_banner_courses,
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "key": "Num_Courses_Per_Semester",
                "Category": "Num_Courses_Per_Semester",
                "Value": Semesters,
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "key": "Unique_Semesters",
                "Category": "Unique_Semesters",
                "Value": Unique_Semesters,
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        ]
    )


def db_stats():
    Stats = fetch_all_data("Stats")
    for stat in Stats:
        if stat["key"] == "Num_Users":
            num_users = stat["Value"]
        elif stat["key"] == "Web_Users":
            web_users = stat["Value"]
        elif stat["key"] == "Telegram_Users":
            telegram_users = stat["Value"]
        elif stat["key"] == "Num_Courses":
            num_courses = stat["Value"]
        elif stat["key"] == "Num_Banner_Courses":
            num_banner_courses = stat["Value"]
        elif stat["key"] == "Num_Courses_Per_Semester":
            Semesters = stat["Value"]
        elif stat["key"] == "Unique_Semesters":
            Unique_Semesters = stat["Value"]

    last_updated_data = fetch_all_data("DB_Update_Time")
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
    return data
