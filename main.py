from flask import Flask , render_template, request, redirect, url_for, abort, jsonify
from threading import Thread
import sqlite3
import sys
import zmq
import json
from datetime import datetime, timedelta
import time

def send_notification_request(title, message, delay_seconds=0):
    context = zmq.Context()
    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://localhost:5555")

    notification_time = datetime.now() + timedelta(seconds=delay_seconds)
    
    notification = {
        "type": "notification",
        "id": "unique_id_here",  # You should generate a unique ID for each notification
        "title": title,
        "message": message,
        "time": notification_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    sender.send_json(notification)
    sender.close()
    context.term()

# Example call
send_notification_request("Test Notification", "This is a test message", 10)


app = Flask(__name__)

# Create a Database called taskslash
con = sqlite3.connect('taskslash.db')
print('Opened Database Successfully')

# Create a Table in the database to store user creds
con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT);""")
print("Table created successfully")
con.close()

def check_content_type(content_type) -> None:

    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified")
        abort(
            f"Content-Type must be {content_type}"
        )

    if request.headers["Content-Type"] == content_type:
        return
    
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    app.logger.info(f"Reuest Headers: {request.headers}")
    abort(f"Content-Type must be {content_type}")

def consoleOutputFromJS():
    app.logger.info("Requesting Console Data...")
    check_content_type("application/json")

    # Get data from the request
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    console_database_request(data)

def console_database_request(data):

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.bind("tcp://localhost:5557")
    request = data

    socket.send_json(request)
    response = socket.recv_json()
    print(f"Console Response: {response}")

@app.route('/generate', methods = ['POST', 'GET'])
def generate():
    with open('prng-service.txt', 'w') as file:
        file.write("run")
    time.sleep(5)

    with open("prng-service.txt", "r") as file:
      content = file.read()

    with open("image-service.txt", "w") as file:
      file.write(content)
    time.sleep(5)

    with open("image-service.txt", "r") as file:
        content = file.read()

    return render_template("index.html", image_path=content)

@app.route('/test', methods = ['POST'])
def test():
    consoleOutputFromJS()
    return 'success'

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():

    


    # Fetch the username from the form submission on the home path
    username = request.form.get('Username') if request.method == 'POST' else request.args.get('username', '')
    tables_data = {}

    if request.method == 'POST':

        # Fetch data from the form
        username = request.form['Username']
        password = request.form['Password']

        with sqlite3.connect("taskslash.db") as con:
            cur = con.cursor()
            con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT);""")
            con.commit()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",(username, password))
            con.commit()
            cur.execute("SELECT * FROM users WHERE password =?", (password,))    
            user = cur.fetchone()
            print(user)
            print(username)
            print(user[1])
            if user[1] != username:    
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",(username, password))
                con.commit()
                msg = "User record successfully added"
                print(msg)

                # Create a User Database
                user_db_path = f"{username}.db"
                db = sqlite3.connect(f"{user_db_path}")

                db = sqlite3.connect(f"{username}.db")
                cur = db.cursor()
                
                cur1 = con.cursor()
                cur1.execute("SELECT * FROM users;")
                print(f'Username: {username} & Password: {password}!')
                print(f'Username: {username}!')

                # Send User to their Empty Dashboard
                return render_template("dashboard.html", username=username, tables_data=tables_data)
            
            else:

                # Send Returning Users to their dashboard
                return redirect(url_for("dashboard", username=username))
            
    if request.method == 'GET':

        # In the User's Database, create a table to keep
        # track of all the tables they make via the table name
        if username:
                db = sqlite3.connect(f"{username}.db")
                cur = db.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS tables (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            table_name TEXT UNIQUE);""")
                db.commit()
                print("tables table created")
                cur.execute("""CREATE TABLE IF NOT EXISTS example (
                        task TEXT,
                        time TEXT,
                        priority TEXT,
                        assignee TEXT);""")
                db.commit()
                print("example table created")
                cur.execute("SELECT * FROM example;")
                print("example selected")
                cur.execute("INSERT OR IGNORE INTO example VALUES (?, ?, ?, ?)", ('Laundry', '2hrs', 'high', 'James'))
                db.commit()
                cur.execute("SELECT * FROM example;")
                db.commit()
                print(f"tables added to tables table")
                cur.execute("""SELECT table_name FROM tables;""")
                tables_list = [row[0] for row in cur.fetchall()]
                for table_name in tables_list:
                    cur.execute(f"PRAGMA table_info({table_name});")
                    columns = [column[1] for column in cur.fetchall()]
                    cur.execute(f"SELECT * FROM {table_name};")
                    rows = cur.fetchall()
                    tables_data[table_name] = {'columns': columns, 'rows' : rows}
                    print(f'table rows: {tables_data}')
                    print(f'all rows: {rows}')
                print(f'username/\: {username}')
                print(f'Table List/\: {tables_list}')

                # Display the User's Dashboard with the tables
                return render_template("dashboard.html", username = username, tables_data=tables_data)
        else:
                username = request.args.get('username', '')
                password = request.args.get('password', '')
                print(f' Start Username: {username}')
                print(f"Start Passsword: {password}")

                # open the user Table from taskslash database and update the username
                with sqlite3.connect("taskslash.db") as con:
                     cur = con.cursor()
                     cur.execute("""UPDATE users SET username = ? WHERE password = ?""", (username, password))
                     con.commit()
                     user = cur.execute("""SELECT * FROM users;""").fetchone()
                     username = user[1]
                     print(f"Username = {username}")

                # Open the User's database and read all the tables
                with sqlite3.connect(f"{username}.db") as con1:
                    cur1 = con1.cursor()
                    cur1.execute("""SELECT table_name FROM tables;""")
                    print(cur1.fetchall())
                    tables_list = [row[0] for row in cur1.fetchall()]
                    for table_name in tables_list:
                        cur1.execute(f"PRAGMA table_info({table_name});")
                        columns = [column[1] for column in cur1.fetchall()]
                        cur1.execute(f"SELECT * FROM {table_name};")
                        rows = cur.fetchall()
                        tables_data[table_name] = {'columns': columns, 'rows' : rows}
                        print(f'table rows--: {tables_data}')
                        print(f'all rows--: {rows}')
                    print(f'username/\/\: {username}')
                    print(f'Table List/\/\: {tables_list}')

                # Send the User to their Dashboard with all their tables
                return redirect(url_for('dashboard', username=username))

@app.route("/create_table/<username>", methods=["GET", "POST"])
def create_table(username):

    # Create a new table with a single row containing placeholder values
    if request.method == "POST":
        table_name = request.form["table_name"]
        print(f'Table name: {table_name}')
        columns = request.form["columns"].split(',')
        columns = [col.strip() for col in columns]
        db = sqlite3.connect(f'{username}.db')
        cur = db.cursor()
        fields = ', '.join([f'"{col}" TEXT' for col in columns])
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} ({fields});""")
        cur.execute("INSERT OR IGNORE INTO tables (table_name) VALUES (?)", (table_name,))
        db.commit()

        cur.execute(f"PRAGMA table_info({table_name});")
        num_columns = len(cur.fetchall())

        placeholders = ", ".join(["?"] * num_columns)
        cur.execute(f"""INSERT OR IGNORE INTO {table_name} VALUES ({placeholders})""", tuple(["0"] * num_columns))
        db.commit()
        print(f"Create Table Username: {username}")

        # Send the User back to their dashboard
        # Which is now populated with the new table
        return redirect(url_for('dashboard', username=username))
    else:

        # Otherwise stay on the current page
        return render_template("create_table.html", username=username)

@app.route('/help')
def help():
    username = request.args.get('username', '')
    with sqlite3.connect("taskslash.db") as con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users WHERE username =?", (username,))

    # Display the Help Page
    return render_template("help.html", username=username)



if __name__ == "__main__":
    app.run(debug=True)