import functools
from raven import Client
from groundhogday import GroundhogDayClass

class SentryNotifier(object):
    
    def __init__(self, **kwargs):
        self.environment = kwargs.get('environment', 'production')
        self.sentry_client = Client(**kwargs)
        
    def __call__(self, e):
        if not self.environment == 'test':
            self.sentry_client.get_ident(self.sentry_client.captureException())
        else:
            print 'Would send [%s] to sentry.' % e

def RetryWithSentry(*args, **kwargs):
    def wrap(f):
        functools.wraps(f)
        kwargs['notification_callback'] = SentryNotifier(**kwargs)
        return GroundhogDayClass(f, **kwargs)()
    return wrap