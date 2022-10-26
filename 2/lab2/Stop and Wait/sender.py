import socket, time, random, threading

#-----------------------socket creation
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 8000
s.bind( (host, port) )

propogation = 12
l = [i for i in range(0, 1000)]

class client(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.start()
        
#-----------------------user run
    def start(self):
        package_buff = str(input("ENTER BIT STRINGS : "))
        
        i = 0
        while i < len(package_buff):
            DATA_INDEX = {}
            DATA_INDEX = {i%2 : package_buff[i], }
            
            sendstring = str(DATA_INDEX)
            
            current_time = time.time()
            if not random.randint(0, 1):
                clientsocket.send(sendstring.encode())
                time.sleep(1.5)
                compare_time = time.time()
                ackflag= False
            
            else: 
                time.sleep(1.5)
                compare_time = time.time()
                print("[-] Package dropped (1)")
                ackflag= False               

            while True:
                if compare_time-current_time<=propogation:
                    compare_time= time.time()
                    clientsocket.settimeout(2)

                    try:
                        recieved = clientsocket.recv(1024)
                        msg = recieved.decode('utf-8')
                        if msg != '' :
                            print(f'[+] {msg}')
                        
                        if recieved:
                            print("[+] ACK received")
                            i = i+1
                            ackflag = True
                            break 

                    except:
                        if (compare_time-current_time)>propogation and not ackflag:
                            print ("[-] Timeout!!", end=" - ")
                            if not random.randint(0, 1):
                                clientsocket.send(sendstring.encode())
                                print("package resend")
                            else: 
                                print("package dropped 2")
                            current_time = time.time()
                            compare_time = time.time()
        
s.listen(5)
print('[*] Server is listening ..')
while True:
    clientsocket, address = s.accept()
    print(f'[*] Receiver connected at {address[0]}:{address[1]} ')
    client(clientsocket, address)