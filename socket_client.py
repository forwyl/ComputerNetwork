# -*- coding: utf-8 -*-
 
import socket
import threading
 
PORT = 8888 
inString = ''
outString = ''
nick = ''
 
def DealOut(s):
    global nick, outString
    while True:
        outString = raw_input().strip(" ")
        outString = "[" + nick + ']: ' + outString
        s.send(outString)
 
def DealIn(s):
    global inString
    while True:
        try:
            inString = s.recv(4096)
            if not inString:
                break
            if outString != inString:
                print "\n" + inString
        except:
            break
         
while True:
    nick = raw_input("Input your nickname: ")
    ip = raw_input("Input server's ip adrress: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, PORT))
    sock.send(nick)
    result_msg = sock.recv(4096)
    print result_msg
    if result_msg == "Successfully login.": break
 
thin = threading.Thread(target = DealIn, args = (sock,))
thin.start()
thout = threading.Thread(target = DealOut, args = (sock,))
thout.start()
 