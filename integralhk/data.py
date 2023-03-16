from integralhk import spiacs_config, dump_lc, integral, realtime

from integralhk.exception import GeneratorException, handleall
from .integral import ijd2utc, x2ijd, time_interval, utc2utc_sec, getphase, ijd2scw

import tempfile
import subprocess
import os
import time
import re
import copy
import sys

import pandas as pd
import numpy as np

from integralclient import converttime

import astropy.table as table
import astropy.io.fits as fits
        
#advice=advise_time(utc1)+"; "+advise_time(utc2)


class BadTime(GeneratorException):
    def __init__(self,comment):
        self.comment=comment
    
    def __repr__(self):
        return f"Bad time: {self.comment}"


def translate_exceptions(f):
    def nf(*a,**b):
        try:
            return f(*a,**b)
        except integral.BadTimeFormat as e:
            raise GeneratorException("bad time format: "+repr(e))
    return nf


def validate_argnum(num,excc,arg):
    def dec(f):
        def nf(*a,**b):
            if len(a) != num:
                message = f"wrong number of arguments ({len(a)}), expected {num}. Arguments: {a}"
                exc=excc(arg)
                exc.message+="; " + message
                raise exc
            return f(*a,**b)
        return nf
    return dec

    
@validate_argnum(3,GeneratorException,"Generic LC needs three arguments")
@integral.with_both_rbp
@translate_exceptions
def getgenlc(*a,**b):
    target,timestr,rangestr=a

    validate_time(timestr)

    rbp=b['rbp']

    print(("getgenlc using "+rbp+" from target ",target))

    if target.startswith('SPTI'):
        raise GeneratorException("SPTI is private")
    

    timestr=timestr.strip()
    rangestr=rangestr.strip()

    ranges=time_interval(rangestr)
    ijd0=x2ijd(timestr,rbp=rbp)
            
    if ranges>400000.:
        raise GeneratorException("due to limits on the system load the requests to this service are limited to +-5000 span; to acquire very large spans of the data, please contact me directly (savchenk@apc.in2p3.fr)")

    utc0=ijd2utc(ijd0,rbp=rbp)
    utc1=ijd2utc(ijd0-ranges/24./3600,rbp=rbp)
    utc2=ijd2utc(ijd0+ranges/24./3600,rbp=rbp)
    

    print(("requested LC around",timestr,"range",rangestr))
    print(("interpeted as",ijd0,utc0,"range +-",ranges,utc1," - ",utc2))

    try:
        result,output=dump_lc.dump_lc(utc1,utc2,rbp=rbp,target=target)
        if 'output_utc' in b and b['output_utc']:
            return result,output,utc0,utc1,ranges
        else:
            return result,output  # may be note which rbp is used 
    except dump_lc.DumpLCException as e:
        print(("dump_lc exception",repr(e)))
        raise GeneratorException("dump lc exceptions:"+repr(e),times=[utc1,utc2])


@validate_argnum(2,GeneratorException,"IPN LC needs two arguments")
@translate_exceptions
def getipn(*a):
    timestr,rangestr=a

    result,output,utc0,utc1,ranges=getgenlc("ACS",timestr,rangestr,output_utc=True)

    date,refsec=utc2utc_sec(utc0)
    date1,refsec1=utc2utc_sec(utc1)
    dref=ranges
    print(("reference seconds:",refsec))
    print(("start (input reference) seconds:",refsec1))
    print(("range in seconds:",ranges))
    sanity=(lambda x:x-int(x))((refsec-refsec1-dref))
    print(("discrepancy of",sanity*1000,"ms"))
    if sanity>1e-4:
        print("input range inconsistend with the shift in the input! (leaps?..)")
        raise  Exception("input range inconsistend with the shift in the input! (leaps?..)")

    try:
        lc=[list(map(float,l.split())) for l in result.split("\n") if l!="" and l[0]!="#"]
        lc=["%10.3lf %10.5lf"%((T-refsec1-dref-0.025),c) for i,t,c,T in lc]
        if lc==[]:
            raise GeneratorException("empty lc!")
    except Exception as e:
        print(e)
        raise

    lcstr="\n".join(lc)

    bkg=0
    header="'INTEGRAL  ' '%s' %10.5lf 100.000  10000.000\n%10.5lf 0.05000000\n"%(date,refsec,bkg)

    return header+lcstr+"\n",output


