import multiprocessing
import os

def worker():
    """worker function"""
    print 'Worker %i using %s' % (os.getpid(), sys.executable)
    return

if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()
