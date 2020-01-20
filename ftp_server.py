"""
FTP 文件服务器，服务端
多进程/线程并发 socket

"""
import time
from socket import *
import sys,os
from threading import Thread

#全局变量
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)
FTP = '/home/tarena/study/FTP/'
FILES = os.listdir(FTP)

# 创建类实现服务器文件处理功能

class FTPServer(Thread):
    """
    查看列表，上传，下载，退出处理
    """
    def __init__(self,connfd):
        self.connfd = connfd
        super().__init__()

    def do_list(self):
        if not FILES:
            self.connfd.recv("文件库为空".encode())
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
        # 拼接文件名
        filelist = ''
        for file in FILES:
            if file[0] != '.' and os.path.isfile(FTP+file):
                filelist += file + '\n'
        self.connfd.send(filelist.encode())

    def do_get(self,filename):
        if len(FILES) == 0 or filename not in FILES:
            self.connfd.send("找不到文件".encode())
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
            f = open(FTP+filename,'rb')
            while True:
                text = f.read(1024)
                if not text:
                    break
                self.connfd.send(text)
            f.close()
            time.sleep(0.1)
            self.connfd.send(b'##')

    def do_put(self,filename):
        if filename in FILES:
            self.connfd.send("不可上传与服务器已有文件同名的文件".encode())
            return
        else:
            self.connfd.send(b'OK')
            f = open(FTP + filename,'wb')
            while True:
                text = self.connfd.recv(1024)
                if text == b'##':
                    break
                f.write(text)
            f.close()

    def run(self):
        while True:
            data = self.connfd.recv(1024).decode()
            if not data or data == 'Q':
                addr = self.connfd.getpeername()
                print("退出连接！",addr)
                return # 线程结束
            elif data == 'L':
                self.do_list()
            elif data[0] == 'G':
                filename = data.split(' ')[-1]
                self.do_get(filename)
            elif data[0] == 'P':
                filename = data.split(' ')[-1]
                self.do_put(filename)




#搭建网络服务端模型
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(10)


    print("waiting for the connection...")
    while True:
        try:
            c,addr = s.accept()
            print("Connect from",addr)
        except KeyboardInterrupt:
            sys.exit("FTP服务器退出！")
        except Exception as e:
            print(e)
            continue

        t = FTPServer(c)
        t.setDaemon(True)
        t.start()




if __name__=="__main__":
    main()














