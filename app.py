import os
from flask import Flask, render_template, redirect, session, abort, request
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash  # Hashing av passord
from werkzeug.utils import secure_filename
from forms import RegisterForm, LoginForm, MonsterForm


app = Flask(__name__)
app.secret_key = "hemmelig-nokk"

 #Instillinger for admin-bruker
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg"}
PASSWORD_HASH_METHOD = "scrypt"  # Algoritme som brukes for alle passord-hasher

# is_admin i databasen: 0 = vanlig bruker, 1 = admin
VANLIG_BRUKER = 0
ADMIN_BRUKER = 1


# DB-tilkobling
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="ludde",
        password="123Akademiet",
        database="handleliste_db"
    )

# Sørger for at admin-bruker finnes (is_admin = 1)
def ensure_admin_support():
    conn = get_conn()
    cur = conn.cursor()
    admin_password_hash = generate_password_hash(ADMIN_PASSWORD, method=PASSWORD_HASH_METHOD)

    # Kolonne is_admin: 0 = vanlig, 1 = admin (standard 0 for nye rader)
    cur.execute("SHOW COLUMNS FROM brukere LIKE 'is_admin'")
    has_is_admin = cur.fetchone() is not None
    if not has_is_admin:
        cur.execute(
            "ALTER TABLE brukere ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0"
        )

    cur.execute("SELECT bruker FROM brukere WHERE bruker = %s", (ADMIN_USERNAME,))
    admin_exists = cur.fetchone()
    if admin_exists:
        cur.execute(
            "UPDATE brukere SET passord = %s, is_admin = %s WHERE bruker = %s",
            (admin_password_hash, ADMIN_BRUKER, ADMIN_USERNAME),
        )
    else:
        cur.execute(
            "INSERT INTO brukere (bruker, passord, is_admin) VALUES (%s, %s, %s)",
            (ADMIN_USERNAME, admin_password_hash, ADMIN_BRUKER),
        )

    conn.commit()
    cur.close()
    conn.close()


# Går gjennom alle brukere og hasher passord som fortsatt er klartekst
def ensure_password_hashing():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT bruker, passord FROM brukere")
    users = cur.fetchall()

    for username, stored_password in users:
        # Sjekk om passordet allerede er hash (starter med pbkdf2: eller scrypt:)
        is_hashed = bool(stored_password) and (
            stored_password.startswith("pbkdf2:") or stored_password.startswith("scrypt:")
        )
        if not is_hashed:
            # Hash klartekst og erstatt i databasen
            cur.execute(
                "UPDATE brukere SET passord = %s WHERE bruker = %s AND passord = %s",
                (generate_password_hash(stored_password, method=PASSWORD_HASH_METHOD), username, stored_password),
            )

    conn.commit()
    cur.close()
    conn.close()


# Hovedside
@app.route("/")
def index():
    return render_template("index.html")

# Registrering av ny bruker
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        bruker = form.username.data
        # Hash passordet før det lagres — aldri klartekst i databasen
        passord_hash = generate_password_hash(form.password.data, method=PASSWORD_HASH_METHOD)

        conn = get_conn()
        cur = conn.cursor()
        # Nye brukere får alltid is_admin = 0 (vanlig bruker)
        cur.execute(
            "INSERT INTO brukere (bruker, passord, is_admin) VALUES (%s, %s, %s)",
            (bruker, passord_hash, VANLIG_BRUKER),
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html", form=form)

# Innlogging
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        brukerbruker = form.username.data
        passord = form.password.data

        conn = get_conn()
        cur = conn.cursor()
        # Hent bruker + is_admin (0 eller 1) fra databasen
        cur.execute(
            "SELECT bruker, passord, is_admin FROM brukere WHERE bruker=%s",
            (brukerbruker,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], passord):
            session['bruker'] = user[0]
            # Lagre 1 hvis admin, ellers 0
            session['is_admin'] = ADMIN_BRUKER if user[2] == ADMIN_BRUKER else VANLIG_BRUKER
            return redirect("/velkommen")
        else: 
            form.username.errors.append("Feil brukernavn eller passord")

    return render_template("login.html", form=form)

# Side som vises etter innlogging
@app.route("/velkommen")
def velkommen():

    bruker = session.get('bruker')

    if not bruker:
        return redirect("/login")  # Må være innlogget
    
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM monster_smaker")
    monster_info = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "velkommen.html", 
        name=bruker,
        monster_liste=monster_info,
        is_admin=session.get('is_admin', VANLIG_BRUKER),  # 1 = admin, 0 = vanlig
    )

# Detaljside for én monster-smak, f.eks. /velkommen/Ultra
@app.route("/velkommen/<string:smak>")
def monster_info(smak: str):
    bruker = session.get('bruker')
    if not bruker:
        return redirect("/login")

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM monster_smaker WHERE navn = %s", (smak,))
    monster = cur.fetchone()
    cur.close()
    conn.close()

    if not monster:
        abort(404)  # Finnes ikke i databasen

    return render_template(
        "monster_info.html",
        name=bruker,
        monster=monster,
        is_admin=session.get('is_admin', VANLIG_BRUKER),  # 1 = admin, 0 = vanlig
    )

# Starter nettsiden lokalt
if __name__ == "__main__":
    ensure_admin_support()      # Oppretter/oppdaterer admin med hashet passord
    ensure_password_hashing()   # Hasher gamle klartekst-passord ved oppstart
    app.run(debug=True)