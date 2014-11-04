# -*- coding: utf-8 -*-

import socket
import threading
import os 
import uuid
import time
 
CON = threading.Condition()
HOST = "localhost"
PORT = 8888
data = ""
user_nickname_list = []
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created.'
s.bind((HOST, PORT))
s.listen(10)
print 'Socket now listening...'
    
def clientThreadIn(connect, nick):
    global data, file_counter
    while True:
        try:
            temp = connect.recv(1024)
            if not temp:
                connect.close()
                return
            if(temp[0:10] == "send_file "):
                output_file = str(uuid.uuid4()) + "_" + temp[temp.rindex("/")+1:temp.rindex(";")]
                filesize = long(temp[temp.rindex(";")+1:])
                print output_file + ", size:" + str(filesize)
                temp = connect.recv(1024)
                with open(output_file, "wb") as w:
                    while not ("EOF" in temp):
                        w.write(temp)
                        temp = connect.recv(1024)
                w.close()
                NotifyAll("Successfully upload file "+ output_file + " to server")
                print "Successfully upload file "+ output_file + " to server"
                
            else:
                NotifyAll(temp)
                print data
        except:
            NotifyAll(nick + " leaves the room!")
            print data
            return
 
    #came out of loop
 
def NotifyAll(sss):
    global data
    if CON.acquire():
        data = sss
        CON.notifyAll()
        CON.release()
  
def ClientThreadOut(connect, nick):
    global data
    while True:
        if CON.acquire():
            CON.wait()
            if data:
                try:
                    connect.send(data)
                    CON.release()
                except:
                    CON.release()
                    return
                
def check_legal(nickname):
    global user_nickname_list
    if nickname in user_nickname_list:
        return False, "This name has existed."
    else:
        user_nickname_list.append(nickname)
        return True, "Successfully login."
 
while True:
    connect, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    nick = connect.recv(1024)
    is_legal, msg = check_legal(nick)
    connect.send(msg)
    if is_legal:
        NotifyAll('Welcome ' + nick + ' to the room! There are ' + str((threading.activeCount() + 1) / 2) + ' member(s) online!')
        print data
        connect.send(data)
        threading.Thread(target = clientThreadIn , args = (connect, nick)).start()
        threading.Thread(target = ClientThreadOut , args = (connect, nick)).start() 
s.close()