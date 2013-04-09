import sys, runpy

#runpy.run_module(sys.argv[1])
runpy.run_path(sys.argv[1], run_name='__main__')
