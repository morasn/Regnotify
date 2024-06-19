from flask import Flask, request
from back import db_stats, sender, last_updated, User_stats, Banner_stats, Courses_stats
from custom_semester import BannerRetriever

app = Flask(__name__)


@app.route("/__space/v0/actions", methods=["POST"])
def actions():
    event = request.get_json()
    if event["event"]["id"] == "Notifier":
        sender()
        return {"Done": event["event"]["id"]}
    elif event["event"]["id"] == "UserStats":
        User_stats()
        return {"Done": event["event"]["id"]}
    elif event["event"]["id"] == "BannerStats":
        Banner_stats()
        return {"Done": event["event"]["id"]}
    elif event["event"]["id"] == "CoursesStats":
        Courses_stats()
        return {"Done": event["event"]["id"]}


@app.route("/stats", methods=["GET"])
def stats():
    data = db_stats()
    return data


@app.route("/last_updated", methods=["GET"])
def last_updated_send():
    print("Last Updated")
    data = last_updated()
    return data


@app.route("/CustomSemester", methods=["POST"])
async def CustomSemester():
    api_data = await request.get_json()

    data = BannerRetriever(
        api_data["Subject"],
        api_data["Semester"],
        api_data["SemesterCode"],
        api_data["Course_ID"],
    )
    return data


@app.route("/ForceUpdate", methods=["GET"])
def ForceUpdate():
    sender(None,None)
    return "Sent Successfully!"

@app.route("/ManualUpdate", methods=["GET"])
def ManualUpdate():
    Sem = request.args.get('Sem')
    SemesterCode = request.args.get('SemesterCode')
    sender(Sem=Sem, SemesterCode=SemesterCode)
    
    return "Sent Successfully!"