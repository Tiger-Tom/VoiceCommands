import socket
class client():
    def connect(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        self.sock = s
        return s

    def send(self, data, bt=1024, doRecv=True):
        s = self.sock
        s.sendall(bytes(data, 'UTF-8'))
        if doRecv:
            data = s.recv(bt)
            return data

class server():
    def createHost(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((str(ip), int(port)))
        self.sock = s;
        return s
    def bounce_back(self, data, conn):
        conn.sendall(data)
        print (conn)
        print (data)
    def listen(self, rBt=1024, runOnRecieved=bounce_back):
        s = self.sock
        s.listen()
        connaddr = s.accept()
        conn = connaddr[0]
        addr = connaddr[1]
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if runOnRecieved(conn, data) == False:
                break
            

def close(s):
    s.close()
def find_open_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port
