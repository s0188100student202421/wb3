
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
from mysql.connector import Error
import cgi

class HttpProcessor(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_header()

        with open('form.html', 'r') as file:
            html_content = file.read()
            self.wfile.write(html_content)
    def do_POST(self):
        form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {'REQUEST_METHOD' : 'POST'}
        )
        fio = form.getvalue('fio')
        phone = form.getvalue('phone')
        email = form.getvalue('email')
        date = form.getvalue('date')
        gender = form.getvalue('radio')
        languages = form.getlist('language')  # Получаем список выбранных языков
        bio = form.getvalue('bio')
        check = form.getvalue('check')

        errors = []
        if not fio or not fio.replace(' ', '').isalpha() or len(fio) > 150:
            errors.append("Incorrect fio")
        if not phone or not phone.isdigit() or len(phone) ! = 11: # TODO сделать норм проверку 
            errors.append("Incorrect phone number")
        if not email:
            errors.append("Incorrect email")
        if not gender:
            errors.append("Gender isnt selected")
        if not languages:
            errors.append("Languages isnt selected")
        if not bio or len(bio) > 500:
            errors.append("Error in bio")
        if not check:
            errors.append("Необходимо ознакомиться с конктрактом")


        if errors:
            self.send_respond(400)
            self.end_headers()
            self.wfile.write("Ошибки" + ", ".join(errors))
            return 

        try:
            connection = mysql.connector.connect(
                    host = 'localhost',
                    database = 'u68824',
                    user = 'root',
                    password = '6409075'
                    )
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO users (fio, phone, email, date, gender, bio, check_agreement)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (fio, phone, email, date, gender, bio, bool(check)))
                user_id = cursor.lastrowid

                for lang in languages:
                    cursor.execute("""
                        INSERT INTO programming_languages (user_id, lang)
                        VALUES (%s, %s)
                    """, (user_id, lang))
                connection.commit()
                cursor.close()
                connection.close()

                self.send_response(200)
                self.end_headers()
                self.wfile.write("Data was succesfully send")
        excepr Error as e:
            self.send_response(500)
            send.end_headers()
            self.wfile.write(f"Ошибка базы данных : {e}")


serv = HTTPServer(("localhost", 8888), HttpProcessor)
serv.serve_forever()





