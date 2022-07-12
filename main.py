from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2 #pip install psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'dueJuly'

# Enter your database connection details below
DB_HOST = "ec2-3-224-8-189.compute-1.amazonaws.com"
DB_NAME = "d9tmmg8f329u7q"
DB_USER = "dgmngaedsbampl"
DB_PASS = "c49e7707bfe4377da7b4ea48b34c2d6286238936c4e4f2c018973453b878696d"

# Intialize MySQL
#mysql = MySQL(app)
connect = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
           # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
    # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
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
                _hashed_password = generate_password_hash(password)
                cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, _hashed_password, email,))
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

# http://localhost:5000/pythinlogin/userrequest - this will be the user request page
@app.route('/pythonlogin/userrequest', methods=['GET','POST'])
def userrequest():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s',(session['username'],) )
        account = cursor.fetchone()
        userofticket=account['username']
        id = account['id']
        status = "New"
        # Output message if something goes wrong...
        msg = ''
        #User is loggedin show them the userrequest page
        if request.method == 'POST' and 'dateofticket'in request.form and 'requesttype' in request.form and 'title' in request.form and 'name' in request.form and 'address' in request.form and 'phonenumber' in request.form and 'emailofticket' in request.form and 'userrequest' in request.form:
            dateofticket=request.form['dateofticket']
            requesttype=request.form['requesttype']
            title=request.form['title']
            name = request.form['name']
            address = request.form['address']
            phonenumber = request.form['phonenumber']
            emailofticket = request.form['emailofticket']
            userrequest=request.form['userrequest']
        # Insert new request into request table
            cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
            #cursor.execute('INSERT INTO request (id,userofticket,dateofticket, requesttype,title,name,address,phonenumber,emailofticket,userrequest,status) VALUES (%s,%s,%s, %s, %s,%s,%s,%s,%s,%s,%s)', (id,userofticket,dateofticket, requesttype,title,name,address,phonenumber,emailofticket,userrequest,status))
            connect.commit()
            msg = 'dateofticket'
            return redirect(url_for('userrequest'), msg=msg)
        else:
            msg = 'Incorrect input'
        # User is loggedin show them the userrequest page
        return render_template('userrequest.html',msg=msg)
    else:    return redirect(url_for('login'))
#http://localhost:5000/pythinlogin/historyuserrequest
@app.route('/pythonlogin/historyuserrequest')
def historyuserrequest():
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM request WHERE id=%s',(session['id']))
    list_requests = cursor.fetone()
    return render_template('historyuserrequest',list_requests=list_requests)
# http://localhost:5000/pythinlogin/adminindex
@app.route('/pythonlogin/adminindex')
def adminindex(): 
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM request')
    list_requests = cursor.fetchall()
    return render_template('adminindex.html',list_requests=list_requests)
@app.route('/add_userrequest', methods=['POST'])
def add_userrequest():
    cursor = connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        userofticket    = request.form['userofticket']
        dateofticket    = request.form['dateofticket']
        requesttype     = request.form['requesttype']
        title           = request.form['title']
        name            = request.form['name']
        address         = request.form['address']
        phonenumber     = request.form['phonenumber']
        emailofticket   = request.form['emailofticket']
        userrequest     = request.form['userrequest']
        status          = request.form['status']
        cursor.execute("INSERT INTO request (userofticket, dateofticket, requesttype, title, name, address, phonenumber,emailofticket,userrequest,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (userofticket,dateofticket, requesttype,title,name,address,phonenumber,emailofticket,userrequest,status))
        connect.commit()
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
        userofticket    = request.form['userofticket']
        dateofticket    = request.form['dateofticket']
        requesttype     = request.form['requesttype']
        title           = request.form['title']
        name            = request.form['name']
        address         = request.form['address']
        phonenumber     = request.form['phonenumber']
        emailofticket   = request.form['emailofticket']
        userrequest     = request.form['userrequest']
        status          = request.form['status']
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
if __name__ == '__main__':
    app.run(debug=True)