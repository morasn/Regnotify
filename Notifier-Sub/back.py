import os
from requests import post
from json import dumps
from deta import Deta


def sender():
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

    z = 12  # Number of subjects to send at a time
    for m in range(0, len(Subjects), z):
        try:
            payload = dumps(Subjects[m : m + z])
            res = post(
                "https://regnotifyfinal-1-b1004847.deta.app/notifier/",
                data=payload,
                timeout=1,
            )
        except:
            pass

    print("CRON Sent to Notifier Successfully")

def last_updated():
    project = Deta()
    stats = project.Base("Time")
    data = stats.fetch().items

    return data


def db_stats():
    project = Deta()
    users = project.Base("Users")
    users_data = users.fetch().items
    num_users = len(users_data)
    web_users = len([i for i in users_data if i["Username"] != None])
    telegram_users = len([i for i in users_data if i["Username"] == None])
    courses = project.Base("Courses")
    courses_data = courses.fetch().items
    num_courses = len(courses_data)

    banner = project.Base("Banner")
    num_banner_courses = len(banner.fetch().items)
    data = {
        "total_users": num_users,
        "web_users": web_users,
        "telegram_users": telegram_users,
        "total_courses": num_courses,
        "banner_courses": num_banner_courses,
    }
    # payload = dumps(data)
    return data
