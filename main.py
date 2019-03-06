from flask import Flask, render_template, request, flash, get_flashed_messages
import sqlite3
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

global current_email
current_email = "@gmail.com"

global number_users
number_users = 0

global post_made_total
post_made_total = 0


UPLOAD_FOLDER_1 = 'C:/Users/Mareva Zenelaj/PycharmProjects/untitled1/static/images/members'
UPLOAD_FOLDER_2 = 'C:/Users/Mareva Zenelaj/PycharmProjects/untitled1/static/images/pets'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/profile")
def profile():
    connection = sqlite3.connect('database.db')
    cc = connection.cursor()
    global current_email
    cc.execute('SELECT name, surname, usrtel, nationality, bday, role FROM members WHERE email=?', [current_email])
    result = cc.fetchone()
    if result == None:
        return render_template("needlogin.html")
    else:
        connection.commit()
        surname = result[1]
        name = result[0]
        telno = result[2]
        nationality = result[3]
        bday = result[4]
        role = result[5]
        connection.close()
        return render_template("profile.html", name=name, surname=surname, birthday=bday, nationality=nationality,
                               email=current_email, tel=telno, role=role)


@app.route("/logout")
def logout():
    global current_email
    current_email = "@gmail.com"

    return render_template("log_out.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/editprofile", methods=['GET', 'POST'])
def editprofile():

    global current_email
    if current_email != "@gmail.com":
        return render_template('edit_profile.html')
    else:
        return render_template('needlogin.html')


@app.route("/updateprofile", methods=['GET', 'POST'])
def updateprofile():
    name = request.form['name']
    email = request.form['email']
    surname = request.form['surname']
    role = request.form['role']
    bday = request.form['bday']
    nationality = request.form['nationality']
    usrtel = request.form['usrtel']
    res = data_update(name, surname, email, nationality, usrtel, bday, role)

    if res == 0:
        return render_template('profile.html', name=name, surname=surname, usrtel=usrtel, nationality=nationality, email=email, bday=bday, role=role)
    else:
        return render_template('edit_profile.html')


@app.route("/post_results", methods=['GET', 'POST'])
def post_results():
    pet_name = request.form['pet_name']
    pet_type = request.form['pet_type']
    payment_ = request.form['payment']
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER_1, filename))
    filename_to_use = os.path.join(UPLOAD_FOLDER_1, filename)
    global current_email

    connection = sqlite3.connect('database.db')
    cc = connection.cursor()
    cc.execute("SELECT id, post_made FROM members WHERE email=?", [current_email])
    result = cc.fetchone()
    if result[0]:
        if result[1] is None:
            post_id = 1
        else:
            post_id = result[1] + 1
        global post_made_total
        post_made_total = post_made_total + 1
        cc.execute("INSERT INTO posts (id, pet_type, pet_name, payment, image_path, mem_id) VALUES(?,?,?,?,?,?);",
                   (post_made_total, pet_type, pet_name, payment_, filename_to_use, result[0]))
        cc.execute("UPDATE members SET post_made=? WHERE id=?",
                   (post_id, result[0]))
        connection.commit()
    connection.close()
    return render_template('edit_profile.html')


@app.route("/get_results", methods=['GET', 'POST'])
def get_results():
    email = request.form['email']
    confirmemail = request.form['confirmemail']
    password = request.form['password']
    name = request.form['name']
    surname = request.form['surname']
    if email != confirmemail:
        flash("Email and Comfirm Email entries should be the same!")
        return render_template('signup.html')
    else:

        global number_users
        number_users = number_users + 1
        print(number_users)
        res = data_entry(number_users, name, surname, email, password)
        if res == 1:
            global current_email
            current_email = email
            return render_template('index.html', name=name, surname=surname)
        else:
            return render_template('same_email.html')


@app.route("/check_login_info", methods=['GET', 'POST'])
def check_login_info():
    email_ = request.values['email']
    password_ = request.values['password']
    result = check_existing_data(email_, password_)
    if result is not None:
        name = result[0]
        surname = result[1]
        global current_email
        current_email = email_
        return render_template("index.html", name=name, surname=surname)
    else:
        return render_template("wrong_info.html")


@app.route("/home")
def home():
    return render_template("index.html")


def check_existing_data(email, password):
    connection = sqlite3.connect('database.db')
    cc = connection.cursor()
    cc.execute("""SELECT name, surname FROM members WHERE email=? AND password=?""", (email, password))
    result = cc.fetchone()
    connection.commit()
    cc.close()
    connection.close()
    return result


def data_entry(nr, name, surname, email, password):
    connection = sqlite3.connect('database.db')
    cc = connection.cursor()
    cc.execute("SELECT email FROM members WHERE email=?", [email])
    result = cc.fetchone()
    if result is None:
        cc.execute("INSERT INTO members (id, name, surname, email, password) VALUES(?,?,?,?,?);", (nr, name,
                                                                                                 surname, email, password))
        connection.commit()
        cc.close()
        connection.close()
        return 1
    else:
        cc.close()
        connection.close()
        return 0


def data_update(name, surname, email, nationality, usrtel, bday, role):
    connection = sqlite3.connect('database.db')
    cc = connection.cursor()
    cc.execute("UPDATE members SET name=?, surname=?, nationality=?, usrtel=?, bday=?, role=? WHERE email=?",
               (name, surname, nationality, usrtel, bday, role, email))
    res = cc.fetchone()
    connection.commit()
    cc.close()
    connection.close()
    if res == 1:
        return 1
    else:
        return 0


if __name__ == "__main__":
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS members(id INTEGER, name TEXT, surname TEXT, email TEXT, '
              'password TEXT, nationality TEXT, role TEXT, usrtel INTEGER, bday TEXT, post_made INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS posts(id INTEGER, pet_type TEXT, '
              'pet_name TEXT, payment INTEGER, image_path TEXT, mem_id INTEGER)')

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    #sess.init_app(app)
    app.run(debug=True)
