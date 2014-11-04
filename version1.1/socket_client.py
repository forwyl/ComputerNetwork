# -*- coding: utf-8 -*-
 
import socket
import threading
import os
import uuid
import inspect

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
            s.send("send_file " + filepath)
            with open(filepath, "rb") as r:
                while True:
                    data = r.read(1024)
                    if not data: break
                    s.send(data)
            r.close()
            s.send("EOF")
            print "Successfully send file " +  filepath + " to server!"                            
        elif outString[0:len("get_file ")] == "get_file ":
            s.send(outString)
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
                if (inString[0:len("send_file_to;")] == "send_file_to;") and (inString[inString.index(";")+1:inString.index(",")] == nick) :
                    input_file =  os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "\\" + str(uuid.uuid4()) + "_" + inString[inString.index(",")+1:]              
                    temp = s.recv(1024)
                    with open(input_file, "wb") as w:
                        while True:
                            if "EOF" in temp:
                                w.write(temp[:temp.rindex("EOF")])                                
                                break
                            w.write(temp)
                            temp = s.recv(1024)

                    w.close()
                    print "\nSuccessfully receive file " + input_file + " from server"
                else:
                    print "\n" + inString
        except:
            break
         
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