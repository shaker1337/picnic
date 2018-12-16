import os
import re
from flask import Flask, jsonify, render_template, request, session, redirect
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from datetime import datetime
import json
from werkzeug.datastructures import ImmutableMultiDict

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///picnic.db")
marker1=[]

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    rows=db.execute("SELECT * from places ORDER by place_id DESC")

    return render_template("index.html", rows=rows)

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/join", methods=["GET", "POST"])
def join():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("alert.html", alert_message="Must provide username."), 400
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("alert.html", alert_message="Must provide password."), 400
            # Ensure password was submitted
        elif not request.form.get("confirmation"):
           return render_template("alert.html", alert_message="Must provide password confirmation."), 400
        # Ensure password and confirmation match
        elif not request.form.get("password")==request.form.get("confirmation"):
            return render_template("alert.html", alert_message="Password and confirmation must match."), 400
        elif db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username")):
            return render_template("alert.html", alert_message="must provide username"), 400
        hash=generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    return render_template("join.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("alert.html", alert_message="Must provide username."), 400

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("alert.html", alert_message="Must provide password."), 400

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("alert.html", alert_message="Username or password is incorrect."), 400

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/add_place", methods=["GET", "POST"])
def add_place():
    return render_template("add_place.html")

@app.route("/add_data", methods=["POST"])
def add_data():
    place_name=request.form["place_name"]
    description=request.form["description"]
    position= request.form["position"].strip("()")
    marker_lat, marker_lng=position.split(",")
    marker_lat=float(marker_lat)
    marker_lng=float(marker_lng)
    user=session["user_id"]
    db.execute("INSERT into places(user_id, description, place_name, marker_lat, marker_lng) VALUES(:user, :description, :place_name, :marker_lat, :marker_lng)",
    user=user, description=description, place_name=place_name, marker_lat=marker_lat, marker_lng=marker_lng)
    return render_template("add_place.html")

@app.route("/generate_markers",methods=["POST"])
def generate_markers():
    rows= db.execute("SELECT * from places")
    print(rows)
    return jsonify(rows)

def errorhandler(e):
    """Handle error"""
    return render_template("alert.html", alert_message="error")


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

@app.route("/goto")
def goto():
    lat=request.args.get('lat')
    lng=request.args.get('lng')
    LatLng=[lat, lng]
    print(lat)
    print(lng)
    return render_template("goto.html",lat=lat,lng=lng)