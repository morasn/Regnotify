import requests
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
from deta import Deta
from datetime import datetime
from telegram import Bot
import os

deta = Deta()


def Semcode():
    date = datetime.now()
    month = date.month
    year = date.year
    day = date.day

    if (
        (month == 1 and day == 7)
        or (month == 1 and day >= 10 and day <= 24)
        or (month == 1 and day >= 29)
        or (month == 2 and day <= 8)
    ):
        # Spring
        SemesterCode = str(year) + "20"
        Sem = f"Spring{year}--"
    elif month == 12 and day >= 10 and day <= 14:
        # Winter
        SemesterCode = str(year + 1) + "15"
        Sem = f"Winter{year+1}--"
    elif month == 1 and day <= 3:
        # Winter
        SemesterCode = str(year) + "15"
        Sem = f"Winter{year}--"
    elif ((month == 6 and day >= 22) or (month == 7 and day <= 4)) or (
        (month == 8 and day >= 26) or (month == 9 and day <= 6)
    ):
        # Fall
        SemesterCode = str(year + 1) + "10"
        Sem = f"Fall{year}--"

    elif (month >= 5 and day >= 13 and day <= 21) or (
        month == 6 and day >= 3 and day <= 6
    ):
        # Summer
        SemesterCode = str(year) + "30"
        Sem = f"Summer{year}--"
    else:
        raise Exception("Not a regestration Period..!!")
    return Sem, SemesterCode


def DBReader(db, criteria):
    db = deta.Base(db)
    res = db.fetch(criteria)
    CoursesDB = res.items

    # fetch until last is 'None'
    while res.last:
        res = db.fetch(criteria, last=res.last)
        CoursesDB += res.items

    return CoursesDB


def BannerRetriever(subjects, Sem, SemesterCode):
    url = "https://ssb-prod.ec.aucegypt.edu/PROD/crse_submit.submit_proc"

    headers = CaseInsensitiveDict()
    headers["Accept"] = (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    )
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    # Subjects = []
    # for m in range(0, len(subjects)):
    Subject = "&sel_subj=".join(subjects)

    course_dict = []
    # for Subject in Subjects:
    data = f"term_in={SemesterCode}&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj={Subject}&sel_crse=&sel_title=&sel_schd=%25&sel_from_cred=&sel_to_cred=&sel_camp=%25&sel_levl=%25&sel_ptrm=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a"

    response = requests.post(url, headers=headers, data=data)

    # Parse the HTML content of the response using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the course table
    course_table = soup.find("table", {"class": "datadisplaytable"})

    # Find all the rows in the course table
    rows = course_table.find_all("tr")

    # Define a dictionary to store the course information

    # Loop through each row in the table
    for row in rows:
        # Find all the cells in the row
        cells = row.find_all("td")

        # Check if the row is a course row (i.e., it has 10 cells)
        if len(cells) == 18:
            # Extract the course information from the cells
            course_crn = cells[0].text.strip()
            course_department = cells[1].text.strip()
            course_id = course_department + " " + cells[2].text.strip()
            course_section = cells[3].text.strip()
            course_credits = cells[4].text.strip()
            course_title = cells[6].text.strip()
            course_days = cells[8].text.strip()
            course_time = cells[9].text.strip()
            course_capacity = cells[10].text.strip()
            course_actual = cells[11].text.strip()
            course_remaining = cells[12].text.strip()
            course_instructor = cells[13].text.strip()
            course_location = cells[15].text.strip()
            course_category = cells[16].text.strip()
            course_notes = cells[17].text.strip()

            if course_crn != "":
                # Add the course information to the dictionary
                course_dict.append(
                    {
                        "key": Sem + course_crn,
                        "CRN": course_crn,
                        "Department": course_department,
                        "Title": course_title,
                        "Section": course_section,
                        "Credits": course_credits,
                        "Days": course_days,
                        "Time": course_time,
                        "Capacity": course_capacity,
                        "Actual": course_actual,
                        "Remaining": course_remaining,
                        "Instructor": course_instructor,
                        "Location": course_location,
                        "Notes": course_notes,
                        "Course_ID": course_id,
                        "Category": course_category,
                        "Semester": Sem.replace("--", ""),
                    }
                )
    return course_dict


def StatsUpdate(departments):
    Sem, Semester = Semcode()
    Sem = Sem.replace("--", "")
    deta = Deta()
    db = deta.Base("DB_Update_Time")
    data = []
    for department in departments:
        data.append(
            {
                "key": Sem + "---" + department,
                "Department": department,
                "Semester": Sem,
                "Time": datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f"),
            }
        )
    for i in range(0, len(data), 25):
        db.put_many(data[i : i + 25])


def get_application():
    BotToken = os.getenv("TOKEN")

    application = Bot(BotToken)
    return application


async def Notifier(data):
    Sem, SemesterCode = Semcode()
    BannerDB = deta.Base("Banner")

    OldDB = DBReader("Banner", {"Department": data})
    NewDB = BannerRetriever(data, Sem, SemesterCode)

    old_db_dict = {old_dict["key"]: old_dict for old_dict in OldDB}
    new_db_changed = []
    new_db_added = []

    bot = get_application()
    async with bot:
        for new_dict in NewDB:
            old_dict = old_db_dict.get(new_dict["key"])
            if old_dict is None:
                new_db_added.append(new_dict)
            elif str(old_dict["Remaining"]) != str(new_dict["Remaining"]):
                new_db_changed.append(new_dict)
                chat_ids = DBReader("Courses", criteria={"CRN": new_dict["CRN"]})

                if chat_ids is not None:
                    for chat_id in chat_ids:
                        if int(new_dict["Remaining"]) == 0:
                            msg = f"""Unfortunately there are no seats remaining in the course {new_dict["Title"]} ({new_dict["Course_ID"]}) with section number {new_dict["Section"]} . However, there is still hope do not worry."""
                        else:
                            msg = f"""{new_dict["Remaining"]} Seats are now available in the course {new_dict["Title"]} ({new_dict["Course_ID"]}) with the instructor {new_dict["Instructor"]} and section number {new_dict["Section"]}. Hurry up to reserve the course.
                CRN is {new_dict["CRN"]} """
                        try:
                            await bot.send_message(chat_id=chat_id["Chat_ID"], text=msg)
                        except Exception as e:
                            print(e)
                            pass
        for m in range(0, len(new_db_added), 25):
            BannerDB.put_many(new_db_added[m : m + 25])

        for c in range(0, len(new_db_changed), 25):
            BannerDB.put_many(new_db_changed[c : c + 25])
    StatsUpdate(data)
