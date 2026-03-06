from flask import Flask, render_template, redirect, session
import mysql.connector



app = Flask(__name__)
app.secret_key = "Monstererdigg"

@app.route("/")
def index():
    return "Hello"

if __name__ == "__main__":
    app.run(debug=True)