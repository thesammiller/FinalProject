import time
import sys
import os
import stomp

user = os.getenv("ACTIVEMQ_USER") or "admin"
password = os.getenv("ACTIVEMQ_PASSWORD") or "password"
host = os.getenv("ACTIVEMQ_HOST") or "localhost"
port = os.getenv("ACTIVEMQ_PORT") or 61613
destination = sys.argv[1:2] or ["/topic/event"]
destination = destination[0]

class MyListener(object):
  
  def __init__(self, conn):
    self.conn = conn
    self.count = 0
    self.start = time.time()
  
  def on_error(self, headers, message):
    print('received an error %s' % message)

  def on_message(self, headers, message):
    if message == "SHUTDOWN":
    
      diff = time.time() - self.start
      print("Received %s in %f seconds" % (self.count, diff))
      conn.disconnect()
      sys.exit(0)
      
    else:
      if self.count==0:
        self.start = time.time()
        
      self.count += 1
      if self.count % 1000 == 0:
         print("Received %s messages." % self.count)

conn = stomp.Connection(host_and_ports = [(host, port)])
conn.set_listener('', MyListener(conn))
conn.start()

for i in range(30):
  try:
    conn.connect(login='admin',passcode='admin')
  except:
    time.sleep(.1)
    pass
conn.subscribe(destination=destination, id=1, ack='auto')
print("Waiting for messages...")
while 1: 
  time.sleep(10) 
