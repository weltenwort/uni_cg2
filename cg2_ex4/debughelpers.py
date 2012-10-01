import logging
from traceback import format_exc

def log_exceptions(func):
    def _handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            log = logging.getLogger('func.func_name EXCEPTIONS')
            log.error(format_exc())
            raise
    return _handler

def dump_args(func):
    "This decorator dumps out the arguments passed to a function before calling it"
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    def echo_func(*args,**kwargs):
        print fname, ":", ', '.join(
            '%s=%r' % entry
            for entry in zip(argnames,args) + kwargs.items())
        return func(*args, **kwargs)
    return echo_func

