from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
from mysql.connector import Error
import cgi

class HttpProcessor(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отправляем HTML-форму из файла
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()

        # Читаем HTML-файл и отправляем его клиенту
        with open('form.html', 'r') as file:
            html_content = file.read()
            self.wfile.write(html_content)

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
            errors.append("Неверное ФИО")
        if not phone or not phone.isdigit() or len(phone) != 11:
            errors.append("Неверный номер телефона")
        if not email or '@' not in email:
            errors.append("Неверный email")
        if not gender:
            errors.append("Не выбран пол")
        if not languages:
            errors.append("Не выбран ни один язык программирования")
        if not bio or len(bio) > 500:
            errors.append("Неверная биография")
        if not check:
            errors.append("Необходимо ознакомиться с контрактом")

        if errors:
            # Если есть ошибки, отправляем их клиенту
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Ошибки: " + ", ".join(errors))
            return

        # Подключение к базе данных и сохранение данных
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='form_db',
                user='root',
                password='your_password'
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Вставка данных пользователя
                cursor.execute("""
                    INSERT INTO aplications_languages(fio, phone, email, date, gender, bio, check_agreement)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (fio, phone, email, date, gender, bio, bool(check)))

                user_id = cursor.lastrowid

                # Вставка выбранных языков программирования
                for lang in languages:
                    cursor.execute("""
                        INSERT INTO programming_languages (user_id, language)
                        VALUES (%s, %s)
                    """, (user_id, lang))

                connection.commit()
                cursor.close()
                connection.close()

                # Успешный ответ
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Данные успешно сохранены")

        except Error as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Ошибка базы данных: {e}")

serv = HTTPServer(("localhost", 8888), HttpProcessor)
serv.serve_forever()
