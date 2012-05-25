import time
import types
import inspect
import functools

LINEAR = 0
EXPONENTIAL = 1

class GroundhogDayClass(object):

    def __init__(self, f, **kwargs):
        self.f = f
        self.maximum_retries = kwargs.get('maximum_retries', 4)
        self.sleep_time = kwargs.get('sleep_time', 1.7)
        self.backoff = kwargs.get('backoff', 1)
        self.notification_threshold = kwargs.get('notification_threshold', 3)
        self.exception_callback_name = kwargs.get('exception_callback', None)
        self.notification_callback_name = kwargs.get('notification_callback', None)
        self.maximum_retry_callback_name = kwargs.get('maximum_retry_callback', None)
        
    def _sleep(self, retry_count):
        if self.backoff == LINEAR:
            time.sleep(self.sleep_time)
        else:
            backoff = self.sleep_time
            for i in range(0, retry_count):
                backoff *= backoff
            time.sleep(backoff)
            
    def __call__(self):
        def wrap(*args, **kwargs):
            last_exception = None
            
            for retry_count in range(0, self.maximum_retries):
                if retry_count:
                    self._sleep(retry_count)
                    
                try:
                    return self.f(*args, **kwargs)
                except Exception, e:
                    last_exception = e
                    exception_callback = self._get_wrapped_method(args[0], self.exception_callback_name)
                    if exception_callback:
                        exception_callback(last_exception)
                        
                    notification_callback = self._get_wrapped_method(args[0], self.notification_callback_name)
                    if notification_callback and retry_count == (self.notification_threshold - 1):
                        notification_callback(last_exception)
            
            if self.maximum_retry_callback_name:
                maximum_retry_callback = self._get_wrapped_method(args[0], self.maximum_retry_callback_name)
                if maximum_retry_callback:
                    maximum_retry_callback(last_exception)
            
            raise last_exception
        return wrap
    
    def _get_wrapped_method(self, wrapped_self, method_name):
        if callable(method_name): # Allow for callbacks to be callables rather than method names.
            return method_name
            
        members = {}
        for kv in inspect.getmembers(wrapped_self, inspect.ismethod):
            if kv[0] == method_name:
                return kv[1]
            
def GroundhogDay(*args, **kwargs):
    if len(args) and type(args[0]) == types.FunctionType: # We called without parenthesis.
        functools.wraps(args[0])
        return GroundhogDayClass(args[0])()
    else:
        def wrap(f):
            functools.wraps(f)
            return GroundhogDayClass(f, **kwargs)()
        return wrap