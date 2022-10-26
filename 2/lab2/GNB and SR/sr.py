import random, socket
from select import select
from server import HOST

class SR:
    def __init__(self, local_addr: tuple, remote_addr: tuple):
        self.WINDOW_BASE = 0
        self.next_seq = 0
        self.local = local_addr
        self.remote = remote_addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.local)
        self.DATA = []

        self.WRITE_FILE_DATA('', mode='w')
        self.READ_FILE_DATA()
        self.time_counts = {}
        self.ack_seqs = {}
        self.rcv_base = 0
        self.rcv_data = {}

    def send_data(self):
        if self.next_seq == len(self.DATA):
            return
        if self.next_seq < self.WINDOW_BASE+(WINDOW_SIZE := 4):
            if random.random() > (PACKAGE_LOSS := 0.1):
                self.socket.sendto(HOST.build_package(self.next_seq, self.DATA[self.next_seq]), self.remote)
            self.time_counts[self.next_seq] = 0
            self.ack_seqs[self.next_seq] = False
            print(f'[+] Data Sent Successfully [{str(self.next_seq)}]')
            self.next_seq += 1

    def timeout_handler(self, time_out_seq):
        print(f'[*] Timeout ({str(time_out_seq)}) Resending ')
        self.time_counts[time_out_seq] = 0
        if random.random() > (PACKAGE_LOSS := 0.1):
            self.socket.sendto(HOST.build_package(time_out_seq, self.DATA[time_out_seq]), self.remote)
    
    def READ_FILE_DATA(self):
        f = open('FILE.txt', 'r', encoding='utf-8')
        while True:
            send_data = f.read(2048)
            if len(send_data) <= 0:
                break
            self.DATA.append(send_data)
    
    def WRITE_FILE_DATA(self, data, mode='a'):
        with open('SAVED.txt', mode, encoding='utf-8') as f:
            f.write(data)        
    
    def slide_send_window(self):
        while self.ack_seqs.get(self.WINDOW_BASE):
            self.WINDOW_BASE += 1
            print(f'* SERVER: window slided ({str(self.WINDOW_BASE)})')
    
    def slide_rcv_window(self):
        while self.rcv_data.get(self.rcv_base):
            self.WRITE_FILE_DATA(self.rcv_data.get(self.rcv_base))
            self.rcv_base += 1
            print(f'* CLIENT: window slided ({str(self.rcv_base)})')

    def server_run(self):
        while True:
            self.send_data()
            readable = select([self.socket], [], [], 1)[0]
            if len(readable) > 0:
                rcv_ack = self.socket.recvfrom(BUFFER_SIZE := 10)[0].decode().split()[0]
                if self.WINDOW_BASE <= int(rcv_ack) < self.next_seq:
                    print(f'[*] ACK Received [{rcv_ack}]')
                    self.ack_seqs[int(rcv_ack)] = True
                    if self.WINDOW_BASE == int(rcv_ack):
                        self.slide_send_window()
            for seq in self.time_counts.keys():
                if not self.ack_seqs[seq]:
                    self.time_counts[seq] += 1
                    if self.time_counts[seq] > (TIME_OUT := 5):
                        self.timeout_handler(seq)
            if self.WINDOW_BASE == len(self.DATA):
                self.socket.sendto(HOST.build_package(0, 0), self.remote)
                print('================================================\n* Message from server : Sent successfully!')
                break

    def client_run(self):
        while True:
            readable = select([self.socket], [], [], 1)[0]
            if len(readable) > 0:
                rcv_data = self.socket.recvfrom(1024)[0].decode()
                rcv_seq = rcv_data.split()[0]
                rcv_data = rcv_data.replace(rcv_seq+' ', '')
                if rcv_seq == '0' and rcv_data == '0':
                    print('* Message from client : Sent successfully!')
                    break
                print(f'* Message from client : data recieved ({rcv_seq})')
                if self.rcv_base - (WINDOE_SIZE := 4) <= int(rcv_seq) < (self.rcv_base+WINDOE_SIZE):
                    if self.rcv_base <= int(rcv_seq) < self.rcv_base+WINDOE_SIZE:
                        self.rcv_data[int(rcv_seq)] = rcv_data
                        if int(rcv_seq) == self.rcv_base:
                            self.slide_rcv_window()
                    if random.random() >= (ACK_LOSS := 0): # 模拟引入数据包的丢失
                        self.socket.sendto(HOST.build_package(int(rcv_seq), 0), self.remote)