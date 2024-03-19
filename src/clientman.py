import os, time
from pathlib import Path
from uuid import uuid4

from runners import ProcRunner
import multiprocessing
from multiprocessing.managers import BaseManager

import yaml

class DistributedClient(BaseManager, ProcRunner):

    #hard coded properties for convenience. No change in values
    start_time = time.perf_counter()
    dir_name = os.path.dirname(__file__) + '/'
    project_dir = str(Path(__file__).parents[1]) + '/' 
    database_dir = project_dir + 'databases' + "/"
    

    #service props
    app: None
    config:dict = {}
    server_config:dict = {}
    #misc
    results = []

    def load_config(self ):
        self.log = ['Initializing server configuration..'] #also initializes log

        with open(os.path.join(self.project_dir, 'config.yaml')) as yaml_config_file:
            config = yaml.safe_load(yaml_config_file)
            
            self.config = { 
                'app_config': config['app'],
                'database_config' : config['database'],
                'externals_config' : config['externals'],
                'server_config' : config['server']
            }
        self.server_config = self.config['server_config']
        
    def connect_to_server(self):
        "connect to server as a client who works on queue jobs"
        self.load_config()

        self.connect() #the difference is here. you don't `start` but `connect`
        
        print('Client connected at port {} with api_key {}'.format(self.server_config['port'], self.server_config['authkey'] ))
        self.run()
        print('shutting client down in 2 secs..')
        time.sleep(2)
       
        self._terminate()
        return self
    
    def run(self):
        print("Initializing proc runner on client..")

        self.mp_factorizer(5)

    def mp_factorizer(self, nprocs, shared_job_q=None, shared_result_q=None):
        
        print("factorizing numbers using {} processes..".format(nprocs))
        print(self.get_queue)
        print(self.result_queue)
        

        procs = []
        for i in range(nprocs):
            '''p = multiprocessing.Process(
                    target=self.factorizer_worker,
                    args=(self.get_queue, self.result_queue))
            procs.append(p)
            p.start()

        for p in procs:
            p.join()'''
            self.factorizer_worker()

    def factorizer_worker(self, job_q = None, result_q = None, interval=1):
        myname = multiprocessing.current_process().name
        while True:
            try:
                job = self.get_queue().get_nowait()
                print('%s got %s nums...' % (myname, len(job)))
                outdict = {n: self.factorize_naive(n) for n in job}
                print(outdict)
                self.result_queue().put(outdict)
                print('  %s done' % myname)
            except Exception as e:
                print("{}: jobs queue seems to be empty. returning..".format(myname))
                return
            time.sleep(interval)

    def factorize_naive(self, n):
        """ A naive factorization method. Take integer 'n', return list of
            factors.
        """
        if n < 2:
            return []
        factors = []
        p = 2

        while True:
            if n == 1:
                return factors

            r = n % p
            if r == 0:
                factors.append(p)
                n = n // p
            elif p * p >= n:
                factors.append(n)
                return factors
            elif p > 2:
                # Advance in steps of 2 over odd numbers
                p += 2
            else:
                # If p == 2, get to 3
                p += 1
        assert False, "unreachable"
        
def parseArguments():
    import argparse
    parser = argparse.ArgumentParser(description='Start a bi-directional udp server..')
    parser.add_argument('-p', '--port', required=False,type=int,
                        help='The port where which the server is listening to. Eg: 9000  (If not specified a random port from 59000 to 59999 will be used)' )
    parser.add_argument('-k', '--key', required=False,type=str,
                        help='for now, just copy it from server coz its running random apikeys..')
    parser.add_argument('-v', '--verbose', required=False,type=str,
                        help='if set to true or 1, provides detailed and extensive output or information.')

    return parser.parse_args()

if __name__ == "__main__":

    args = parseArguments()
    PORT = args.port if isinstance(args.port, int) else 8624 
    authkey = args.key
    authkey = bytes("769ac424-adb6-5a73-83b0-d22eb27e543b", 'utf-8') #comment out this line for random apikey
    server_address = ('localhost', PORT)

    #early binding
    DistributedClient.register('get_queue')
    DistributedClient.register('result_queue')

    #api key must be specified as that of server
    dc = DistributedClient(address=server_address, authkey=authkey)
   
    print('Connecting to server at {} using key {}'.format(server_address, authkey))
    dc.connect_to_server()
    