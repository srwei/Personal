from http.client import HTTPConnection
import sys

#get http server ip
host, port = sys.argv[1], sys.argv[2]
#create a connection
conn = HTTPConnection(host, port)

while True:
  cmd = input('input command (ex. GET index.html): ')
  cmd = cmd.split()

  if cmd[0] == 'exit': #tipe exit to end it
    break
  
  #request command to server
  #file = open(cmd[1], 'r')
  #conn.request(cmd[0], '/test', body = file)
  conn.request(cmd[0], cmd[1])
  #get response from server
  rsp = conn.getresponse()
  
  #print server response and data
  print(rsp.status, rsp.reason)
  data_received = rsp.read()
  print(data_received)
  
conn.close()