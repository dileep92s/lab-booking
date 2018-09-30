from flask import Flask, redirect, url_for, render_template, request
import sqlite3
import os
import datetime
import time

app = Flask(__name__)

@app.route('/')
def index():
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(1)
    today = datetime.datetime.strftime(today,'%d-%m-%Y') 
    tomorrow = datetime.datetime.strftime(tomorrow,'%d-%m-%Y')

    rows = cursor.execute("SELECT * from bookings WHERE date == ?", (today,))
    booked_slots_today = []
    for row in rows:
        booked_slots_today.append((row[0], row[1], row[2], row[5]))

    rows = cursor.execute("SELECT * from bookings WHERE date == ?", (tomorrow,))
    booked_slots_tomorrow = []
    for row in rows:
        booked_slots_tomorrow.append((row[0], row[1], row[2], row[5]))

    return render_template("index.html", booked_slots_today=booked_slots_today, booked_slots_tomorrow=booked_slots_tomorrow)

@app.route('/book', methods=['POST'])
def book_slot():
    if request.method == 'POST':
        
        user = request.form['user']
        begin = int(request.form['begin'])
        end = int(request.form['end']) - 1

        if end <= begin:
            return render_template("error.html")

        lab = request.form['lab']
        
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(1)
        today = datetime.datetime.strftime(today,'%d-%m-%Y') 
        tomorrow = datetime.datetime.strftime(tomorrow,'%d-%m-%Y')

        date = int(request.form['date'])
        if date == 0 :
            target = today
        else:
            target = tomorrow

        rows = cursor.execute("SELECT * from bookings WHERE date == ?", (target,))
        busy_slots = []
        for row in rows:
            slots = list(range(row[1], row[2]+1))
            busy_slots.extend(slots)

        for slot in range(begin, end+1):
            if slot in busy_slots:
                return render_template("error.html")

        cursor.execute("INSERT INTO bookings VALUES (?,?,?,?,?,?)", (user, begin, end, target, lab, time.time()) )
        conn.commit()

        return redirect(url_for('index'))

@app.route('/del/', )
def delete_slot():
    if request.method == 'GET':
        uid = request.args.get('uid')
        cursor.execute("DELETE FROM bookings WHERE timestamp == ?", (uid,) )
        conn.commit()

    return redirect(url_for('index'))

def create_database(database):    
    if not os.path.exists(database):
        conn = sqlite3.connect(database, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE bookings (user TEXT, begin INTEGER, end INTEGER, date TEXT, lab TEXT, timestamp REAL)''')
        conn.commit()
    else:
        conn = sqlite3.connect(database, check_same_thread=False)
        cursor = conn.cursor()
    return conn, cursor


if __name__ == '__main__':
    conn, cursor = create_database("booking.db")
    busy_slots = []
    booked_slots = []
    app.run(debug = True)
    conn.close()