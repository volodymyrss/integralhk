#!/bin/env python

import subprocess,pickle,datetime,re,urllib.request,urllib.parse,urllib.error,tempfile,time
import glob,os
import shutil,glob,os
from math import *

import pscolors as bcolors

from integralhk import support
from integralhk import spiacs_config
from integralhk.exception import GeneratorException

class BadTimeFormat(Exception):
    pass

def with_both_rbp(f):
    def nf(*a,**b):
        if 'rbp' in b and b['rbp'] is not None:
            print(("rbp already set to",b['rbp'],", will not iterate over ARC/NRT"))
        else:
            rbp=[spiacs_config.isdc_env['isdc_nrt'],spiacs_config.isdc_env['isdc_arc']]
            #rbp=[spiacs_config.isdc_env['isdc_arc'],spiacs_config.isdc_env['isdc_nrt']]
            b['rbp']=rbp
        print(("with",a,b))
        try:
            return support.try_all(key='rbp')(f)(*a,**b)
        except Exception as e:
            print(("with_both_rbp failed with",a,b))
            raise
    return nf


#########

rev_days=2.990997
rev_T0=1016.4021300000001

def revol(tstart):
    t=(tstart-rev_T0)/rev_days
    i=int(t)
    return i

rev1700_start = 6034.849157222222
rev1600_start = 5502.690279907407

def getphase(tstart):
    if tstart<100: return 0.5
    if tstart<5500:
        t=(tstart-rev_T0)%rev_days
        t/=rev_days
        return t
    rev_days_late=((rev1700_start-rev1600_start)/100.)
    rev=int((tstart-rev1600_start)/rev_days_late)
    return (tstart-rev1600_start-rev*rev_days_late)/rev_days_late


# timing

def time_interval(input):
    try:
        return float(input)
    except ValueError:
        raise BadTimeFormat("not time interval length: "+repr(input))

def utc_sec2utc(utc):
    d,t=utc
    h=int(t/3600)
    m=int((t-h*3600)/60)
    s=int((t-h*3600-m*60))
    sf=(t-h*3600-m*60-s)
    if sf>=1: raise Exception("WT?!")
    sf=("%.6f"%sf)[2:]
    return "%sT%.2i:%.2i:%.2i.%s"%(d,h,m,s,sf)

def utc2utc_sec(utc):
    D,T=utc.split("T")
    y,m,d=D.split("-")
    date=d+"/"+m+"/"+y[2:]
    
    H,M,S=list(map(float,T.split(":")))
    sec=H*3600+M*60+S
    
    return date,sec

def validate_utc(utc):
    utc=utc[:25] # limiting  precision (time has a problem with it)
    try:
        dt=time.strptime(utc,"%Y-%m-%dT%H:%M:%S")
    except ValueError as e:
        try:
            dt=time.strptime(utc,"%Y-%m-%dT%H:%M:%S.%f")
        except ValueError as e:
            raise BadTimeFormat("does not match the format of UTC; python says:"+str(e))   


def utc_sec2ijd(utc):
    validate_utc(utc) # as converttime is not dooing it right
    return float(utc2ijd(utc_sec2utc(utc)))

@with_both_rbp
def converttime(inpf,inp,outpf,rbp):
    print((bcolors.render("{RED}converttime{/} using {BLUE}"+str(rbp)+"{/}")))
    env=os.environ.copy()
    env['REP_BASE_PROD']=rbp
    env['PFILES']=env['HOME']+"/pfiles;"+env['ISDC_ENV']+"/pfiles"

    inps="%.30lg"%inp if isinstance(inp,float) else str(inp)
    c=["converttime",inpf,inps,outpf,"accflag=10"]
    print(("command:"," ".join(c)))

    try:
        pr=subprocess.check_output(c,env=env).decode()
    except subprocess.CalledProcessError as e:
        if re.search("DAL3GEN_INVALID_.*?_TIME",e.output.decode()):
            print(("failed bad time:",e))
            raise BadTimeFormat("bad time content: "+repr(inp)+" as "+repr(inpf))
        print(("called process failed, raising:",e))
        raise e
    except Exception as e:
        print(("failed:",e))
        raise e
    print(pr)

    r=re.search("Output Time\(%s\):(.*)"%outpf,pr)
    outt=r.groups(0)[0].strip()
    
    if outpf=="SCWID" and outt=="000000000000.000":
        raise Exception("conversion failed")

    return  outt

def utc2ijd(utc,rbp=None):
    validate_utc(utc) # as converttime is not dooing it right
    return float(converttime("UTC",utc,"IJD",rbp=rbp))

def autc2ijd(autc,rbp=None):
    r=re.match("(\d\d\d\d)(\d\d)(\d\d)T(\d\d)(\d\d)(\d\d)(\d{6})",autc)
    if not r:
        raise BadTimeFormat("does not match the format of UTC")
    g=r.groups()
    utc=g[0]+"-"+g[1]+"-"+g[2]+"T"+g[3]+":"+g[4]+":"+g[5]+"."+g[6]
    return utc2ijd(utc)

def ijd2utc(ijd,rbp=None):
    return converttime("IJD",ijd,"UTC",rbp=rbp)

def ijd2scw(ijd,rbp=None):

    try:
        scwid=converttime("IJD","%.20lg"%ijd,"SCWID",rbp=rbp)[:12]

        if len(scwid)!=12:
            raise Exception("conversion IJD to SCWID caused something weird")
    except Exception as e:
        print(("poorly handled exception",e))
        scwid="0"*12
        raise

    return scwid

def ijd2utc_sec(ijd):
    return utc2utc_sec(ijd2utc(ijd))

def x2ijd(x,rbp=None):
    if isinstance(x,float) or isinstance(x,int):
        print("float must be IJD: IJD found!")
        return x
    
    if not isinstance(x,str):
        print("should be float or string")
        raise BadTimeFormat("can not interpret time (shoud be float or string) "+repr(x))


    if re.match("\d+(\.\d*)?$",x):
        print(("IJD found!",x))
        try:
            return float(x)
        except:
            raise BadTimeFormat("can not interpret time, looks like IJD "+repr(x))


    if re.match("\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.?\d*",x):
        print("UTC found!")
        return utc2ijd(x,rbp=rbp)
    
    if re.match("\d\d\d\d\d\d\d\dT\d\d\d\d\d\d\d{6}",x):
        print("alternative UTC found!")
        return autc2ijd(x,rbp=rbp)
    
    print(("can not interpret time:",x))
    raise BadTimeFormat("can not interpret time "+repr(x))



