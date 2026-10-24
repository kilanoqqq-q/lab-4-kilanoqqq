<h1 align="center">Запуск:</h1>  
 
```
git clone https://github.com/kilanoqqq-q/lab-3-kilanoqqq.git

cd lab-3-kilanoqqq

docker build -t my-app .

docker run --rm -p 5000:5000 -p 2121:2121 -p 30000-30010:30000-30010 my-app
```

<h1 align="center">Отчёт по лабораторной работе</h1>

**Тема:** настройка FTP-сервера, управление доступом и блокировка подключений

**Цель работы:** настроить FTP-сервер, создать учетную запись пользователя, назначить права доступа, настроить конфигурацию порта и лимитов, а также заблокировать подключения с указанных IP-адресов.

Выбранный пользователь:
- Пользователь: student8
- Пароль: 8resu
- Порт: 8081
- Максимальное кол-во подлючений: 12
- Заблокированный ip: 195.155.10.1

<h1 align="center">Создание учетной записи пользователя и назначение папки</h1>

```
def run_ftp_server():
    ftp_dir_student = os.path.join(os.getcwd(), 'ftp_student') # папка пользователя
    os.makedirs(ftp_dir_student, exist_ok=True)

    authorizer = DummyAuthorizer()
    authorizer.add_user('student8', '8resu', ftp_dir_student, perm='elr') # создание учетной записи

    handler = CustomFTPHandler
    handler.authorizer = authorizer

    server = CustomFTPServer(('0.0.0.0', 8081), handler) # выбранный порт
    server.serve_forever()
```

Папка для пользователя называется "ftp_student". Права `perm='elr'` дают ему возможность только чтения. 

<h1 align="center">Блокировка IP</h1>

```
class CustomFTPServer(FTPServer):
    def handle_accepted(self, sock, addr):
        ip = addr[0]
        if ip == '195.155.10.1': sock.close()
        super().handle_accepted(sock, addr)
```

Библиотека "pyftpdlib" не предусматривает такой возможности по умолчанию, но дает возможность изменить класс "FTPServer" под свои нужды. У него тот же самый функционал, но к нему добавляются нужные нам функции.

<h1 align="center">Ограничение кол-ва сессий</h1>

```
active_user_sessions = {} # словарь {пользователь:кол-во сессий}
sessions_lock = threading.Lock() # блокировка для безопасной работы с потоками
MAX_CONNECTIONS = 12 # ограничение на кол-во ессий

class CustomFTPHandler(FTPHandler):
    def on_login(self, username): # вызывается, когда пользователь авторизуется в аккаунт
        with sessions_lock: 
            current_sessions = active_user_sessions.get(username, 0)

            if current_sessions >= MAX_CONNECTIONS: self.close()

            active_user_sessions[username] = current_sessions + 1

    def on_logout(self, username): # вызывается, когда пользователь сам отключается от сервера
        self._decrease_session_counter(username)

    def handle_close(self): # вызывается, если пользователь отключился не добровольно (сервер разорвал доступ, интренет отключился и т.д.)
        if hasattr(self, 'username') and self.username:
            with sessions_lock:
                if self.username in active_user_sessions:
                    self._decrease_session_counter(self.username)
        super().handle_close()

    def _decrease_session_counter(self, username): # вспомогательная функция для уменьшения счётчика сессий
        with sessions_lock:
            if username in active_user_sessions:
                active_user_sessions[username] -= 1
                if active_user_sessions[username] <= 0:
                    active_user_sessions.pop(username, None)
```

Так же, как и с "FTPServer" нужно было сделать свой класс, который наследует "FTPHandler".
