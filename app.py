from flask import Flask, render_template, redirect, session
import mysql.connector
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.secret_key = "hemmelig-nokk"

# DB-tilkobling
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="ludde",
        password="123Akademiet",
        database="handleliste_db"
    )

# Hovedside
@app.route("/")
def index():
    return render_template("index.html")

# Registrering
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        bruker = form.name.data
        brukerbruker = form.username.data
        passord = form.password.data

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO brukere (bruker, passord) VALUES (%s, %s)",
            (bruker, passord)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html", form=form)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        brukerbruker = form.username.data
        passord = form.password.data

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT bruker FROM brukere WHERE bruker=%s AND passord=%s",
            (brukerbruker, passord)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['bruker'] = user[0]
            return redirect("/velkommen")
        else: 
            form.username.errors.append("Feil brukernavn eller passord")

    return render_template("login.html", form=form)

# Velkomstside (krever login)
@app.route("/velkommen")
@app.route("/velkommen/<int:id>")
def velkommen(id=None):
    bruker = session.get('bruker')
    if not bruker:
        return redirect("/login")
    
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    #henter alle smaker
    cur.execute("SELECT * FROM monster_smaker")
    monster_info = cur.fetchall()

    vaglt_monster = None

    #hvis id finnes
    if id is not None:
        cur.execute("SELECT * FROM monster_smaker WHERE id = %s", (id,))
        vaglt_monster = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "velkommen.html", 
        name=bruker,
        monster_liste=monster_info,
        valgt_monster=vaglt_monster
    )


if __name__ == "__main__":
    app.run(debug=True)