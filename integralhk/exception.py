
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

