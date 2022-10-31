import os
from re import template
# from tkinter.tix import INTEGER, TEXT
from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static\images'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

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
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/encounter', methods=['GET', 'POST'])
def encounter():
    # First login, if verified redirect to submit an encounter
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('encountersubmit'))
    return render_template('login.html', error=error)

@app.route('/encountersubmit', methods=['GET','POST'])
def encountersubmit():
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
if __name__ == '__main__':
    app.run(debug=True)