@validate_argnum(1,GeneratorException,"EPHS needs one argument")
@integral.with_both_rbp
@translate_exceptions
def getephs(*a,**b):
    timestr,=a
    rbp=b['rbp']

    ijd=x2ijd(timestr,rbp=rbp)
    utc=ijd2utc(ijd,rbp=rbp)

    try:
        result,output=dump_lc.dump_lc(utc,utc,mode=1,rbp=rbp)
        return result,output
    except dump_lc.DumpLCException as e:
        print(("dump_lc exception:",e))
        raise GeneratorException("dump lc exceptions:"+str(e))

@validate_argnum(1,GeneratorException,"ATT needs one argument")
@integral.with_both_rbp
def getatt(*a,**b):
    timestr,=a
    rbp=b['rbp']

    ijd=x2ijd(timestr,rbp=rbp)
    utc=ijd2utc(ijd,rbp=rbp)

    try:
        result,output=dump_lc.dump_lc(utc,utc,mode=2,rbp=rbp)
        return result,output
    except dump_lc.DumpLCException as e:
        print(("dump_lc exception:",e))
        raise GeneratorException("dump lc exceptions:"+str(e))
    except Exception as e:
        print(("unhandled exception in att?",e))
        raise

@validate_argnum(1,GeneratorException,"SCW needs one argument")
@integral.with_both_rbp
def getscw(*a,**b):
    timestr,=a
    rbp=b['rbp']

    try:
        ijd=x2ijd(timestr,rbp=rbp)
        scw=ijd2scw(ijd,rbp=rbp)
    except subprocess.CalledProcessError as e:
        print(("converttime exception:",e))
        raise GeneratorException("converttime exception:"+str(e))

    return scw,"none"


@validate_argnum(2, GeneratorException,"realtime needs twos argument, time and window size")
def getrealtime(*a,**b):
    timestr, window_s = a
    
    try:
        ijd = x2ijd(timestr, rbp=spiacs_config.isdc_env['isdc_nrt'])
    except subprocess.CalledProcessError as e:
        print(("converttime exception:",e))
        raise GeneratorException("converttime exception:"+str(e))
    
    result, output = realtime.get_realtime_data(ijd, window_s)

    return result, "none"



def validate_time(timestr):
    print(("validate time:",timestr))
    ijd=x2ijd(timestr)

    ijdfirst=x2ijd(time.strftime("2002-11-01T00:00:00"))
    if ijd<ijdfirst: raise BadTime(timestr+" is before the mission start!")

    ijdnow=x2ijd(time.strftime("%Y-%m-%dT%H:%M:%S"))
    if ijd>ijdnow: raise BadTime(timestr+" is in the future!")
    
    phase=getphase(ijd)
    if phase<0.1 or phase>0.9: return timestr+" dangerous orbit phase:"+str(phase)
    
    if ijd>ijdnow-1.: return timestr+" hm, possibly not yet in the near-realtime data (wait a bit)"

    return str(timestr)+" seems to be valid"


############################################################

def generate(*req):
    return get_generator_by_name(req[0])(*req[1:])

def get_generator_by_name(name): 
    print(("generator by name:",name))
    
    if name=="tmlc":
        return tmlc

    if name=="ipnlc":
        return getipn
    
    if name=="ephs":
        return getephs
    
    if name=="att":
        return getatt
    
    if name=="genlc":
        return getgenlc
    
    if name=="scw":
        return getscw

    raise GeneratorException("unknown generator: "+name)


class NoData(Exception):
    pass

def open_one_of(options):
    f = None

    tried=[]

    for fn in options:
        print("trying", fn)

        try:
            f = fits.open(fn)
            print("... managed!")
        except Exception as e:
            print("... did not manage:", repr(e))
            tried.append(dict(fn=fn))

    if f is None:
        raise NoData("tried: "+repr(tried))

    return f

