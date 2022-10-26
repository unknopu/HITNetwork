import  os
from threading import Thread

class HOST:
    def __init__(self) -> None:
        config = self.configuration()
        self.addr1 = (config['HOST1'][0], int(config['HOST1'][1]))
        self.addr2 = (config['HOST2'][0], int(config['HOST2'][1]))
        print(self.addr1, self.addr2)
    
    def build_package(number: str, data: str) -> bytes:
        return (f'{number} {data}').encode(encoding='utf-8')
    
    def GBN_START(self):
        from gbn import GBN 
        h1 = GBN(self.addr1, self.addr2)
        h2 = GBN(self.addr2, self.addr1)
        Thread(target=h1.server_run).start()
        Thread(target=h2.client_run).start()
    
    def SR_START(self):
        from sr import SR
        h1 = SR(self.addr1, self.addr2)
        h2 = SR(self.addr2, self.addr1)
        Thread(target=h1.server_run).start()
        Thread(target=h2.client_run).start()
        
    def configuration(self) -> dict:
        import configparser
        file = str(os.path.abspath(os.getcwd())) + '/config.ini'
        parser = configparser.ConfigParser()
        parser.read(file)
        config = {}
        config['HOST1'] = parser.get("HOST", "host1").split(':')
        config['HOST2'] = parser.get("HOST", "host2").split(':')
        return config
    

if __name__ == '__main__':
    host = HOST()
    host.GBN_START()
    # host.SR_START()    