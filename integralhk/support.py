from integralhk.exception import GeneratorException

import sys
import traceback

def view_traceback():
    ex_type, ex, tb = sys.exc_info()
    traceback.print_tb(tb)
    del tb

def try_all(key):
    def decr(f):
        def nf(*a,**b):
            if key not in b:
                raise Exception("can not try all:"+str(key)+"not found in args")

            if not isinstance(b[key],list):
                print("can not try all:",key,"is not list",b[key])
                print("returning normal call")
                return f(*a,**b)
    
            print("will try %s as %s"%(key,str(b[key])))

            exceptions={}
            for c in b[key]:
                try:
                    print("trying with %s as %s"%(key,str(c)))
                    r=f(*a,**dict(list(b.items())+[[key,c]]))
                    print("succeded with %s as %s"%(key,str(c))) #,"got",r
                    return r
                except Exception as re:
                    #view_traceback()

                #except GeneratorException as e:
                    e = GeneratorException(re)

                    print("failed with %s as %s"%(key,str(c)))
                    print("exception:",e)
                    e.message="%s as %s: "%(key,str(c))+e.message
                    exceptions[c]=e

            print("failed all over!")
            
            print("exceptions:",list(exceptions.items()))
                
            for k1 in list(exceptions.keys()):
                for k2 in list(exceptions.keys()):
                    if k1==k2: continue
                    if exceptions[k1] is None: continue
                    if exceptions[k2] is None: continue
                    try:
                        print("merge? exceptions:",exceptions[k1],"and",exceptions[k2])
                        exceptions[k1].merge(exceptions[k2])
                        exceptions[k2]=None
                        print("yes!",exceptions[k1])
                    except Exception as e:
                        print("no...",e)
                        continue
            exceptions_not_none=dict([(k,v) for k,v in list(exceptions.items()) if v is not None])
            if len(list(exceptions_not_none.keys()))==1:
                e=list(exceptions_not_none.values())[0]
                print("merged exception:",e)
                raise e

            print("multiple exceptions:",exceptions)

            raise Exception("failed trial: "+repr(exceptions))

        return nf
    return decr

