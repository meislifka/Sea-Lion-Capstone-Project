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
import random

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SECRET_KEY"] = 'super secret key'
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set path of app.py to use for database connections
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER=os.path.join(BASE_DIR, "static/images")


def register_user_to_db(fName, lName, phoneNumber, occupation, email, username, password):
    db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO users(fName, lName, phoneNumber, occupation, email, username, password) values (?,?,?,?,?,?,?)', (fName, lName, phoneNumber, occupation, email, username, password))
    conn.commit()
    conn.close()
    
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
    message = None
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
        cur.execute('SELECT * FROM users WHERE username=?', [username])
        entry = cur.fetchall()
        if(len(password)<8):
            message = "Password must be longer than 8 characters"
            return render_template('register.html', message=message)
        else:
            #IT CORRECTLY IDENTFIES IF A USERNAME IS ALREADY IN THE TABLE AND DOESNT ADD IT BUT THE ERROR MESSAGE WONT THROW --HELP
            if len(entry) == 0:
                message = "Registration Successful!"
                hashedpassword = generate_password_hash(password)
                register_user_to_db(fName, lName, phoneNumber, occupation, email, username, hashedpassword)  
                conn.close()  
                return redirect(url_for('home'))
            else:
                message = "ERROR: Username taken. Please try again."
            conn.close()
    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':  
        session.clear()   
        username = request.form['username']
        password = request.form['password']
        db_path = os.path.join(BASE_DIR, "database.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor() 
        cur.execute('SELECT * FROM users WHERE username=?', [username])
        entry = cur.fetchall()
        message = ""
        if(entry):
            if(check_password_hash(entry[0][6],password)):
                message = "Login Successful!"
                session["username"] = request.form.get("username")
                #return redirect(url_for('homelogged'))
            else:
                message = 'ERROR: Invalid Credentials. Incorrect Password. Please try again.'
        else:
               message = 'ERROR: Invalid Credentials. Username does not exist. Please try again.'
        conn.close()
    return render_template('login.html', message=message)

@app.route('/encounter', methods=['GET','POST'])
def encounter():
    if request.method == 'POST':
            # Connect to database
            db_path = os.path.join(BASE_DIR, "sealions.db")
            con = sqlite3.connect(db_path)
            db = con.cursor()
            temp1 = db.execute("SELECT max(ID) from encounter")
            temp2 = db.fetchone()
            name = int(temp2[0]) + 1
            # Gather info from user
            user = session["username"]
            sealion_id = (random.randint(0,9))
            year = request.form.get('year')
            if request.form.get('year') == "":
                return render_template('encounter.html', error="Must input year")
            month = request.form.get('month')
            if request.form.get('month') == "":
                return render_template('encounter.html', error="Must input month")
            day = request.form.get('day')
            if request.form.get('day') == "":
                return render_template('encounter.html', error="Must input day")
            timeofday = request.form.get('timeofday')
            if request.form.get('timeofday') == "":
                return render_template('encounter.html', error="Must input timeofday")
            location = request.form.get('location')
            if request.form.get('location') == "":
                return render_template('encounter.html', error="Must input location")
            # check if the post request has the file part
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
                fileVar = "ID" + str(sealion_id) + "_E" + str(name) + ".jpg"
                filename = secure_filename(fileVar)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # add data into database
            db.execute("INSERT INTO encounter (ID, user, sealion_id, year, month, day, timeofday, location) VALUES(?,?,?,?,?,?,?,?)",(name, user, sealion_id, request.form.get('year'), request.form.get('month'), request.form.get('day'), request.form.get('timeofday'), request.form.get('location')))
            # commits insert into database
            con.commit()
            return render_template('encounterpost.html', name=name, user=user, sealion_id=sealion_id, year=year, month=month, day=day, timeofday=timeofday, location=location)
    else:
        if session.get("username")==None:
            return redirect(url_for('login'))
        return render_template('encounter.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for handling the search page logic
@app.route('/search', methods=["POST", "GET"])
def search():
    message = None
    if request.method == 'POST':
        
        db_path = os.path.join(BASE_DIR, "sealions.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor() 
        loc = request.form['location']
        sID = request.form['sealion_id']
        mon = request.form['month']
        ye = request.form['year']

        
        if(loc !="" and sID !="" and mon !="" and ye !=""):#specify all
            cur.execute('SELECT * FROM encounter WHERE location=? and month =? and sealion_id =? and year =?', [loc,mon,sID,ye])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry) 
        elif(loc !="" and sID !="" and mon !=""): #No year
            cur.execute('SELECT * FROM encounter WHERE location=? and month =? and sealion_id =?', [loc,mon,sID])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry) 
        elif(loc !="" and sID !="" and ye !=""): #No month
            cur.execute('SELECT * FROM encounter WHERE location=? and sealion_id =? and year =?', [loc,sID,ye])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry) 
        elif(loc !="" and mon !="" and ye !=""): #No sID
            cur.execute('SELECT * FROM encounter WHERE location=? and month =? and year =?', [loc,mon,ye])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry) 
        elif(sID !="" and mon !="" and ye !=""): #No loc
            cur.execute('SELECT * FROM encounter WHERE sealion_id=? and month =? and year =?', [sID,mon,ye])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry) 
        elif(mon !="" and sID !=""): #No year loc
            cur.execute('SELECT * FROM encounter WHERE month=? and sealion_id =?', [mon,sID])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry) 
        elif(sID !="" and ye !=""): #No month loc
            cur.execute('SELECT * FROM encounter WHERE sealion_id=? and year =?', [sID,ye])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry) 
        elif(sID !="" and loc !=""): #No month year
            cur.execute('SELECT * FROM encounter WHERE sealion_id=? and location =?', [sID,loc])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry)
        elif(mon !="" and ye !=""): #No sID loc
            cur.execute('SELECT * FROM encounter WHERE mon=? and year =?', [mon,ye])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry)
        elif(mon !="" and loc !=""): #No sID year
            cur.execute('SELECT * FROM encounter WHERE mon=? and location =?', [mon,loc])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry)
        elif(ye !="" and loc !=""): #No sID month
            cur.execute('SELECT * FROM encounter WHERE year=? and location =?', [ye,loc])
            entry = cur.fetchall() 
            return render_template('searchPost.html',entry = entry)
        elif(loc !=""):
            cur.execute('SELECT * FROM encounter WHERE location=?', [loc])
            entry = cur.fetchall()  
            return render_template('searchPost.html',entry = entry)  
        elif(sID != ""):
            cur.execute('SELECT * FROM encounter WHERE sealion_id=?', [sID])
            entry = cur.fetchall()  
            return render_template('searchPost.html',entry = entry) 
        elif(mon != ""):
            cur.execute('SELECT * FROM encounter WHERE month=?', [mon])
            entry = cur.fetchall()
            return render_template('searchPost.html',entry = entry) 
        elif(ye != ""):
            cur.execute('SELECT * FROM encounter WHERE year=?', [ye])
            entry = cur.fetchall()
            return render_template('searchPost.html',entry = entry) 
    return render_template('search.html', message=message)



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
    message = None
    if request.form.get('LogoutButton') == 'Logout':
        message = "Logout Successful!"
        session.clear()
        return redirect(url_for('home'))
    else:
        return render_template('logout.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)