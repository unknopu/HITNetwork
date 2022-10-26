import random, socket
from select import select
from server import HOST

class GBN:
    def __init__(self, local_addr: tuple, remote_addr: tuple):
        self.local = local_addr
        self.remote = remote_addr
        self.WINDOW_BASE = 0
        self.next_seq = 0
        self.TIME_COUNTER = 0
        self.time_out = 5
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.local)
        self.DATA = []
        self.exp_seq = 0
        self.READ_FILE_DATA()
        self.WRITE_FILE_DATA('', mode='w')
    
    def send_data(self):
        if self.next_seq == len(self.DATA):
            return
        if self.next_seq - self.WINDOW_BASE < (WINDOW_SIZE := 4):
            if random.random() > (PACKAGE_LOSS := 0.1):
                self.socket.sendto(HOST.build_package(self.next_seq, self.DATA[self.next_seq]), self.remote)
            print(f'[+] Data Sent Successfully [{str(self.next_seq)}]')
            self.next_seq += 1
            
    def timeout_handler(self):
        print('[*] Timeout Resending ..')
        for i in range(self.WINDOW_BASE, self.next_seq):
            if random.random() > (PACKAGE_LOSS := 0.1):
                self.socket.sendto(HOST.build_package(i, self.DATA[i]), self.remote)
            print(f'[*] Data Resended => ({str(i)})')
        self.TIME_COUNTER = 0
        
    def READ_FILE_DATA(self):
        f = open('FILE.txt', 'r', encoding='utf-8')
        while True:
            send_data = f.read(1024)
            if len(send_data) <= 0:
                break
            self.DATA.append(send_data)
        
    def WRITE_FILE_DATA(self, data, mode='a'):
        with open('SAVED.txt', mode, encoding='utf-8') as f:
            f.write(data)

    def server_run(self):
        while True:
            self.send_data()
            readable = select([self.socket], [], [], 1)[0]
            if len(readable) > 0:
                rcv_ack = self.socket.recvfrom(ACK_BUFFER := 10)[0].decode().split()[0]
                print(f'[*] ACK Received [{rcv_ack}]')
                self.WINDOW_BASE, self.TIME_COUNTER = int(rcv_ack)+1, 0
            else:
                self.TIME_COUNTER += 1
                if self.TIME_COUNTER > (TIMEOUT := 5):
                    self.timeout_handler()
            if self.WINDOW_BASE == len(self.DATA):
                self.socket.sendto(HOST.build_package(0, 0), self.remote)
                print('==================================\n* Message from server : Sent successfully!')
                break
            
    def client_run(self):
        while True:
            readable = select([self.socket], [], [], 1)[0]
            if len(readable) > 0:
                rcv_data = self.socket.recvfrom(BUFFER := 2048)[0].decode()
                rcv_seq = rcv_data.split()[0]
                rcv_data = rcv_data.replace(rcv_seq+' ', '')
                if rcv_seq == '0' and rcv_data == '0':
                    break
                if int(rcv_seq) == self.exp_seq:
                    print(f'* Message from client, Received expected serial number ({str(rcv_seq)})')
                    self.WRITE_FILE_DATA(rcv_data)
                    self.exp_seq += 1
                else:
                    print(f'* Message from client, Wrong!!serial number received ({str(self.exp_seq)}), Expected : ({str(rcv_seq)})')
                if random.randint(0, 5) == (ACK_LOSS := 0):  # 模拟引入数据包的丢失
                    self.socket.sendto(HOST.build_package(self.exp_seq-1, 0), self.remote)