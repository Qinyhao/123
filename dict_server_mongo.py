'''
dict project for AID
'''
from socket import *
from pymongo import MongoClient
import os,sys
import time
import signal

if len(sys.argv)<3:
    print('''Start as:
    python3 dict_server.py 0.0.0.0 8000
    ''')

#定义全局变量
HOST = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (HOST,PORT)
DICT_TEXT = "./dict.txt"

#搭建网络连接
def main():

    
    #创建套接子
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(6)

    #僵尸进程处理
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    #创建数据库连接对象
    conn = MongoClient('localhost',27017)
    db = conn.dict

    #循环处理客户端请求
    while True:
        try:
            c,addr = s.accept()
            print('Connect from',addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务器退出')
        except Exception as e:
            print('Error:',e)
            continue
        
        #创建紫禁城
        pid = os.fork()
        if pid==0:
            s.close()
            do_child(c,db)
            conn.close()    #数据库关闭
            sys.exit()
        else:
            c.close()

#处理客户端请求
def do_child(c,db):
    while True:
        #接收客户端请求
        data = c.recv(1024).decode()
        print(c.getpeername(),':',data)
        if (not data) or (data[0] == 'E'):
            c.close()
            sys.exit()
        elif data[0] == 'R':
            do_register(c,db,data)
        elif data[0] == 'L':
            do_login(c,db,data)
        elif data[0] == 'Q':
            do_query(c,db,data)
        elif data[0] == 'H':
            do_hist(c,db,data)
    

def do_register(c,db,data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]

    #连接到ｕｓｅｒ表
    myset = db.user
    d = myset.find_one({'name':name})
    if d != None:
        c.send(b'EXISTS')
        return
    

    try:
        #插入用户
        myset.insert_one({'name':name,'passwd':passwd})
        c.send(b'OK')
    except:
        c.send(b'FAIL')
            
def do_login(c,db,data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]

    #查看ｕｓｅｒ表中信息
    myset = db.user
    r = myset.find_one({'name':name,'passwd':passwd})

    if r is None:
        c.send(b'FAIL')
    else:
        c.send(b'OK')

def do_query(c,db,data):
    l = data.split(' ')
    name = l[1]
    word = l[2]

    #插入历史记录
    myset = db.hist
    tm = str(time.ctime())
    try:
        myset.insert_one({'name':name,'word':word,'time':tm})
    except Exception as e:
        print(e)

    #通过单词本查找
    f = open(DICT_TEXT)

    for line in f:
        tmp = line.split(' ')[0]
        if tmp>word:
            break
        elif tmp == word:
            c.send(line.encode())
            f.close()
            return
    c.send('没有找到该单词'.encode())
    f.close()

def do_hist(c,db,data):
    name = data.split(' ')[1]
    myset = db.hist
    cur = myset.find({'name':name}).limit(10).sort([('time',-1)])
    if not r:
        c.send(b'FAIL')
    else:
        c.send(b'OK')
        time.sleep(0.1)
    for i in r:
        msg = "%s %s %s" % (i[1],i[2],i[3])
        c.send(msg.encode())
        time.sleep(0.1)
    c.send(b'##')




if __name__ == '__main__':
    main()