from re import template
# from tkinter.tix import INTEGER, TEXT
from flask import Flask, render_template, redirect, url_for, request
import sqlite3
app = Flask(__name__)
# check_same_thread=False ensures db commands run anywhere in file
con = sqlite3.connect("sealions.db", check_same_thread=False)
db = con.cursor()
# db.execute("CREATE TABLE sealions(sealionID, sex, encounter)")
# db.execute("CREATE TABLE encounters(encounter, sealionID, year, month, day, timeofday, location)")
# db.execute("INSERT INTO sealions(name, age) VALUES('John', '21')")
# con.commit()
# CREATE TABLE sealion
#(
#    id INTEGER,
#    sex TEXT,
#    encounter TEXT,
#    encounter_id INTEGER,
#    PRIMARY KEY(id),
#    FOREGIN KEY(encounter_id) REFERENCES encounters(id)
#);

# CREATE TABLE encounter
#(
#    id INTEGER,
#    user TEXT,
#    sealion_id INTEGER,
#    year INTEGER,
#    month INTEGER,
#    day INTEGER,
#    timeofday INTEGER,
#    location TEXT,
#    PRIMARY KEY(id),
#    FOREGIN KEY(sealion_id) REFERENCES sealion(id)
#);

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about/')
def about():
    return render_template('about.html')

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/encounter', methods=['GET','POST'])
def encounter():
    if request.method == 'POST':
        # Gather info from user
        name = request.form.get('name')
        age = request.form.get('age')
        # add data into database
        db.execute("INSERT INTO sealions(name, age) VALUES(?,?)",(request.form.get('name'), request.form.get('age')))
        # commits insert into database
        con.commit()
        info = db.execute("SELECT name FROM sealions")
        info = info.fetchall()
        return render_template('encounterpost.html', name=name, age=age, info=info)
    else:
        return render_template('encounter.html')


if __name__ == '__main__':
    app.run(debug=True)