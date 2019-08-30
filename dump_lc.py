try:
    import spiacs_config
except ImportError:
    print("no spiacs-config: standalone")

import copy,tempfile,os,subprocess,re,resource,fcntl

class DumpLCException(Exception):
    pass

class BadTarget(DumpLCException):
    def __init__(self,s=""):
        DumpLCException.__init__(self,"Bad Target"+s)

class NoAccess(DumpLCException):
    def __init__(self,s=""):
        DumpLCException.__init__(self,"No access to the data"+s)

class OverRevolution(DumpLCException):
    def __init__(self):
        DumpLCException.__init__(self,"Over revolution")

#class DumpLCInternalException(DumpLCException):
class DumpLCUnhandledException(Exception):
    def __init__(self):
        DumpLCException.__init__(self,"dump_lc returned non-zero")

class NoData(DumpLCException):
    def __init__(self,s=""):
        DumpLCException.__init__(self,"No Data (at this time?) "+s)

class ZeroData(DumpLCException):
    def __init__(self,s=""):
        DumpLCException.__init__(self,"Zero Data (at this time?)"+s)

class NoAuxData(DumpLCException):
    def __init__(self):
        DumpLCException.__init__(self,"No Auxiliaty Data (for this time?)")

def get_open_fds():
    fds = []
    for fd in range(3,resource.RLIMIT_NOFILE):
        try:
            flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        except IOError:
            continue

        fds.append(fd)
    return fds

def close_all(f):
    
    def nf(*a,**aa):
        before=get_open_fds()
        r=f(*a,**aa)
        after=get_open_fds()
        diff=[a for a in after if a not in before]
        print "open before and after",before,after,diff
        return r

    return nf

@close_all
def dump_lc(utc1,utc2,mode=0,target="ACS",rbp=None,dump_lc_path=None):
    if dump_lc_path is None:
        dump_lc_binary=spiacs_config.dump_lc_binary
        dump_lc_path=spiacs_config.dump_lc_path
    else:
        dump_lc_binary=dump_lc_path+"/dump_lc"


    tf=tempfile.mkstemp(suffix="acs")
    command=[dump_lc_binary,
            "start_time_utc="+utc1,
            "stop_time_utc="+utc2,
            "target="+target,
            "output="+tf[1],
            "orbit_accy=30",
            "mode=%i"%mode]

    env=copy.deepcopy(os.environ)
    env['PFILES']=dump_lc_path
    env['REP_BASE_PROD']=rbp

    print "command:"," ".join(command)
    print "env:",env['PFILES']

    #otf=tempfile.mkstemp()
    #otfh=open(otf[1])

    exception=None
    try:
        output=subprocess.check_output(command,env=env)
    except subprocess.CalledProcessError as e:
        exception=e
        print "dump_lc returns",repr(e)
        output=exception.output

    try:
        off=open(tf[1])
        result="".join(list(off))
        off.close()
        os.remove(tf[1])
        os.close(tf[0])
    except Exception as e:
        print "could not read temp file?.."
        raise
   # p.wait()

    #output="\n".join(list(otfh))

    #otfh.close()
    #os.remove(otf[1])

    print "output:",output

    if re.search("Error_0: unknown target",output):
        raise BadTarget(" "+target)
    
    s=re.search("unable to read.*? skipping",output)
    if s:
        print "found problems: probably no permission to access"
        #raise NoAccess(" probably no permission to access")
    
    if re.search("No ScW files in here",output):
        raise NoData("requested: "+utc1+" ... "+utc2)
    
    s=re.search("Read (.*?) ScW files with 0 bins",output)
    if s:
        raise NoData(" in %s ScW"%s.group(1))

    if re.search("Fatal! Execution failed with exit code -25501",output):
        raise NoAuxData()
    
    if re.search("Fatal! Execution failed with exit code -25502",output):
        raise NoAuxData()
    
    if re.search("Fatal! Execution failed with exit code -2550",output):
        raise NoAuxData()
    
    if re.search("overrevolution!",output):
        raise OverRevolution()

    errors=re.findall("^Error_. *(.*?)\n",output,re.S and re.M)
    if errors!=[]:
        print "noticed unhandled errors in the output:",errors
        raise Exception("\n".join(errors))

    if exception is not None:
        raise DumpLCUnhandledException(repr(exception))
    
    errors=re.findall("^Warn_.*?\n",output,re.S)
    if errors!=[]:
        print "noticed warnings in the output:",errors

    def sfloat(x):
        try:
            return float(x)
        except:
            return 0

 #   print result
    if mode==0 and all([sfloat(a.split()[2])==0 for a in result.split("\n") if len(a.split())>=4]):
        raise ZeroData()

    print "leaving dump_lc"

    return result,output
