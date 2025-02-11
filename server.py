from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Здесь код, который может вызвать ошибку базы данных
            raise Exception("Ошибка соединения с БД")  # Симуляция ошибки

        except Exception as e:
            self.send_response(500)  # HTTP 500 - Внутренняя ошибка сервера
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Ошибка базы данных: {e}".encode("utf-8"))

server_address = ("", 8080)
httpd = HTTPServer(server_address, MyHandler)
print("Сервер запущен на порту 8080...")
httpd.serve_forever()
