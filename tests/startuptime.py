import resource
r = resource.getrusage(resource.RUSAGE_SELF)
print ('Startup time: %f sec = %fu + %fs sec' % (
    r.ru_utime + r.ru_stime,
    r.ru_utime,
    r.ru_stime))
