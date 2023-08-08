from flask import (
    Flask,
    render_template,
    request,
    url_for,
    flash,
    redirect,
    # make_response,
    session,
    jsonify,
)


# from json import dumps
import os
from WebBack import (
    get_token,
    add_user,
    authenticate,
    get_courses,
    DBDropCourse,
    DBAddCourse,
    CoursesAPI,
    CoreAPI,
    SemDate,
    CRN_lookup,
)
from schedule_builder import schedule_function
from var import departments

from BotSender import CreateToken
from datetime import timedelta

app = Flask(__name__, template_folder="templates")

app.config["SECRET_KEY"] = "os.urandom(24).hex()"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=9999)


def IsLoggedIn():
    if not session.get("name") or not session.get("chatid"):
        raise RuntimeError("No session")
    else:
        return True


@app.route("/")
def index():
    try:
        IsLoggedIn()
        return redirect(url_for("home"))
    except RuntimeError:
        return redirect(url_for("login"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["action"] == "login":
            username = request.form["username"]
            password = request.form["password"]

            if username == "" or password == "":
                flash("Please enter your name and your password.")
                return render_template("login.html")
            else:
                chat_id, name = authenticate(username, password)
                if chat_id == None:
                    flash(
                        "The username or password you entered is incorrect. Please try again."
                    )
                    return render_template("login.html")
                else:
                    session["chatid"] = chat_id
                    session["name"] = name
                    session.permanent = True
                    return redirect(url_for("home"))

        elif request.form["action"] == "register":
            return redirect(url_for("token"))

        elif request.form["action"] == "forget_passw":
            return redirect(url_for("password"))

    return render_template("login.html")


@app.route("/token/", methods=["GET", "POST"])
def token():
    if request.method == "POST":
        otp = [
            request.form["otp1"],
            request.form["otp2"],
            request.form["otp3"],
            request.form["otp4"],
        ]
        otp = "".join(otp)
        auth = get_token(otp)
        if auth["auth"] == True:
            session["temp_chat_id"] = str(auth["Chat_ID"])
            session["temp_name"] = str(auth["Name"])
            session.permanent = True

            return redirect(url_for("registration"))
        elif auth["auth"] == "Old-Token":
            flash("The token you entered is too old. Please enter the new token.")
            CreateToken(str(auth["Chat_ID"]), auth["Name"])
            return render_template("token.html")
        else:
            flash("The token you entered is invalid. Please try again.")
            return render_template("token.html")
    return render_template("token.html")


@app.route("/home/", methods=["GET", "POST"])
def home():
    try:
        IsLoggedIn()
    except RuntimeError:
        return redirect(url_for("login"))

    if request.method == "POST":
        form = request.form
        response = DBDropCourse(request.form["drop"])
        if response == True:
            flash("You have successfully dropped the course.")
            return redirect(url_for("home"))

    chat_id = session.get("chatid")
    name = session.get("name")

    courses = get_courses(chat_id=chat_id)

    return render_template("home.html", courses=courses, name=name)


@app.route("/registration/", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conf_password = request.form["confirm-password"]
        if password != conf_password:
            flash("The passwords you entered do not match. Please try again.")
            return render_template("registration.html")
        else:
            # response = add_user(username, password, request.cookies.get("temp_chat_id"))
            response = add_user(username, password, session.get("temp_chat_id"))
            if response == True:
                session["chatid"] = session.get("temp_chat_id")
                session["name"] = session.get("temp_name")
                session.permanent = True

                session.pop("temp_chat_id", None)
                session.pop("temp_name", None)

                flash("You have successfully registered.")
                return redirect(url_for("home"))
            else:
                flash(
                    "The username you entered is already taken. Please try again with a different username."
                )
                return render_template("registration.html")

    return render_template("registration.html")


@app.route("/password/", methods=["GET", "POST"])
def forget_passw():
    if request.method == "POST":
        username = request.form["username"]
        if username == "":
            flash("Please enter your username.")
            return render_template("password.html")
        else:
            # CreateToken(username)
            return redirect(url_for("token.html"))
    return render_template("password.html")


@app.route("/logout/")
def logout():
    try:
        IsLoggedIn()
    except RuntimeError:
        return redirect(url_for("login"))

    session.pop("chatid", None)
    session.pop("name", None)

    flash("You have successfully logged out.")
    return redirect(url_for("login"))


@app.route("/scheduler/", methods=["GET", "POST"])
def scheduler():
    if request.method == "POST":
        CRNS = []
        for i in range(1, 12):
            crns = request.form.getlist("CRNS" + str(i))
            for crn in crns:
                if crn != "":
                    CRNS.append(crn)

        if len(CRNS) == 0:
            flash("Please enter at least one CRN.")
            return render_template(
                "scheduler.html", departments=departments(True), iter=12
            )
        schedules = schedule_function(
            CRNS, start_time=request.form["StartTime"], end_time=request.form["EndTime"]
        )

        return render_template("scheduled.html", schedules=schedules)
    else:
        api_path = f"https://{os.getenv('DETA_SPACE_APP_HOSTNAME')}"
        return render_template(
            "scheduler.html", departments=departments(True), iter=12, api_path=api_path
        )


@app.route("/add/", methods=["GET", "POST"])
def add_course():
    if request.method == "POST":
        try:
            response = DBAddCourse(
                crns=request.form.getlist("crn"),
                chat_id=session.get("chatid"),
                name=session.get("name"),
                Semester=str(request.form["semester"]).split(" ")[0],
                Year=str(request.form["semester"]).split(" ")[1],
            )
            if response == True:
                return redirect(url_for("home"))
        except RuntimeError:
            flash("Please enter a valid CRN.")
            return redirect(url_for("home"))

    semesters = SemDate()
    api_path = f"https://{os.getenv('DETA_SPACE_APP_HOSTNAME')}"
    return render_template("add.html", semesters=semesters, api_path=api_path)


@app.route("/scheduler/courses/", methods=["GET"])
def get_department_courses():
    try:
        department = request.args.get("department")
        courses = [course for course in CoursesAPI(department=department)]
        return jsonify(courses)
    except RuntimeError:
        return jsonify({"error": "Invalid department."}), 400


@app.route("/scheduler/core/", methods=["GET"])
def get_core_courses():
    try:
        core = request.args.get("core")
        courses = [course for course in CoreAPI(core=core)]
        return jsonify(courses)
    except RuntimeError:
        return jsonify({"error": "Invalid department."}), 400


@app.route("/add/crn/", methods=["GET"])
def crn_lookup():
    try:
        crn = request.args.get("crn")
        semester = request.args.get("semester")
        msg = CRN_lookup(crn=crn, semester=semester)
        return msg
    except RuntimeError:
        return jsonify({"error": "Invalid CRN."}), 400


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/contact/")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=3000)
