# -*- coding: utf-8 -*-
 
import socket
import threading
import os
import uuid

HOST = "localhost" 
PORT = 8888 
inString = ''
outString = ''
nick = ''
         
def output_dealer(s):
    global nick, outString
    while True:
        outString = raw_input().strip(" ")
        if outString[0:10] == "send_file ":
            filepath = outString[10:]
            filesize = os.stat(filepath).st_size
            s.send("send_file " + filepath + ";" + str(filesize))
            with open(filepath, "rb") as r:
                while True:
                    data = r.read(1024)
                    if not data: break
                    s.send(data)
            r.close()
            s.send("EOF")
            print "Successfully send file " +  filepath + " to server!"
        else:    
            outString = "[" + nick + ']: ' + outString
            s.send(outString)
 
def input_dealer(s):
    global inString
    while True:
        try:
            inString = s.recv(1024)
            if not inString:
                break
            if outString != inString:
                print "\n" + inString
        except:
            break
   
# def _test():
# 
#     filepath = "D://seo.jpg"
#     with open(filepath, "rb") as r:
#         with open(uuid.uuid4() + "_" + filepath[filepath.rindex("/")+1:], "wb") as w:
#             for item in r:
#                 w.write(item)
#                  
#     filepath = "D://data.txt"
#     with open(filepath, "rb") as r:
#         with open(uuid.uuid4() + "_" + filepath[filepath.rindex("/")+1:], "wb") as w:
#             for item in r:
#                 w.write(item)
# 
#     filepath = "D://data.txt"
#     with open(filepath, "rb") as r:
#         result = r.read()
#     print result
    
# _test()
         
while True:
    nick = raw_input("Input your nickname: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.send(nick)
    result_msg = sock.recv(1024)
    print result_msg
    if result_msg == "Successfully login.": break
  
thin = threading.Thread(target = input_dealer, args = (sock,))
thin.start()
thout = threading.Thread(target = output_dealer, args = (sock,))
thout.start()

#sock.close()