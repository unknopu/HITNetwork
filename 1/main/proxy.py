import socket
import sys
import threading
import os
import ssl
from urllib.parse import urlparse


def main():
    global config 
    config = configuration()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((config['HOST'], config['PORT']))
        s.listen(config['MAX'])

        print("[*] Intializing socket successfully ... ")
        print("[*] Socket binded successfully ...")
        print(f"[*] Server started successfully at :{config['PORT']}")
        print("--------------------------------------")
    except Exception as e:
        print(e)
        sys.exit(2)

    while 1:
        try:
            conn, addr = s.accept()
            threading._start_new_thread(conn_string, (conn, addr))
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Server shutting down ...")
            sys.exit(2)
    s.close()

def conn_string(conn, addr):
    try:
        print(f"[+] Request from {addr[0]}:{addr[1]}")
        request = conn.recv(config['BUFFER'])

        http = request.decode('utf-8').split('\n')[0]
        url_parse = urlparse(http.split()[1])
        if http.startswith('CONNECT'):
            print("\n[*] Server only support :80")
            return

        if addr[0] in config['BLOCK_USER']:
            conn.send(str.encode('HTTP/1.1 403 Forbidden\r\n'))
            conn.close()
            print("*** WARNNING!! this user is blocked.")
            return
        if url_parse.hostname in config['BLOCK_HOST']:
            conn.send(str.encode('HTTP/1.1 403 Forbidden\r\n'))
            conn.close()
            print("*** WARNNING!! this server is blocked.")
            return
        port = 80

        print(f"[+] webserver : {url_parse.hostname}:{port}")
        proxy_server(url_parse, port, conn, request, http)
    except  Exception as e:
        print(e)
    
def proxy_server(webserver, port, conn, request, http):

    import hashlib, time

    CACHE_DIR = os.path.join(os.path.dirname(__file__), 'CACHE')
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(100)
        s.connect((webserver.hostname, port))
        
        # forward data back to client
        m = hashlib.md5()
        m.update(str.encode(webserver.hostname + webserver.path))
        filename = os.path.join(CACHE_DIR, m.hexdigest()+'.cached')

        if os.path.exists(filename):
            timestamp = (time.strptime(time.ctime(os.path.getmtime(filename)),"%a %b %d %H:%M:%S %Y"))
            tmp = http + '\n' + 'If-Modified-Since: ' + time.strftime('%a, %d %b %Y %H:%M:%S GMT', timestamp) + '\n'
            for line in request.decode().split('\n')[1:]:
                tmp += line + '\n'
            s.sendall(str.encode(tmp))
            first = True
            openfile = open(filename, 'ab')
            while True:
                reply = s.recv(config['BUFFER'])
                if first:
                    if reply.decode('iso-8859-1').split()[1] == '304':
                        print(f'Cache hit: {webserver.hostname}{webserver.path}')
                        conn.send(open(filename, 'rb').read())
                        break
                    else:
                        o = open(filename, 'wb')
                        print(f'Cache update: {webserver.hostname}{webserver.path}')
                        if len(reply) > 0:
                            conn.send(reply)
                            openfile.write(reply)
                        else:
                            break
                        first = False
                else:
                    o = open(filename, 'ab')
                    if len(reply) > 0:
                        conn.send(reply)
                        openfile.write(reply)
                    else:
                        break
            openfile.close()

        else:
            print(f'Cache miss: {webserver.hostname}{webserver.path}')

            s.sendall(request)

            openfile = open(filename, 'wb')
            while 1:
                reply = s.recv(config['BUFFER'])
                if len(reply) > 0:
                    conn.send(reply)
                    openfile.write(reply)
                else:
                    break
            openfile.close()
      
        s.close()
        conn.close()
    except socket.error as e:
        print("[-] WARNNING!1 proxy server ",e)
        s.close()
        conn.close()
        sys.exit(1)



def configuration() -> dict:

    import configparser
    file = str(os.path.abspath(os.getcwd())) + '/config.ini'
    parser = configparser.ConfigParser()
    parser.read(file)
    config = {}
    config['HOST'] = parser.get("CONFIGURATION", "host")
    config['PORT'] = int(parser.get("CONFIGURATION", "port"))
    config['BUFFER'] = int(parser.get("CONFIGURATION", "buffer"))
    config['CACHE_BUFFER'] = int(parser.get("CONFIGURATION", "cache"))
    config['MAX'] = int(parser.get("CONFIGURATION", "max"))
    config['BLOCK_HOST'] = parser.get("BLOCK", "host")
    config['BLOCK_USER'] = parser.get("BLOCK", "user")
    return config

if __name__ == '__main__':
    main()