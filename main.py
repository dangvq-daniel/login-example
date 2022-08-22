
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail,Message
import psycopg2
import psycopg2.extras
import re
import os
import ssl
import smtplib
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = b'\xd3\x89\x87 \xf9Hu\xafv?\xeb\x93\xda\xfe|N<\xcc\x16\x9f^\xc7\xa9\xfb'

# Enter your database connection details below
"""DB_HOST = "ec2-3-224-8-189.compute-1.amazonaws.com"
DB_NAME = "d9tmmg8f329u7q"
DB_USER = "dgmngaedsbampl"
DB_PASS = "c49e7707bfe4377da7b4ea48b34c2d6286238936c4e4f2c018973453b878696d"
"""
DB_HOST = "localhost"
DB_NAME = "account"
DB_USER = "user"
DB_PASS = "123456789"""
# Intialize MySQL
# mysql = MySQL(app)
connect = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        # Check if account exists using MySQL
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            password_rs = account['password']
            if check_password_hash(password,password_rs):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                if session['id'] == 1:
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('home'))
            else:
                msg = 'Incorrect username/password!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)


@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'token' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        token = request.form['token']
        # Check if account exists using MySQL
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute("SELECT * FROM tokens WHERE token LIKE '{0}'".format(token))
            verification = cursor.fetchone()
            if verification:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)',
                               (username, password, email,))
                connect.commit()
                return redirect(url_for('login'))
            else:
                msg = 'Invalid token'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# CREATE NEW USER REQUEST
@app.route('/pythonlogin/userrequest', methods=['GET', 'POST'])
def userrequest():
    email_sender =  'noreply.DPBusiness@gmail.com'
    email_password = 'aggctvaynqbindkd'
    email_receiver = 'economydpbusiness@gmail.com'
    # Check if user is loggedin
    msg = ''
    if 'loggedin' in session:
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['username'],))
        account = cursor.fetchone()
        userofticket = account['username']
        status = "New"
        # Output message if something goes wrong...
        # User is loggedin show them the userrequest page
        if request.method == 'POST' and 'dateofticket' in request.form and 'title' in request.form and 'name' in request.form and 'address' in request.form and 'phonenumber' in request.form and 'emailofticket' in request.form and 'userrequest' in request.form:
            dateofticket = request.form['dateofticket']
            title = request.form['title']
            name = request.form['name']
            address = request.form['address']
            phonenumber = request.form['phonenumber']
            emailofticket = request.form['emailofticket']
            userrequest = request.form['userrequest']
            # Insert new request into request table
            cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(
                "INSERT INTO request ( userofticket,dateofticket,title,name,address,phonenumber,emailofticket,userrequest,status) VALUES (%s,%s,%s, %s, %s,%s,%s,%s,%s)",
                ( userofticket, dateofticket, title, name, address, phonenumber, emailofticket, userrequest, status))
            connect.commit()
            subject = 'New Request from ' + userofticket
            body = "Have new request titled " + title + " with phone number: " + phonenumber + " and email: " + emailofticket
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
            msg = 'Request submitted'
        elif request.method == 'POST':
            msg = 'Incorrect input'
        # User is loggedin show them the userrequest page
    else:
        return redirect(url_for('login'))
    return render_template('userrequest.html', msg=msg)


# USER VIEW HISTORY REQUEST
@app.route('/pythonlogin/historyuserrequest')
def historyuserrequest():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM request WHERE userofticket = %s', (session['username'],))
        list_requests = cursor.fetchall()
    return render_template('historyuserrequest.html', list_requests=list_requests)


# ADMIN
@app.route('/pythologin/admin', methods=['POST', 'GET'])
def admin():
    if 'loggedin' in session and session['id'] == 1:
        # User is loggedin show them the admin page
        return render_template('admin.html')
    else:
        return redirect(url_for('login'))


# ADMIN CONTROL USER REQUEST
@app.route('/pythonlogin/admin/requestcontrolindex')
def requestcontrolindex():
    if 'loggedin' in session and session['id'] == 1:
        # User is loggedin show them the admin page
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM request')
        list_requests = cursor.fetchall()
        return render_template('requestcontrolindex.html', list_requests=list_requests)
    else:
        return redirect(url_for('home'))


