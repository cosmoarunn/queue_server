from functools import reduce
import yaml
import os, sys, time 
from uuid import uuid4
from queue import Queue
from pathlib import Path
from runners import ProcRunner
from utils.runnerutils import bytes_verbose, clear_terminal_display

PY3 = sys.version_info[0] == 3
'''
# Python 2 vs. 3 compatibility
if PY3:
    from functools import reduce
else:
    import Queue as queue   '''

def iteritems(d):
    """Return an iterator over the items of a dictionary."""
    return getattr(d, 'items' if PY3 else 'iteritems')()

class SupplyRunner(ProcRunner):

    #hard coded properties for convenience. No change in values
    start_time = time.perf_counter()
    dir_name = os.path.dirname(__file__) + '/'
    database_dir = str(Path(__file__).parents[1]) + '/' + 'databases' + "/"

    #service props
    app: None
    config:dict = {}
    _ledger:dict = {}
    #misc
    results = metrics = logs = []

    def __init__(self,address, authkey = None, get_Queue:Queue = None, result_Queue:Queue = None) -> None:
        #handler:callable = None, args:list = None, kwargs:list = None, daemon:bool = False, max_workers: int = 5, max_tasks_per_child:int  = None
        
        if not authkey:
            self.load_config()
       
        self.jobQueue = get_Queue
        self.resultQueue = result_Queue

        #super the legendary ProcRunner
        #super().__init__(self.commence_sequence, [self.jobQueue, self.resultQueue])
        self.commence_sequence(self.jobQueue, self.resultQueue)

    def load_config(self):
        self.log = ['Initializing configuration..'] #also initializes log

        with open(os.path.join(self.dir_name, 'config.yaml')) as yaml_config_file:
            config = yaml.safe_load(yaml_config_file)
            
            self.config = { 
                'app_config': config['app'],
                'database_config' : config['database'],
                'externals_config' : config['externals'],
                'server_config' : config['webserver']
            }
        server_config = self.config['server_config']

        if not self.authkey:
            self.authkey = bytes(server_config['authkey'], 'utf-8') 
       
       
    def commence_sequence(self, job_q = None, result_q = None, interval:int = 1):
        
        print('commencing queue jobs..')
        
        N = 999
        nums = [999999999999]
        for i in range(N):
            nums.append(nums[-1] + 2)

        chunksize = 43
        #for i in range(0, len(nums), chunksize):
        i = dt_tx = 0
        
        while True:
            try:
                clear_terminal_display()
                print('\nSupply runner (worker): ')
                print('Currently pushing job (to queue at index {}) :  \n\n{}'.format( i, nums[i:i + chunksize]))
                print("\nQueues in play:")
                print(job_q)
                print(result_q)

                chunk = nums[i:i + chunksize]
                dt_tx +=  sys.getsizeof(chunk)

                print("Data Transferred: {}".format(bytes_verbose(size_bytes=dt_tx)))
                job_q.put(chunk)
                i += 1
                time.sleep(interval)
            except KeyboardInterrupt:
                break

        numresults = 0
        resultdict = {}

        while numresults < N:
            #fetch the results
            print("Awaiting results from client(s)..")
            outdict = result_q.get()
            
            if isinstance(outdict, dict):
                resultdict.update(outdict)
                numresults += len(outdict)

        for num, factors in iteritems(resultdict):
            product = reduce(lambda a, b: a * b, factors, 1)
            if num != product:
                assert False, "Verification failed for number %s" % num

        print('distribution done!')
        time.sleep(0.2)


if __name__ == "__main__":

    server_address = ('localhost', 8624)
    queue = Queue()

    authkey = "769ac424-adb6-5a73-83b0-d22eb27e543b"  #comment out this line for random apikey

    #early binding
    SupplyRunner.register('get_queue')
    SupplyRunner.register('result_queue')

    sr = SupplyRunner(address=server_address)
    sr.load_config()


