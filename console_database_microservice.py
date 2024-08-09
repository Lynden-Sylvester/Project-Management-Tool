import zmq
import sqlite3
import json
from datetime import datetime, timedelta
import os

def console_database_processor():

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect("tcp://localhost:5557")

    directory = './'
    filename = 'db_log.txt'
    file_path = os.path.join(directory, filename)
    while True:

        message = socket.recv_json()
        print(f"Received Request: {message}")

        processed = datetime.now()
        database_logger = {
            "ConsoleInput": message,
            "Process Date": processed
        }
        if not os.path.isfile(file_path):
            with open(file_path, 'w') as file:
                file.write('Test')
            print(f"File {filename} created")
        else:
            with open(filename, 'a') as file:
                file.write(f"\n{database_logger}\n")

        reply = f"console database processed: {database_logger}"
        socket.send_json(reply)

console_database_processor()
