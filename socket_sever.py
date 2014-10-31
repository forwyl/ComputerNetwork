# -*- coding: utf-8 -*-

import socket
import sys
import threading
 
conn = threading.Condition()
HOST = raw_input("Input the server's ip adrress: ") # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
data = ""
user_nickname_list = []
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created.'
s.bind((HOST, PORT))
s.listen(10)
print 'Socket now listening...'
 
#Function for handling connections. This will be used to create threads
def clientThreadIn(conn, nick):
    global data
    while True:
        try:
            temp = conn.recv(1024)
            if not temp:
                conn.close()
                return
            NotifyAll(temp)
            print data
        except:
            NotifyAll(nick + " leaves the room!")
            print data
            return
 
    #came out of loop
 
def NotifyAll(sss):
    global data
    if conn.acquire():
        data = sss
        conn.notifyAll()
        conn.release()
  
def ClientThreadOut(conn, nick):
    global data
    while True:
        if conn.acquire():
            conn.wait()
            if data:
                try:
                    conn.send(data)
                    conn.release()
                except:
                    conn.release()
                    return
                
def check_legal(nickname):
    global user_nickname_list
    if nickname in user_nickname_list:
        return False, "This name has existed."
    else:
        user_nickname_list.append(nickname)
        return True, "Successfully login."                     
 
while 1:
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    nick = conn.recv(4096)
    is_legal, msg = check_legal(nick)
    conn.send(msg)
    if is_legal:
        NotifyAll('Welcome ' + nick + ' to the room! There are ' + str((threading.activeCount() + 1) / 2) + ' member(s) online!\n')
        print data
#         print str((threading.activeCount() + 1) / 2) + ' person(s)!'
        conn.send(data)
        threading.Thread(target = clientThreadIn , args = (conn, nick)).start()
        threading.Thread(target = ClientThreadOut , args = (conn, nick)).start() 
s.close()