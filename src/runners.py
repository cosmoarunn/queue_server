
import uuid
import threading
from multiprocessing import Process
from utils.runnerutils import _argsList,_kwArgsType, pipeType
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor

class Runner(object):

    def __init__(self) -> None:
        pass
    

    def _run(self, handler:callable, args:_argsList):
        "single run the handler func / trial test run on main thread"
        try:
            return handler(*args)
        except KeyboardInterrupt:
            return


    def _batch__run(self, handler:callable, args:_argsList, _yield:bool = False):
        "batch run will run the iteration forever until a keyboar interrupt(then returns)" 
        "a generator always executes and yields results," 
        "and if _yield is set to true, batch_run returns values in an array only if the callable function returns any value "

        cnt = 1
        while cnt < len(args):
            _resp = None
            try:
                _resp =  handler(*args[cnt])
                cnt += 1
                if _yield: 
                    yield _resp
            except KeyboardInterrupt:
                return _resp


class ThreadRunner(Runner):

    def __init__(self, max_threads:int=5) -> None:

        self.max_threads:int = max_threads
    
    def _run(self, handler, args=[], kw_args={}, daemon=False):
        "default runnning threads "
        if not hasattr(self, 'runnerThread'):
            self.runnerThread = threading.Thread(target=handler, args=args, kwargs=kw_args)
            self.runnerThread.daemon = daemon
            self.runnerThread.start()
            self.runnerThread.join()
    
    def _batch__run(self, handler:callable, args, _yield=False, runner_id:str = uuid.uuid4()):
        "batch run is executed using threadpool"
        "runner_id: an unique identifier to prefix the threads' name"
        #print("running batch threads on executor. please wait..")

        if not hasattr(self, 'executor'):
            with ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix=runner_id) as self.executor:
                results = self.executor.map(handler, [*args])
                self.thread_count = self.executor._threads.__len__
                if _yield: 
                    yield results
                else: 
                    return results


    def _terminate(self, wait=True, cancel_futures=False):
        "terminate afrer certain condition"
        "warning: awaits until joins, refer thread.join "
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=wait)


class ProcRunner(Runner):

    max_workers: int
    max_tasks_per_child: int
    is_batch_runner: bool

    def __init__(self, handler:callable = None, args:list = [], kwargs:dict = {}, daemon:bool = False, max_workers:int=1, max_tasks_per_child:int = None, is_batch_runner:bool = False) -> None:

        self.max_workers = max_workers
        self.max_tasks_per_child = max_tasks_per_child #None => worker processes lives as long as the executor
    
        #light it up, the fireworks!!!!
        if not is_batch_runner:
            self._run(handler=handler,args=args, kw_args=kwargs, daemon=daemon )
        else:
            #TODO: kwargs must be used in batch run
            self._batch__run(handler=handler,args=args, daemon=daemon )
        
    def _run(self, handler:callable, args=[], kw_args={}, daemon=False):
        "default runnning process "

        print("Starting single runner..")
        if not hasattr(self, 'runnerProcess'):
            self.runnerProcess = Process(target=handler, args=args, kwargs=kw_args, daemon=False)
            if self.runnerProcess:
                self.runnerProcess.start()

                self.runnerProcess.join()
        return self.runnerProcess
    
    def _batch__run(self, handler:callable, args, _yield=False, runner_id:str = uuid.uuid4()):
        "batch run is executed using threadpool"
        "See ProcesPoolExecutor for further reference"
        print("Starting batch runner..")
        if not hasattr(self, 'executor'):
            with ProcessPoolExecutor(max_workers=self.max_workers, max_tasks_per_child=self.max_tasks_per_child) as self.executor:
                results = self.executor.map(handler, [*args])
                self.process_count = self.executor._processes.__len__
                if _yield: 
                    yield results
                else: 
                    return results


    def _terminate(self, wait=True, cancel_futures=False):
        "terminate afrer certain condition"
        "warning: awaits until joins, refer thread.join "
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=wait)


    def run(self, handler, args=[], kw_args={}, daemon=False):
        "Guard routine for _run"
        return self._run(handler, args, kw_args, daemon=daemon)
    




'''
# Example USAGE

def trial_run(args):
    max, verbose = args
    #print(*max*('-*-',), sep='_')
    for _ in range(0, max, 1):
        print("\n{}: {}".format(verbose, max))
    return max

if __name__ == "__main__":

    tr = ProcRunner(10)

    single_args = [10, "I'm a Single Process funning for : "]
    tr._run(trial_run, single_args)

    batch_args = [(count, "I'm a batch count Running in batch process run!") for count in range(1, 6, 1)]
    batch_res = tr._batch__run(trial_run, batch_args)

    try:
        next(batch_res)
    except StopIteration:
        print("\nEnd of ProcRunner execution. All done under the gun!")'''