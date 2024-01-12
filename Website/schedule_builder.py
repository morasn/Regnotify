import deta
import random

# Initialize the Deta project
project = deta.Deta()

# Initialize the Banner database
dbBanner = project.Base("Banner")


def schedule_function(Form_CRNS, start_time, end_time):
    Course_List = CoursesData(Form_CRNS, start_time, end_time)
    schedule_options = find_schedule_options(Course_List)
    random.shuffle(schedule_options)
    selected_schedules = schedule_options[:50]
    return selected_schedules


def CoursesData(Form_CRNS, start, end):
    Course_List = {}
    for course, CRNS in enumerate(Form_CRNS):
        Course_List[course] = []

        for i in CRNS:
            try:
                banner = dbBanner.get(i)
                if not time_filter(start, end, banner["Time"]):
                    continue
                data = {
                    "Title": banner["Title"],
                    "Course_ID": banner["Course_ID"],
                    "Instructor": banner["Instructor"],
                    "CRN": banner["CRN"],
                    "Days": banner["Days"],
                    "Time": banner["Time"],
                }
                Course_List[course].append(data)
            except KeyError:
                pass
    return Course_List


def find_schedule_options(courses):
    schedule_options = []
    current_schedule = []

    backtrack(list(courses.values()), current_schedule, schedule_options)

    return schedule_options


def backtrack(
    courses,
    current_schedule,
    schedule_options,
):
    if not courses:
        schedule_options.append(current_schedule.copy())
        return

    current_day_courses = courses.pop(0)

    for course in current_day_courses:
        if is_valid_option(course, current_schedule):
            current_schedule.append(course)
            backtrack(courses, current_schedule, schedule_options)
            current_schedule.pop()

    courses.insert(0, current_day_courses)


def is_same_section(course1, course2):
    return course1["Section"] == course2["Section"]


def is_valid_option(course, current_schedule):
    if course["Course_ID"] in ["RHET 1010", "Core 1010"]:
        for scheduled_course in current_schedule:
            if scheduled_course["Course_ID"] in ["RHET 1010", "CORE 1010"]:
                if course["Section"] != scheduled_course["Section"]:
                    return False

    for scheduled_course in current_schedule:
        scheduled_days = set(scheduled_course["Days"])
        current_days = set(course["Days"])

        if scheduled_days.intersection(current_days):
            if do_times_overlap(scheduled_course["Time"], course["Time"]):
                return False

    return True


def do_times_overlap(time1, time2) -> bool:
    start1, end1 = time1.split("-")
    start2, end2 = time2.split("-")

    start1 = convert_to_minutes(start1.strip())
    end1 = convert_to_minutes(end1.strip())
    start2 = convert_to_minutes(start2.strip())
    end2 = convert_to_minutes(end2.strip())

    return start1 < end2 and start2 < end1


def convert_to_minutes(time) -> int:
    hours, minutes = time.split(":")
    hours = int(hours)
    minutes = int(minutes.strip("pm").strip("am"))

    if time.endswith("pm") and hours != 12:
        hours += 12

    return hours * 60 + minutes


def time_filter(start, end, time) -> bool:
    start_course, end_courses = time.split("-")

    start_course = convert_to_minutes(start_course.strip())
    end_courses = convert_to_minutes(end_courses.strip())

    start = convert_to_minutes(start.strip())
    end = convert_to_minutes(end.strip())

    return start_course >= start and end_courses <= end
