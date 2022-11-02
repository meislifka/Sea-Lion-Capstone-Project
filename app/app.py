from calendar import month
import os
from re import template
# from tkinter.tix import INTEGER, TEXT
from flask import Flask, render_template, redirect, url_for, request, flash, session
import sqlite3
from flask_session import Session
from werkzeug.utils import secure_filename
import os.path

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SECRET_KEY"] = 'super secret key'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set path of app.py to use for database connections
BASE_DIR=os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = 'static\images'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def register_user_to_db(fName, lName, phoneNumber, occupation, email, username, password):
    db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO users(fName, lName, phoneNumber, occupation, email, username, password) values (?,?,?,?,?,?,?)', (fName, lName, phoneNumber, occupation, email, username, password))
    conn.commit()
    conn.close()
    
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# check_same_thread=False ensures db commands run anywhere in file
con = sqlite3.connect("sealions.db", check_same_thread=False)
db = con.cursor()
# con.commit()

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about/')
def about():
    return render_template('about.html')

# Route for handling the register page logic
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        fName = request.form['fname']
        lName = request.form['lname']
        phoneNumber = request.form['phoneNumber']
        occupation = request.form['occupation']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        register_user_to_db(fName, lName, phoneNumber, occupation, email, username, password)
        return redirect(url_for('home'))

    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':     
        username = request.form['username']
        password = request.form['password']
        db_path = os.path.join(BASE_DIR, "database.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor() 
        cur.execute('SELECT rowid FROM users WHERE username=? AND password=?', (username, password))
        entry = cur.fetchall()
        if len(entry) == 0:
            error = 'Invalid Credentials. Please try again.'
        else:
            session["username"] = request.form.get("username")
            return redirect(url_for('home'))
        conn.close()
    return render_template('login.html', error=error)

@app.route('/encounter', methods=['GET','POST'])
def encounter():
    if request.method == 'POST':
        # Gather info from user
        name = request.form.get('name')
        user = request.form.get('user')
        sealion_id = request.form.get('sealion_id')
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day')
        timeofday = request.form.get('timeofday')
        location = request.form.get('location')
        # add data into database
        db_path = os.path.join(BASE_DIR, "sealions.db")
        con = sqlite3.connect(db_path)
        db = con.cursor()
        db.execute("INSERT INTO encounter (ID, user, sealion_id, year, month, day, timeofday, location) VALUES(?,?,?,?,?,?,?,?)",(request.form.get('name'), request.form.get('user'), request.form.get('sealion_id'), request.form.get('year'), request.form.get('month'), request.form.get('day'), request.form.get('timeofday'), request.form.get('location')))
        # commits insert into database
        con.commit()
        return render_template('encounterpost.html', name=name, user=user, sealion_id=sealion_id, year=year, month=month, day=day, timeofday=timeofday, location=location)
    else:
        return render_template('encounter.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/image', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('image.html')
    else:
        return render_template('image.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    session["username"] = None
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)