@app.route('/add_userrequest', methods=['POST'])
def add_userrequest():
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        invoicenumber = request.form['invoicenumber']
        userofticket = request.form['userofticket']
        dateofticket = request.form['dateofticket']
        title = request.form['title']
        name = request.form['name']
        address = request.form['address']
        phonenumber = request.form['phonenumber']
        emailofticket = request.form['emailofticket']
        userrequest = request.form['userrequest']
        status = request.form['status']
        cursor.execute(
            "INSERT INTO request (userofticket, dateofticket, title, name, address, phonenumber,emailofticket,userrequest,status,invoicenumber) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (userofticket, dateofticket, title, name, address, phonenumber, emailofticket, userrequest, status,invoicenumber))
        connect.commit()
        return redirect(url_for('requestcontrolindex'))


@app.route('/editrequest/<id>', methods=['GET', 'POST'])
def edit_request(id):
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM request WHERE id = %s', (id))
    data = cursor.fetchall()
    cursor.close()
    print(data[0])
    return render_template('requestcontroledit.html', user=data[0])


@app.route('/updaterequest/<id>', methods=['POST'])
def update_request(id):
    if request.method == 'POST':
        invoicenumber = request.form['invoicenumber']
        userofticket = request.form['userofticket']
        dateofticket = request.form['dateofticket']
        title = request.form['title']
        name = request.form['name']
        address = request.form['address']
        phonenumber = request.form['phonenumber']
        emailofticket = request.form['emailofticket']
        userrequest = request.form['userrequest']
        status = request.form['status']
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            UPDATE request
            SET userofticket = %s,
                dateofticket = %s,
                title = %s,
                name = %s,
                address = %s,
                phonenumber = %s,
                emailofticket = %s,
                userrequest = %s,
                status =%s,
                invoicenumber = %s
            WHERE id = %s
            """, (
        userofticket, dateofticket, title, name, address, phonenumber, emailofticket, userrequest, status, invoicenumber, id))
        connect.commit()
        return redirect(url_for('requestcontrolindex'))


@app.route('/deleterequest/<string:id>', methods=['POST', 'GET'])
def delete_request(id):
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('DELETE FROM request WHERE id = {0}'.format(id))
    connect.commit()
    return redirect(url_for('requestcontrolindex'))


# ADMIN CONTROL USER ACCOUNTS
@app.route('/pythonlogin/admin/usercontrolindex')
def usercontrolindex():
    if 'loggedin' in session and session['id'] == 1:
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts')
        list_requests = cursor.fetchall()
        return render_template('usercontrolindex.html', list_requests=list_requests)
    else:
        return redirect(url_for('home'))


@app.route('/add_user', methods=['POST'])
def add_user():
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor.execute("INSERT INTO accounts (username, password,email) VALUES (%s,%s,%s)", (username, password, email))
        connect.commit()
        return redirect(url_for('usercontrolindex'))


@app.route('/edituser/<id>', methods=['GET', 'POST'])
def edit_user(id):
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (id))
    data = cursor.fetchall()
    cursor.close()
    print(data[0])
    return render_template('usercontroledit.html', user=data[0])


@app.route('/updateuser/<id>', methods=['POST'])
def update_user(id):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("UPDATE accounts SET username = %s , password = %s , email = %s WHERE id = %s ", (username, password, email, id))
        connect.commit()
        return redirect(url_for('usercontrolindex'))


@app.route('/deleteuser/<string:id>', methods=['POST', 'GET'])
def delete_user(id):
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('DELETE FROM accounts WHERE id = {0}'.format(id))
    connect.commit()
    return redirect(url_for('usercontrolindex'))

@app.route('/pythonlogin/changepassword', methods=['POST', 'GET'])
def change_password():
    msg = ''
    if 'loggedin' in session:
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['username'],))
        account = cursor.fetchone()
        id = account['id']
        if (request.method == 'POST') and ('password_cr' in request.form) and ('password_new' in request.form) and ('password_ver' in request.form):
            password_cr = generate_password_hash(request.form['password_cr'])
            password_new = generate_password_hash(request.form['password_new'])
            password_ver = request.form['password_ver']
            password = account['password']
            if check_password_hash(password_cr, password):
                if check_password_hash(password_new, password_ver):
                    cursor.execute('UPDATE accounts SET password = %s WHERE id = %s', (password_ver, id))
                    connect.commit()
                    msg = 'Success!'
                else:
                    msg = 'Passwords do not match!'
            else:
                msg = 'Incorrect password'
        elif request.method == 'POST':
            msg = 'Incorrect input'
    else:
        return redirect(url_for('login'))
    return render_template('changepassword.html', msg=msg)

# GET TOKEN
@app.route('/python/admin/gettokens',methods=['GET','POST'])
def gettokens():
    if 'loggedin' in session and session['id'] == 1 :
        # User is loggedin show them the admin page
            cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute('SELECT * FROM tokens order by random () limit 1')
            data = cursor.fetchone()
            return render_template('gettokens.html',data=data)
    else:
            return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)
