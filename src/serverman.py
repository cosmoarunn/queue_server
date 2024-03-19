
import threading
from queue import Queue

import os, sys, time, yaml
from pathlib import Path
from uuid import uuid4
from supplyrunnerman import SupplyRunner
from multiprocessing.managers import BaseManager,SyncManager


PY3 = sys.version_info[0] == 3
# Python 2 vs. 3 compatibility
if PY3:
    from functools import reduce
else:
    import Queue as queue  

def iteritems(d):
    """Return an iterator over the items of a dictionary."""
    return getattr(d, 'items' if PY3 else 'iteritems')()

class DistibutedServer(SyncManager):
    config:dict = {}
    dir_name = os.path.dirname(__file__) + '/'
    project_dir = str(Path(__file__).parents[1]) + '/' 
    database_dir = project_dir + 'databases' + "/"

    def load_config(self, authkey:str = None ):
        self.log = ['Initializing server configuration..'] #also initializes log

        with open(os.path.join(self.project_dir, 'config.yaml')) as yaml_config_file:
            config = yaml.safe_load(yaml_config_file)
            
            self.config = { 
                'app_config': config['app'],
                'database_config' : config['database'],
                'externals_config' : config['externals'],
                'server_config' : config['server']
            }
        server_config = self.config['server_config']

        #auth_key = random.choice(api_keys)
        self.authkey = bytes(server_config['authkey'], 'utf-8')  if not authkey else bytes(authkey, 'utf-8')
       
def start_supplyrunner(get_queue, result_que):
    print('starting supplyrunner..')
    #the worker who push the jobs to  queue expecting results, server_address isn't needed but just for probing
    sr = SupplyRunner(address=server_address, authkey=authkey, get_Queue=get_queue, result_Queue=result_queue) 

if __name__ == '__main__':

    try:

        server_address = ('localhost', 8624)
        get_queue = result_queue = Queue()
        authkey = bytes("769ac424-adb6-5a73-83b0-d22eb27e543b", 'utf-8')  #comment out this line for random apikey

        '''w = Worker(queue) #QueueSupplyWorker(authkey, queue) #a worker object using the same queue
        w.start()'''

        threading.Thread(target=start_supplyrunner, args=[get_queue,result_queue]).start()
        #register queues statically
        DistibutedServer.register('get_queue', callable=lambda: get_queue)
        DistibutedServer.register('result_queue', callable=lambda: result_queue)

       

        ds = DistibutedServer(address=server_address, authkey=authkey)
        #ds.load_config(authkey=authkey)
        s = ds.get_server()
        
        
        #serve_forever must be the last since it enters the loop anything after this won't execute until keyboardinterrupt
        s.serve_forever()

    except KeyboardInterrupt:
        print("winding up..")
        time.sleep(2)
        print('bye, bye!')


    '''     
    dr = DistributedRunner(address=server_address, mQueue=queue)
    dr.load_config(authkey)
    dr.start()
        
    '''