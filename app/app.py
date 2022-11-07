from calendar import month
import os
from re import template
# from tkinter.tix import INTEGER, TEXT
from flask import Flask, render_template, redirect, url_for, request, flash, session
import sqlite3
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
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
    error = None
    if request.method == 'POST':
        fName = request.form['fname']
        lName = request.form['lname']
        phoneNumber = request.form['phoneNumber']
        occupation = request.form['occupation']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        db_path = os.path.join(BASE_DIR, "database.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor() 
        #cur.execute('SELECT rowid FROM users WHERE username=? AND password=?', (username, password))
        cur.execute('SELECT * FROM users WHERE username=?', [username])
        entry = cur.fetchall()

        #IT CORRECTLY IDENTFIES IF A USERNAME IS ALREADY IN THE TABLE AND DOESNT ADD IT BUT THE ERROR MESSAGE WONT THROW --HELP
        print("LENGTH: " +str(len(entry)))
        if len(entry) == 0:
            print("MADE IT HERE")
            hashedpassword = generate_password_hash(password)
            register_user_to_db(fName, lName, phoneNumber, occupation, email, username, hashedpassword)  
            conn.close()  
            return redirect(url_for('home'))
        else:
            print("ACUTALLY HERE")
            error = 'Invalid Credentials. Please try again.' 
        conn.close()
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':     
        username = request.form['username']
        password = request.form['password']
        db_path = os.path.join(BASE_DIR, "database.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor() 
        #cur.execute('SELECT rowid FROM users WHERE username=? AND password=?', (username, password))
        cur.execute('SELECT * FROM users WHERE username=?', [username])
        entry = cur.fetchall()
        """
        if len(entry) == 0:
            error = 'Invalid Credentials. Please try again.'
        else:
            session["username"] = request.form.get("username")
            return redirect(url_for('home'))
        conn.close()

        """
        for i in entry:
            #print(i)
            print(i[6])
            if(check_password_hash(str(i[6]),password)):
                print("correct!")
                session["username"] = request.form.get("username")
                return redirect(url_for('home'))
            else:
                error = 'Invalid Credentials. Please try again.'
        conn.close()
    return render_template('login.html', error=error)

@app.route('/encounter', methods=['GET','POST'])
def encounter():
    if request.method == 'POST':
        db_path = os.path.join(BASE_DIR, "sealions.db")
        con = sqlite3.connect(db_path)
        db = con.cursor()
        # Gather info from user
        db.execute("select max(ID) from encounter")
        previous = db.fetchone()
        name = previous[0] + 1
        user = request.form.get('user')
        sealion_id = request.form.get('sealion_id')
        year = request.form.get('year')
        if int(year) > 2022:
            return render_template('encounter.html', error="year cant be in the future")
        month = request.form.get('month')
        if int(month) > 12:
            return render_template('encounter.html', error="month can't be greater than 12")
        day = request.form.get('day')
        if int(day) > 31:
            return render_template('encounter.html', error="day can't be greater than 31")
        timeofday = request.form.get('timeofday')
        location = request.form.get('location')
        # add data into database
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