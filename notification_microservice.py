import zmq
import json
import time
from datetime import datetime
import threading
import subprocess
import sys
import signal
from plyer import notification

class NotificationMicroservice:
    def __init__(self):
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind("tcp://*:5555")
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:5556")
        self.notifications = {}
        self.lock = threading.Lock()
        self.running = True
        self.threads = []

    def receive_notifications(self):
        while self.running:
            try:
                message = self.receiver.recv_json(flags=zmq.NOBLOCK)
                print(f"Received notification request: {message}")
                with self.lock:
                    notification_id = message['id']
                    if notification_id in self.notifications:
                        print(f"Updating existing notification with ID: {notification_id}")
                        self.notifications[notification_id].update(message)
                    else:
                        print(f"Adding new notification with ID: {notification_id}")
                        self.notifications[notification_id] = message
            except zmq.Again:
                time.sleep(0.1)  # Short sleep to prevent busy waiting
            except Exception as e:
                print(f"Error receiving notification: {e}")

    def check_and_send_notifications(self):
        while self.running:
            current_time = datetime.now()
            with self.lock:
                for notification_id, notification in list(self.notifications.items()):
                    notification_time = datetime.strptime(notification['time'], "%Y-%m-%d %H:%M:%S")
                    if current_time >= notification_time:
                        self.send_notification(notification['title'], notification['message'])
                        del self.notifications[notification_id]
                        self.send_confirmation(notification_id)
            time.sleep(1)  # Check every second for more responsive shutdown

    def send_notification(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Task Manager",
                timeout=10
            )
        except Exception as e:
            print(f"Error sending notification: {str(e)}")

    def send_confirmation(self, notification_id):
        confirmation = {
            "type": "confirmation",
            "id": notification_id
        }
        self.sender.send_json(confirmation)

    def shutdown(self):
        print("Shutting down...")
        self.running = False
        for thread in self.threads:
            thread.join()
        self.receiver.close()
        self.sender.close()
        self.context.term()
        print("Shutdown complete.")

    def run(self):
        self.threads = [
            threading.Thread(target=self.receive_notifications),
            threading.Thread(target=self.check_and_send_notifications)
        ]
        for thread in self.threads:
            thread.start()

        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("Notification microservice is running. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while self.running:
            time.sleep(1)

    def signal_handler(self, signum, frame):
        print(f"Received signal {signum}")
        self.shutdown()

if __name__ == "__main__":
    microservice = NotificationMicroservice()
    microservice.run()