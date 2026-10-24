# edited
import os
import threading
from flask import Flask
from flask import render_template
from pyftpdlib import authorizers
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

app = Flask("PrintingCompany")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/order")
def order():
    return render_template("order.html")

active_user_sessions = {}
sessions_lock = threading.Lock()
MAX_CONNECTIONS = 12

class CustomFTPHandler(FTPHandler):
    def on_login(self, username):
        with sessions_lock:
            current_sessions = active_user_sessions.get(username, 0)

            if current_sessions >= MAX_CONNECTIONS: self.close()

            active_user_sessions[username] = current_sessions + 1

    def on_logout(self, username):
        self._decrease_session_counter(username)

    def handle_close(self):
        if hasattr(self, 'username') and self.username:
            with sessions_lock:
                if self.username in active_user_sessions:
                    self._decrease_session_counter(self.username)
        super().handle_close()

    def _decrease_session_counter(self, username):
        with sessions_lock:
            if username in active_user_sessions:
                active_user_sessions[username] -= 1
                if active_user_sessions[username] <= 0:
                    active_user_sessions.pop(username, None)

class CustomFTPServer(FTPServer):
    def handle_accepted(self, sock, addr):
        ip = addr[0]
        if ip == '195.155.10.1': sock.close()
        super().handle_accepted(sock, addr)

def run_ftp_server():
    ftp_dir_student = os.path.join(os.getcwd(), 'ftp_student')
    os.makedirs(ftp_dir_student, exist_ok=True)

    authorizer = DummyAuthorizer()
    authorizer.add_user('student8', '8resu', ftp_dir_student, perm='elr')

    handler = CustomFTPHandler
    handler.authorizer = authorizer

    server = CustomFTPServer(('0.0.0.0', 8081), handler)
    server.serve_forever()

if __name__ == "__main__":
    ftp_thread = threading.Thread(target=run_ftp_server, daemon=True)
    ftp_thread.start()

    app.run(debug=True, port=5000, host='0.0.0.0')
