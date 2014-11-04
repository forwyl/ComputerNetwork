# -*- coding: utf-8 -*-

import socket
import threading
import os 
import uuid
import time
import inspect
 
CON = threading.Condition()
HOST = "localhost"
PORT = 8888
data = ""
user_nickname_list = []

FILE_PATH_PREFIX = "D://NTU/ComputerNetwork/files_warehouse/"
SYSTEM_FILE_PATH = "D://NTU/ComputerNetwork/property/system_setup.txt"

file_id_counter = 0
file_dict = {}

f = open(SYSTEM_FILE_PATH)
f_line = f.readline()
counter = 0
while f_line:
        counter += 1 
        file_dict[int(f_line.split(";")[0])] = str(f_line.split(";")[1]).strip().strip(" ").strip("\n")
        f_line = str(f.readline())
f.close()
file_id_counter = counter

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created.'
s.bind((HOST, PORT))
s.listen(10)
print 'Socket now listening...'

def message_dealer(data):
    print data
    
def update_fileid(output_file):
    global file_id_counter, file_dict
    file_id_counter += 1
    file_dict[file_id_counter] = output_file
    with open(SYSTEM_FILE_PATH, "a") as w:
        w.write(str(file_id_counter)+ ";" + output_file + "\n")
    w.close()
    
def receive_file(connect, temp):
    global file_id_counter
    output_file = FILE_PATH_PREFIX + str(uuid.uuid4()) + "_" + temp[temp.rindex("/")+1 :]
    temp = connect.recv(1024)
    with open(output_file, "wb") as w:
        while True:
            if "EOF" in temp:
                w.write(temp[:temp.rindex("EOF")])                                
                break
            w.write(temp)
            temp = connect.recv(1024)
    w.close()
    update_fileid(output_file)
    
    return output_file

def check_legal(nickname):
    global user_nickname_list
    if nickname in user_nickname_list:
        return False, "This name has existed."
    else:
        user_nickname_list.append(nickname)
        return True, "Successfully login."
    
def clientThreadIn(connect, nick):
    global data, file_id_counter
    while True:
        try:
            temp = connect.recv(1024)
            if not temp:
                connect.close()
                return
            if(temp[0:10] == "send_file "):  #receive file
                output_file = receive_file(connect, temp)
                inform_all("Successfully upload file "+ output_file + " to server, file id:" + str(file_id_counter))
            elif(temp[0:len("get_file ")] == "get_file "): #send files
                send_file(connect, nick, temp)
            else:
                inform_all(temp)
            message_dealer(data)
        except:
            inform_all(nick + " leaves the room!")           
            message_dealer(data)
            connect.close()
            return
    #came out of loop
 
def send_file(connect, nick, temp):
    global data
    
    if CON.acquire():
        if temp[0:9] == "get_file ":
            req_file_id = int(str(temp[9:]).strip(" "))
            try:
                req_file_id = int(str(temp[9:]).strip(" "))
                if req_file_id in file_dict:
                    file_server_path = file_dict[req_file_id]
                    data = "send_file_to;" + nick + "," +  file_server_path[file_server_path.rindex("/")+1:]
                    connect.send(data)
                    with open(file_server_path, "rb") as r:
                        while True:
                            data = r.read(1024)
                            if not data: break
                            connect.send(data)
                    r.close()
                    data = "EOF"
                    connect.send(data)
                    data = "Successfully send file id:" +  str(req_file_id) + " to " + nick + " !"             
                else:
                    data = "Wrong file id:" +  str(temp[9:]).strip(" ")
                    connect.send(data)
            except:
                data = "Sending "+ str(req_file_id) + " file fails."
                connect.send(data)
                
    CON.notifyAll()
    CON.release()
    
def inform_all(message):
    global data
    if CON.acquire():        
        data = message
        CON.notifyAll()
        CON.release()
  
def client_thread_output(connect, nick):
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
 
while True:
    connect, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    nick = connect.recv(1024)
    is_legal, msg = check_legal(nick)
    connect.send(msg)
    if is_legal:
        inform_all('Welcome ' + nick + ' to the room! There are ' + str((threading.activeCount() + 1) / 2) + ' member(s) online!')
        message_dealer(data)
        connect.send(data)
        threading.Thread(target = clientThreadIn , args = (connect, nick)).start()
        threading.Thread(target = client_thread_output , args = (connect, nick)).start()
    else:
        connect.close() 
s.close()