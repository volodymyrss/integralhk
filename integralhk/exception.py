def handleall(comment):
    def dec(f):
        def nf(*a,**aa):
            try:
                return f(*a,**aa)
            except Exception as e:
                return comment+" : "+str("exception:"+str(e))
        return nf
    return dec


@handleall("can not comment on time!")
def comment_time(timestr):
    try:
        return validate_time(timestr)
    except BadTime as e:
        return repr(e)


class GeneratorException(Exception):
    def __init__(self,arg,times=None):
        self.message=str(arg)
        self.times=times

    def merge(self,e):
        if isinstance(e,self.__class__):
            self.message+="\n"+e.message

    def __repr__(self):
        m=self.message
        if hasattr(self,'times') and self.times is not None:
            for time in self.times:
                m+="\n"+comment_time(time)
        return "GeneratorException('%s')"%m
    
    def __str__(self):
        return repr(self)

