#!/usr/bin/env python
# -*- coding: utf8 -*-
  
import sys
import time
import daemon

import socket
import sys

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def dump(src, length=8):
    """
    Функция отображающая дамп данных
    """
    N=0; result=''
    while src:
       s,src = src[:length],src[length:]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       s = s.translate(FILTER)
       result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
       N+=length
    return result

host = ''    # ip
port = 5000  # порт
backlog = 5  # ожидаемое количество ожидающих обработки запросов
size = 1024  # размер данных

class MyDaemon(daemon.Daemon):
    def __init__(self):
        daemon.Daemon.pidfile = "VNCSnake.pid"
  
    def start(self, interactive=False):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # создаём сокет для IPv4
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # устанавливаем опцию повторного использования порта для того, чтобы не ждать после останова сервера пока освободится порт
        self.s.bind((host,port))  # ассоциировать адрес с сокетом
        self.s.listen(backlog)    # принимать запросы на установление соединения
        daemon.Daemon.start(self, interactive)

    def stop(self):
        daemon.Daemon.stop(self)

    def run(self):
        while 1:
            client, address = self.s.accept() # принять запрос и преобразовать в соединение. client - новое соединение
            # print "server: got connection from %s port %d\n" % (address[0], address[1])
            client.send("Welcome to server\n") # посылаем приглашение клиенту
            data = client.recv(size) # получаем данные от клиента с размером size=1024
            while(len(data) > 0):
                if "quit" in data: break; # если клиент вводит quit, то соединение с клиентом закрывается
                client.send("RECV: %d bytes\n" % len(data))
                client.send(dump(data))
                data = client.recv(size)
            client.close() # Закрыть соединение с клиентом
            time.sleep(0.1)
  
my_daemon = MyDaemon()
  
if len(sys.argv) >= 2:
    if 'start' == sys.argv[1]:
        my_daemon.start()
    elif 'stop' == sys.argv[1]:
        my_daemon.stop()
    elif 'restart' == sys.argv[1]:
        my_daemon.restart()
    else:
        print "Unknown command"
        sys.exit(2)
    sys.exit(0)