from turtle import title
from flask import Flask, render_template, request, redirect, url_for, session,flash,get_flashed_messages
from flask_mysqldb import MySQL
import MySQLdb.cursors
import psycopg2 #pip install psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_HOST = "localhost"
DB_NAME = "account"
DB_USER = "postgres"
DB_PASS = "Tonymin2710"

app.secret_key = 'dueJuly'
connect = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
@app.route('/')
def adminindex(): 
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM request')
    list_requests = cursor.fetchall()
    return render_template('adminindex.html',list_requests=list_requests)
@app.route('/add_userrequest', methods=['POST'])
def add_userrequest():
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        userofticket=request.form['userofticket']
        dateofticket=request.form['dateofticket']
        requesttype=request.form['requesttype']
        title=request.form['title']
        name = request.form['name']
        address = request.form['address']
        phonenumber = request.form['phonenumber']
        emailofticket = request.form['emailofticket']
        userrequest=request.form['userrequest']
        status=request.form['status']
        cursor.execute("INSERT INTO request (userofticket, dateofticket, requesttype, title, name, address, phonenumber,emailofticket,userrequest,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (userofticket,dateofticket, requesttype,title,name,address,phonenumber,emailofticket,userrequest,status))
        connect.commit()
        flash('Userrequest Added successfully')
        return redirect(url_for('adminindex'))
@app.route('/edit/<id>',methods=['GET','POST'])
def edit_userrequest(id):
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM request WHERE id = %s', (id))
    data = cursor.fetchall()
    cursor.close()
    print(data[0])
    return render_template('adminedit.html', user = data[0])
@app.route('/update/<id>',methods=['POST'])
def update_userrequest(id):
    if request.method == 'POST':
        userofticket=request.form['userofticket']
        dateofticket=request.form['dateofticket']
        requesttype=request.form['requesttype']
        title=request.form['title']
        name = request.form['name']
        address = request.form['address']
        phonenumber = request.form['phonenumber']
        emailofticket = request.form['emailofticket']
        userrequest=request.form['userrequest']
        status=request.form['status']
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            UPDATE request
            SET userofticket = %s,
                dateofticket = %s,
                requesttype = %s,
                title = %s,
                name = %s,
                address = %s,
                phonenumber = %s,
                emailofticket = %s,
                userrequest = %s,
                status =%s
            WHERE id = %s
            """, (userofticket,dateofticket, requesttype,title,name,address,phonenumber,emailofticket,userrequest,status, id))
        connect.commit()
        return redirect(url_for('adminindex'))
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_userrequest(id):
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('DELETE FROM request WHERE id = {0}'.format(id))
    connect.commit()
    return redirect(url_for('adminindex'))
if __name__ == "__view__":
    app.run(debug=True)
