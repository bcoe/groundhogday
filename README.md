GroundhogDay
============

GroundhogDay helps you build resilient code in front of less than resilient services. It does so by exposing convenient retry decorators with callbacks for handling error conditions.

Examples
--------

Here's some examples of how you might use GroundhogDay:

```python
from groundhogday import GroundhogDay

class MyClass(object):
	@GroundhogDay
	def my_function(self):
		print 'my message'
		raise Exception('my exception')

MyClass().my_function()
```

If an exception is raised, the default decorator will retry the method _my_function_ four times, with an initial _backoff_ of 1.7 seconds that grows exponentially.

```python
import groundhogday
from groundhogday import GroundhogDay

class MyClass(object):
	@GroundhogDay(backoff=groundhogday.LINEAR, maximum_retry_callback='maximum_retries_reached')
	def my_function(self):
		print 'my message'
		raise Exception('my exception')
	
	def maximum_retries_reached(self, last_error):
		print str(last_error)

MyClass().my_function()
```

This example uses a linear _backoff_ rather than an exponential _backoff_. It will execute the _maximum\_retries\_reached_ method after the fourth exception.

Usage
-----

The Groundhog Day decorator can be configured with the following parameters.

* _maximum_retries_: how many retries before raising an exception.
* _sleep\_time_: how long should Groundhog Day sleep before invoking the method again.
* _backoff_: the back off type, either LINEAR or EXPONENTIAL (defaults to EXPONENTIAL).
* _notification\_threshold_: an optional threshold for configuring a one time notification, prior to retries actually terminating.
* _notification\_callback_: the name of a callback to execute when the notification threshold is reached.
* _exception\_callback_: the name of a callback to execute after each exception occurs.
* _maximum\_retry\_callback_: the name of a method to execute after a maximum number of retries is hit.

Airbrake Decorator
------------------

Groundhog Day provides a decorator that integrates with [Airbrake](http://attachmentsme.airbrake.io/)

```python
class MyClass(object):
	@RetryWithAirbrake(
		name='Python-Crawling-Stack',
		version='1.0.0',
		url='http://attachments.me',
		environment_name='production',
		api_key='[AIRBRAKE-API-KEY]'
	)
	def function_that_sends_error_to_airbrake(self):
		raise Exception('This exception will be sent to Airbrake')
```

* You can also provide any of the configuration options available in the GroundhogDay decorator.
* Rather than providing all the API information in the decorator, you can export the _PYTOAD\_CONFIG\_DIRECTORY_ environment variable.

Copyright
---------

Copyright (c) 2011 Attachments.me. See LICENSE.txt for further details.