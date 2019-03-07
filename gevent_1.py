import gevent
from gevent import monkey
monkey.patch_all()  #执行脚本插件，修改原有阻塞行为
from socket import *

#创建套接子
def server():
    s = socket()
    s.bind(('0.0.0.0',5233))
    s.listen(5)

    while True:
        try:
            c,addr = s.accept()
        except IOError:
            print('Error')
            continue
        print('Connect from',addr)
        gevent.spawn(handle,c)

def handle(c):
    while True:
        data = c.recv(1024)
        if not data:
            break
        print(data.decode())
        c.send(b'OK')
    c.close()

server()