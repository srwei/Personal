from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl

httpd = HTTPServer(('localhost', 4443), BaseHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='./server.pem', server_side=True)
httpd.serve_forever()