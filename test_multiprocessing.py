import multiprocessing
import os, time

def worker():
    """
        Worker function
    """
    print 'Worker %i using %s' % (os.getpid(), sys.executable)

if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()
    while jobs:
        p = jobs.pop()
        p.join()
        print 'Worker %r joined' % p
    print 'Works.'
