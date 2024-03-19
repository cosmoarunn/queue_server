# QueueServer

QueueServer is a tool which utilises python's multiprocessing BaseManager and SyncManager to initialize and run queueservers on both local and remote machines. 
 

<!-- ABOUT THE PROJECT -->
## About The Project

QueueServer demonstrates a working example (but not limited to) of factorizing a list of supplied numbers and collecting results in an infinite loop. QueueServer can run anywhere in a remote machine and can connect to multiple clients and distribute the job.

### Runners
- Runner
    Base implementation for runners that run any callable in single or batch
- ProcRunner
    Runners that run a single process or a batch of repeted process on ProcessPoolExecutor
- ThreadRunner
    Runners that run multiple threads on ThreadPoolExecuto

#### further development
* process augmentation using pipes on runner objects


For further reference visit [SyncManager](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.managers.SyncManager)
    
## Installation & running

- open a terminal and clone the repository from github  
        `git clone && cd queue_server`

- create a virtual environment in the folder 
    `python3 -m venv venv`
    and activate virtual environment,
    `source venv/bin/activate`

- intall requirements file 'requirement.txt'
    ` pip3 install -r requirements`

- edit configurations YAML at 'config.yaml'

- start the queue server, 
    `python3 src/serverman.py`

- open another terminal and run,
    `source venv/bin/activate`
    to run a single client:  `python3 src/clientman.py`
    
- open as many terminals as needed (for each new client) and run the clientman.py to visualize the queue job distribution

- run serverman.py in any server machine and execute `python3 serverman.py` and connect it from local machine `python3 clientman.py`.

## License
[MIT](https://choosealicense.com/licenses/mit/) 

## Acknowledgements ❤️ 
- [Eli Bendersky](https://eli.thegreenplace.net/2012/01/24/distributed-computing-in-python-with-multiprocessing) (for simple factorization)
- [Awesome README](https://github.com/matiassingers/awesome-readme)


## Contributors 💙 
-  [Arun Panneerselvam](https://www.arunpanneerselvam.com)

