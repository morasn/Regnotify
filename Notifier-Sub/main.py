from fastapi import FastAPI, Request
from back import db_stats, sender, last_updated
from custom_semester import BannerRetriever

app = FastAPI()


@app.post("/__space/v0/actions")
def actions():
    sender()


@app.get("/stats")
def stats():
    data = db_stats()
    return data


@app.get("/last_updated")
def last_updated_send():
    data = last_updated()
    return data


@app.get("/CustomSemester")
async def CustomSemester(req: Request):
    api_data = await req.json()

    data = BannerRetriever(
        api_data["Subject"],
        api_data["Semester"],
        api_data["SemesterCode"],
        api_data["Course_ID"],
    )
    return data
