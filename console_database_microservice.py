import zmq
import sqlite3

def console_database_processor():

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect("tcp://localhost:5557")

    while True:

        message = socket.recv_json()
        print(f"Received Request: {message}")

        reply = f"console database processed: {message}"
        socket.send_json(reply)

console_database_processor()
