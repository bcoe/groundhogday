import types
import inspect
import functools
from pytoad import Connection
from groundhogday import GroundhogDayClass

class AirbrakeNotifier(object):
    
    def __init__(self, **kwargs):
        self.environment = kwargs.get('environment', 'production')
        self.additional_information = kwargs['additional_information']
        self.pytoad_connection = Connection(**kwargs)
        
    def __call__(self, e):
        if not self.environment == 'test':
            self.pytoad_connection.send_to_hoptoad(e, self.additional_information)
        else:
            print 'Would send (%s %s) to airbrake' % (e, self.additional_information)

def _get_additional_information(f):
    try:
        sourcelines = inspect.getsourcelines(f)
        return "method=%s file=%s line=%s" % (f.__name__, inspect.getfile(f).split('/')[-1],sourcelines[1])
    except:
        return None

def RetryWithAirbrake(*args, **kwargs):
    if len(args) and type(args[0]) == types.FunctionType: # We called without parenthesis.
        functools.wraps(args[0])
        return GroundhogDayClass(args[0], notification_callback=AirbrakeNotifier(additional_information=_get_additional_information(args[0])))()
    else:
        def wrap(f):
            functools.wraps(f)
            kwargs['additional_information'] = _get_additional_information(f)
            kwargs['notification_callback'] = AirbrakeNotifier(**kwargs)
            return GroundhogDayClass(f, **kwargs)()
        return wrap