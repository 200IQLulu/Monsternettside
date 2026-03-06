from flask import Flask, render_template, redirect, session
import mysql.connector



app = Flask(__name__)
app.secret_key = "Monster_er_digg"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/velkommen")
def velkommen():
    return render_template("velkommen.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def registrer():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)