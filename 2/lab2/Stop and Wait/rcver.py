import socket, random
from ast import literal_eval


#------------------------------------------------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host ="127.0.0.1"
port =8000
s.connect((host,port))
PR_NO_ACK = 0.1
count = 0 
output = ""
#------------------------------------------------------------------------

while True: 
    data=s.recv(8).decode()
    print(f'Received data : {data}')
    datadict = literal_eval(data)
    index = list((datadict).keys())[0]
    number = random.randint(0,1000)
    if not count:
        count += 1
        current = index
        previous = 0
        if not current:
            previous = 1
    else: 
        count += 1
        previous = current
        current = index
        
    if abs(previous-current) == 1:
        output  += list(datadict.values())[0]
        if not random.randint(0, 6):
            print("[-]Acknowledgement not sent")
            pass
        else:    
            s.send("Acknowledgement: Message Received".encode())
    else: 
        s.send("Acknowledgement: Message Received".encode())
        print ("[-] Indices failed. Sending ack for previous")
    print(f'Received bitstring : {output}')
  