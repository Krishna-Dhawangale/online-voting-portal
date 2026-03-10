print("Script started.")
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import random

app = Flask(__name__)
app.secret_key = "secretkey"
print("Flask app initialized.")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'online_voting'
print("MySQL config set.")

try:
    mysql = MySQL(app)
    print("Successfully connected to MySQL.")
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    mysql = None  # Ensure mysql is None if connection fails


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        aadhaar = request.form['aadhaar']
        mobile = request.form['mobile']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO voters (name,aadhaar,mobile,password) VALUES (%s,%s,%s,%s)",
            (name, aadhaar, mobile, password),
        )
        mysql.connection.commit()
        return "Registration Successful"
    return render_template('register.html')


# ---------------- LOGIN + OTP ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM voters WHERE aadhaar=%s AND password=%s", (aadhaar, password)
        )
        user = cur.fetchone()

        if user:
            otp = str(random.randint(100000, 999999))
            cur.execute("UPDATE voters SET otp=%s WHERE aadhaar=%s", (otp, aadhaar))
            mysql.connection.commit()
            session['aadhaar'] = aadhaar
            return f"OTP (Simulation): <b>{otp}</b> <br><a href='/verify'>Verify OTP</a>"
        else:
            return "Invalid Login"
    return render_template('login.html')


# ---------------- OTP VERIFY ----------------
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        otp = request.form['otp']
        aadhaar = session['aadhaar']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM voters WHERE aadhaar=%s AND otp=%s", (aadhaar, otp))
        user = cur.fetchone()

        if user:
            session['voter_id'] = user[0]
            return redirect('/vote')
        else:
            return "Invalid OTP"
    return render_template('otp.html')


# ---------------- VOTING ----------------
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    voter_id = session.get('voter_id')

    cur = mysql.connection.cursor()
    cur.execute("SELECT has_voted FROM voters WHERE voter_id=%s", (voter_id,))
    voted = cur.fetchone()[0]

    if voted == 1:
        return "You have already voted!"

    cur.execute("SELECT * FROM candidates")
    candidates = cur.fetchall()

    if request.method == 'POST':
        cid = request.form['candidate']
        cur.execute(
            "INSERT INTO votes (voter_id,candidate_id) VALUES (%s,%s)", (voter_id, cid)
        )
        cur.execute("UPDATE voters SET has_voted=1 WHERE voter_id=%s", (voter_id,))
        mysql.connection.commit()
        return "Vote Submitted Successfully"

    return render_template('vote.html', candidates=candidates)


# ---------------- ADMIN ----------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        party = request.form['party']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO candidates (name,party) VALUES (%s,%s)", (name, party))
        mysql.connection.commit()
    return render_template('admin.html')


# ---------------- RESULT ----------------
@app.route('/result')
def result():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT candidates.name, COUNT(votes.vote_id)
        FROM candidates
        LEFT JOIN votes ON candidates.candidate_id = votes.candidate_id
        GROUP BY candidates.candidate_id
    """
    )
    data = cur.fetchall()
    return render_template('result.html', data=data)


if __name__ == '__main__':
    print("Entering main block.")
    app.run(debug=True)
    print("Flask app running at: http://127.0.0.1:5000/")

