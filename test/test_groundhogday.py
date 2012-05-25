import sys, traceback
import time
import unittest
from pytoad import Connection
from groundhogday import GroundhogDay, RetryWithAirbrake, LINEAR

class MockPytoadConnection(Connection):
    
    exceptions = []
    
    def send_to_hoptoad(self, exception):
        self.exceptions.append( exception )

class AwesomeFakeClass():
    
    def __init__(self, testCase):
        self.last_exception = None
        self.executed_methods = {}
        self.iterations_before_notification = None
    
    @GroundhogDay(notification_threshold=2, sleep_time=0.5, maximum_retries=3, maximum_retry_callback='my_maximum_retry_callback', notification_callback='my_notification_callback', exception_callback='my_exception_callback')
    def function_that_raises_exception(self, add=-1):
        self.executed_methods['function_that_raises_exception'] = self.executed_methods.get('function_that_raises_exception', 0) + 1
        raise Exception('foobar exception')
    
    @GroundhogDay(backoff=LINEAR, sleep_time=0.3, maximum_retries=3)
    def linear_backoff_exception(self):
        raise Exception('my exception')

    # this is an integration test.
    #@RetryWithAirbrake
    #def function_that_sends_error_to_airbrake(self):
    #    raise Exception('an airbrake exception')
    
    @GroundhogDay
    def function_that_works(self):
        self.executed_methods['function_that_works'] = self.executed_methods.get('function_that_works', 0) + 1
    
    def my_maximum_retry_callback(self, e):
        self.last_exception = e
        self.executed_methods['my_maximum_retry_callback'] = self.executed_methods.get('my_maximum_retry_callback', 0) + 1
    
    def my_notification_callback(self, e):
        self.iterations_before_notification = self.executed_methods['function_that_raises_exception']
    
    def my_exception_callback(self, e):
        self.executed_methods['my_exception_callback'] = self.executed_methods.get('my_exception_callback', 0) + 1

class TestGroundhogDay(unittest.TestCase):

    def test_original_function_executed_with_no_args(self):
        global call_me
        call_me = False

        @GroundhogDay
        def f():
            global call_me
            call_me = True
        f()
        
        afc = AwesomeFakeClass(self)
        afc.function_that_works()
        
        self.assertEqual(call_me, True)
        self.assertEqual(afc.executed_methods['function_that_works'], 1)

    def test_original_function_executed_with_args(self):
        global value, value2
        value = None

        @GroundhogDay
        def f(a, v2=99):
            global value, value2
            value = a
            value2 = v2
        f(2)
        
        self.assertEqual(value, 2)
        self.assertEqual(value2, 99)

    def test_exeption_raised_after_maximum_retries(self):
        afc = AwesomeFakeClass(self)
        try:
            afc.function_that_raises_exception(add=1)
        except:
            pass
        self.assertEqual(3, afc.executed_methods['function_that_raises_exception'])
    
    def test_exponential_backoff_works(self):
        start = time.time()
        afc = AwesomeFakeClass(self)
        try:
            afc.function_that_raises_exception(add=1)
        except:
            pass
        self.assertTrue(time.time() - start >= 0.3)
        self.assertTrue(time.time() - start <= 0.5)
    
    def test_maximum_retry_callback_executed_with_appropriate_exception(self):
        afc = AwesomeFakeClass(self)
        try:
            afc.function_that_raises_exception(add=1)
        except:
            pass
        self.assertEqual('foobar exception', str(afc.last_exception))
        self.assertEqual(1, afc.executed_methods['my_maximum_retry_callback'])
        
    def test_notificadtion_callback_executed_after_appropriate_number_of_exceptions(self):
        afc = AwesomeFakeClass(self)
        try:
            afc.function_that_raises_exception(add=1)
        except:
            pass
        self.assertEqual(2, afc.iterations_before_notification)
    
    def test_linear_backoff(self):
        start = time.time()
        afc = AwesomeFakeClass(self)
        try:
            afc.linear_backoff_exception(add=1)
        except:
            pass
        self.assertTrue(time.time() - start >= 0.5)
        self.assertTrue(time.time() - start <= 0.7)
    
    #   An integration test while building the retry_with_airbrake decorator.
    #   def test_airbrake_retry_decorator(self):
    #   afc = AwesomeFakeClass(self)
    #    try:
    #        afc.function_that_sends_error_to_airbrake()
    #    except:
    #        pass
    
    def test_exception_callback(self):
        afc = AwesomeFakeClass(self)
        try:
            afc.function_that_raises_exception(add=1)
        except:
            pass
        self.assertEqual(3, afc.executed_methods['my_exception_callback'])