def get_timerange(t1, t2, strict=True, ra_dec=None, only_columns=None, source="cons"):
    if only_columns is not None:
        only_columns += ["TIME", "DAYBEG", "DAYEND", "XYZPOS", "DURATION"]

    t1_d = converttime("ANY", t1, "ANY")
    t2_d = converttime("ANY", t2, "ANY")

    t1_ijd = float(t1_d['IJD'])
    t2_ijd = float(t2_d['IJD'])

    if t2_ijd-t1_ijd>3.:
        return make_response("requested %.5lg days, allowed maximum 3."%(t2_ijd-t1_ijd)), 400

    if source == "cons":
        rbp = os.environ.get("REP_BASE_PROD_ARC", "/isdc/arc/rev_3")
        print("REP_BASE_PROD:", rbp)
    else:
        rbp = os.environ.get("REP_BASE_PROD_NRT", "/isdc/pvphase/ops/nrt")
        print("REP_BASE_PROD:", rbp)

    att_dfs = []
    orb_dfs = []

    for revnum in range(int(t1_d['REVNUM']), int(t2_d['REVNUM'])+1):
        print("revnum")

        
        df =  pd.DataFrame()

        try:
            a = table.Table(open_one_of([
                        rbp + "/aux/adp/%.4i.001/attitude_historic.fits.gz"%revnum,
                    ])[1].data)
        except:
            a = table.Table(open_one_of([
                        rbp + "/aux/adp/%.4i.000/attitude_snapshot.fits"%revnum,
                    ])[1].data)

        for col in a.columns:
            if only_columns is None or col in only_columns:
                print(col, a[col].dtype, a[col].shape)
            
                if 'U' in str(a[col].dtype):
                    a[col] = a[col].astype(str)

                df[col] = np.array(a[col]).byteswap().newbyteorder()

        df['DURATION_DAYS'] = df['DURATION'] / 24. / 3600.

        att_dfs.append(df)
        
        try:
            o = table.Table(open_one_of([
                        rbp + "/aux/adp/%.4i.001/orbit_historic.fits.gz"%revnum,
                    ])[1].data)
        except:
            o = table.Table(open_one_of([
                        rbp + "/aux/adp/%.4i.000/orbit_predicted.fits"%revnum,
                    ])[1].data)


        o_df = pd.DataFrame()

        print(o)

        for col in o.columns:
            if only_columns is None or col in only_columns:
                print(col, o[col].dtype, o[col].shape)

                if len(o[col].shape) == 1:
                    o_df[col] = np.array(o[col]).byteswap().newbyteorder()
                elif col == 'XYZPOS':
                    o_df['XPOS'] = np.array(o[col][:,0]).byteswap().newbyteorder()
                    o_df['YPOS'] = np.array(o[col][:,1]).byteswap().newbyteorder()
                    o_df['ZPOS'] = np.array(o[col][:,2]).byteswap().newbyteorder()

        o_df["TIME"] = o_df["DAYBEG"]
        o_df["DURATION_DAYS"] = o_df["DAYEND"] - o_df["DAYBEG"]

        print(o_df)

        orb_dfs.append(o_df)


    att_df = pd.concat(att_dfs)
    orb_df = pd.concat(orb_dfs)


    if strict:
        def pick(l, df):
            t = df["TIME"]
            dt = df["DURATION_DAYS"] 

            m = t + dt >= t1_ijd
            m &= t - dt <= t2_ijd
            df = df[m]

            print(l+" selection mask", sum(m),"/",len(m), "total range", np.array(t)[0], np.array(t)[-1], "requested", t1_ijd, t2_ijd, "sum time fraction:", sum(dt)/(np.array(t)[-1]-np.array(t)[0]))
            
            return df

        att_df = pick("attitude", att_df)
        orb_df = pick("orbit", orb_df)

    return dict(
                attitude=att_df.to_dict('list'),
                orbit=orb_df.to_dict('list'),
            )

