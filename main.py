from flask import Flask , render_template, request, redirect, url_for
from threading import Thread
import sqlite3
import sys


app = Flask(__name__)

con = sqlite3.connect('taskslash.db')
print('Opened Database Successfully')

con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT);""")
print("Table created successfully")
con.close()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():
    username = request.form.get('Username') if request.method == 'POST' else request.args.get('username', '')
    tables_data = {}

    if request.method == 'POST':
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

                user_db_path = f"{username}.db"
                db = sqlite3.connect(f"{user_db_path}")

                db = sqlite3.connect(f"{username}.db")
                cur = db.cursor()
                
                cur1 = con.cursor()
                cur1.execute("SELECT * FROM users;")
                print(f'Username: {username} & Password: {password}!')
                print(f'Username: {username}!')
                return render_template("dashboard.html", username=username, tables_data=tables_data) # Displays Dashboard with no Tables
            
            else:
                return redirect(url_for("dashboard", username=username))
            
    if request.method == 'GET':
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
                return render_template("dashboard.html", username = username, tables_data=tables_data)
        else:
                username = request.args.get('username', '')
                password = request.args.get('password', '')
                print(f' Start Username: {username}')
                print(f"Start Passsword: {password}")
                with sqlite3.connect("taskslash.db") as con:
                     cur = con.cursor()
                     cur.execute("""UPDATE users SET username = ? WHERE password = ?""", (username, password))
                     con.commit()
                     user = cur.execute("""SELECT * FROM users;""").fetchone()
                     username = user[1]
                     print(f"Username = {username}")
                with sqlite3.connect(f"{username}.db") as con1:
                    cur1 = con1.cursor()
                    cur1.execute("""SELECT table_name FROM tables;""")
                    tables_list = [row[0] for row in cur.fetchall()]
                    for table_name in tables_list:
                        cur.execute(f"PRAGMA table_info({table_name});")
                        columns = [column[1] for column in cur.fetchall()]
                        cur.execute(f"SELECT * FROM {table_name};")
                        rows = cur.fetchall()
                        tables_data[table_name] = {'columns': columns, 'rows' : rows}
                        print(f'table rows--: {tables_data}')
                        print(f'all rows--: {rows}')
                    print(f'username/\/\: {username}')
                    print(f'Table List/\/\: {tables_list}')
                username = str(username)
                return render_template("dashboard.html", username = username, tables_data=tables_data)

@app.route("/create_table/<username>", methods=["GET", "POST"])
def create_table(username):
    if request.method == "POST":
        table_name = request.form["table_name"]
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
        return redirect(url_for('dashboard', username=username))
    else:
        return render_template("create_table.html", username=username)

@app.route('/help')
def help():
    username = request.args.get('username', '')
    with sqlite3.connect("taskslash.db") as con:
        cur = con.cursor()
        cur.execute("SELECT username FROM users WHERE username =?", (username,))
    return render_template("help.html", username=username)



if __name__ == "__main__":
    app.run(debug=True)