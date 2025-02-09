
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





