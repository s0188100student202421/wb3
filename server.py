from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
from mysql.connector import Error
import cgi
import re

class HttpProcessor(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отправляем HTML-форму из файла
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()

        # Читаем HTML-файл и отправляем его клиенту
        with open('index.html', 'r') as file:
            html_content = file.read()
            self.wfile.write(html_content.encode('utf-8'))

    def do_POST(self):
        # Обработка данных формы
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        # Извлечение данных из формы
        fio = form.getvalue('fio')
        phone = form.getvalue('phone')
        email = form.getvalue('email')
        date = form.getvalue('date')
        gender = form.getvalue('radio')
        languages = form.getlist('language')  # Получаем список выбранных языков
        bio = form.getvalue('bio')
        check = form.getvalue('check')  # Если галочка поставлена, значение будет "on"

        # Валидация данных
        errors = []
        if not fio or not fio.replace(' ', '').isalpha() or len(fio) > 150:
            errors.append("Nevernoe FIO")
        phone_pattern = re.compile(r"^(?:\+7|8)[0-9]{10}")
        if not phone or not phone_pattern.match(phone):
            errors.append("Nevernyy nomer telefona")
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email or not email_pattern.match(email):
            errors.append("Nevernyy email")
        if not gender:
            errors.append("Ne vybran pol")
        if not languages:
            errors.append("Ne vybran ni odin yazyk programmirovaniya")
        if not bio or len(bio) > 500:
            errors.append("Nevernaya biografiya")
        if not check:
            errors.append("Neobkhodimo oznamitsya s kontraktom")
        
        if errors:
            # Если есть ошибки, отправляем их клиенту
            self.send_response(400)
            self.end_headers()
            error_message = "Ошибки: " + ", ".join(errors)
            self.wfile.write(error_message.encode('utf-8'))
            return

        # Подключение к базе данных и сохранение данных
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='u68824',
                user='u68824',
                password='MyStrongPass'
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Вставка данных пользователя
                cursor.execute("""
                    INSERT INTO applications(full_name, gender,phone,email,date,bio,agreement)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (fio,gender, phone, email, date, bio, bool(check)))

                user_id = cursor.lastrowid

                # Вставка выбранных языков программирования
                for lang in languages:
                    cursor.execute("""
                        INSERT INTO programming_languages (id, name)
                        VALUES (%s, %s)
                    """, (user_id, lang))

                connection.commit()
                cursor.close()
                connection.close()

                # Успешный ответ
                self.send_response(200)
                self.wfile.write(f"Data succesfully send!:".encode('utf-8'))
                self.end_headers()

        except Error as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Ошибка базы данных: {e}".encode('utf-8'))

serv = HTTPServer(("localhost", 8888), HttpProcessor)
serv.serve_forever()
