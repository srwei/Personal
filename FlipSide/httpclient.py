#!/usr/bin/env python

import http.client
import sys

#http_server = '127.0.0.1'
#get http server ip
http_server = sys.argv[1]
http_port = int(sys.argv[2])
#create a connection
conn = http.client.HTTPConnection(http_server, http_port)

while 1:
  cmd = input('input command (ex. GET index.html): ')
  cmd = cmd.split()

  if cmd[0] == 'exit': #tipe exit to end it
    break
  
  #request command to server
  conn.request(cmd[0], cmd[1])

  #get response from server
  rsp = conn.getresponse()
  
  #print server response and data
  print(rsp.status, rsp.reason)
  data_received = rsp.read()
  print(data_received)
  
conn.close()