import threading
import time


class threadSend(threading.Thread):
    def __init__(self,socketio,sock):
        threading.Thread.__init__(self)
        self.socketio = socketio
        self.sock=sock

    def run(self):
        while True:
            try:
                resp = self.sock.recv(1024)
                print("rec:"+resp)
                if resp:
                    self.socketio.send({'data': resp},namespace='/bash')
                    print("send finish")
                else:
                    print 'sock close'
                    break;
            except Exception,e:
                print(e)
                break
        print("thread stop")

