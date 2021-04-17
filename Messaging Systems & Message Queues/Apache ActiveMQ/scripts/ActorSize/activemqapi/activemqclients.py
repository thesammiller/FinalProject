

import os
import sys
import threading
import time
import uuid


import stomp


ACTIVEMQ_PORT = 61613


user = os.getenv("ACTIVEMQ_USER") or "admin"
password = os.getenv("ACTIVEMQ_PASSWORD") or "password"
host = os.getenv("ACTIVEMQ_HOST") or "localhost"
port = os.getenv("ACTIVEMQ_PORT") or 61613
destination = sys.argv[1:2] or ["/topic/event"]
destination = destination[0]


class ActiveMQPublisher:

    def __init__(self, hostname='localhost', topic='message'):
        self.conn = stomp.Connection(host_and_ports=[(host, port)])
        self.conn.start()
        self.conn.connect(login=user, passcode=password)
        self.topic = '/topic/' + topic
        self.message_id = 0
        self.uuid = str(uuid.uuid4())
        self.role = 'publisher'
        self.send_times = []
        self.recv_times = []
        self.lock = 0

    def publish(self, message):
        mId = self.uuid
        data_string = mId+":"+message
        self.conn.send(body=data_string, destination=self.topic,
                       persistent='false')
        self.send_times.append(time.time())

    def notify(self):
        pass
        
    def done(self):
        self.conn.send(body="SHUTDOWN", destination=destination,
                       persistent='false')
        self.conn.disconnect()
        for x, y in zip(self.send_times, self.recv_times):
            print("{},{}".format(x,y))

    def on_message(self, headers, message):
        self.lock = 0
        
            

class ActiveMQSubscriber:

    def __init__(self, hostname='localhost', topic='message'):
        self.conn = stomp.Connection(host_and_ports=[(host, port)])
        self.conn.set_listener('', self)
        self.conn.start()
        self.topic = '/topic/' + topic
        self.role = 'subscriber'
        self.uuid = str(uuid.uuid4())
        self.count = 0
        self.start = time.time()
        self.conn.connect(login='admin', password='admin')
        self.conn.subscribe(destination=self.topic, id=1, ack='auto')

    def notify(self):
        while self.count < 1000:
            pass

    def on_message(self, headers, message):
        print(message)
        #self.conn.ack(headers['ack'])
        if message == "SHUTDOWN":

            diff = time.time() - self.start
            print("Received %s in %f seconds" % (self.count, diff))
            conn.disconnect()
            sys.exit(0)

        else:
            if self.count == 0:
                self.start = time.time()

                self.count += 1
                if self.count % 1000 == 0:
                    print("Received %s messages." % self.count)

    def on_error(self, headers, message):
        print('received an error %s' % message)
