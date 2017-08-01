#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

#Create custom HTTPRequestHandler class
class KodeFunHTTPRequestHandler(BaseHTTPRequestHandler):
  
  #handle GET command
  def do_GET(self):
    rootdir = '/Users/StevenWei/Desktop/Programming/FlipSide' #file location
    try:
      if self.path.endswith('.html'):
        f = open(rootdir + self.path) #open requested file

        #send code 200 response
        self.send_response(200)

        #send header first
        self.send_header('Content-type','text-html')
        self.end_headers()

        #send file content to client
        self.wfile.write(f.read())
        f.close()
        return
      
    except IOError:
      self.send_error(404, 'file not found')
  
def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
  print('http server is starting...')

  #ip and port of servr
  #by default http server port is 80
  server_address = ('127.0.0.1', 8000)
  httpd = server_class(server_address, handler_class)
  print('http server is running...')
  httpd.serve_forever()
  
if __name__ == '__main__':
  run()