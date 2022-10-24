from flask import Flask, render_template, redirect, url_for, request
import sqlite3
app = Flask(__name__)
con = sqlite3.connect("sealions.db")
db = con.cursor()
db.execute("CREATE TABLE sealions(name, age)")
db.execute("INSERT INTO sealions(name, age) VALUES('John', '21')")
con.commit()
info = db.execute("SELECT name FROM sealions")
info = info.fetchall()
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



if __name__ == '__main__':
    app.run(debug=True)