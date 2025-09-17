from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
import random, re

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb+srv://aditya:<adi@12345>@adityakumawat.cempluo.mongodb.net//fake_headline_app")

db = client.fake_headline_app
users_collection = db.users


TEMPLATES = [
     "{w1} and {w2} caught doing fun",
    "{w1} forget his wife because of {w2}",
    "Shocking: {w1} with {w2} at public washroom",
    "Exclusive: {w1} seen with {w2} in public taxi",
    "Scandal: {w1} and {w2} on police radar",
    "Viral: {w1} with {w2} — fans can’t believe it",
    "{w1} and {w2} secret meeting leaked",
    "People react: {w1} caught with {w2} in public",
    "{w1} denies rumors about {w2}, but truth is different",
    "Fans ask: Is {w1} cheating {w2}?",
    "Case Study: {w1} with {w2} — complete story inside",
    "Caught Live: {w1} and {w2} shocking moment",
    "Media Reports: {w1} forgot his wife for {w2}",
    "{w1} and {w2} create chaos in public taxi",
    "{w1} and {w2} romance story goes viral",
    "Breaking: {w1} and {w2} caught again",                           
]

PREFIXES = ["Breaking: ", "Exclusive: ", "Shocking: ", "Viral: ", "Scandal: "]


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).title()


def generate_headlines(w1: str, w2: str, n: int = 10):
    w1, w2 = clean(w1), clean(w2)
    base_seed = hash((w1.lower(), w2.lower())) & 0xFFFFFFFF
    rnd = random.Random(base_seed)
    out = []
    for i in range(n):
        tpl = rnd.choice(TEMPLATES)
        pref = rnd.choice(PREFIXES)
        out.append(pref + tpl.format(w1=w1, w2=w2))
        rnd.seed(base_seed + i + 1)
    return out


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/fun")
def headline_form():
    return render_template("index.html", w1="", w2="", headlines=[])


@app.route("/generate", methods=["POST"])
def generate():
    w1 = request.form.get("w1", "").strip()
    w2 = request.form.get("w2", "").strip()
    headlines = generate_headlines(w1, w2) if (w1 and w2) else []
    return render_template("index.html", w1=w1, w2=w2, headlines=headlines)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not (name and email and password and confirm_password):
            message = "All fields are required!"
        elif password != confirm_password:
            message = "Passwords do not match!"
        else:
            # Check if user already exists
            existing_user = users_collection.find_one({"email": email})
            if existing_user:
                message = "Email already registered!"
            else:
                users_collection.insert_one({
                    "name": name,
                    "email": email,
                    "password": password
                })
                return redirect("/login")

    return render_template("register.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = users_collection.find_one({"email": email, "password": password})
        if user:
            return redirect(url_for('headline_form'))
        else:
            message = "Invalid email or password!"

    return render_template("login.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)
