from fastapi import FastAPI
from back import db_stats, sender, last_updated

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
