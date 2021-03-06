Adventures with IMAP: building for third party APIs
=========================

Attachments.me has created a ton of cool tech on top of Gmail's [XOAUTH IMAP API](http://googlecode.blogspot.com/2010/03/oauth-access-to-imapsmtp-in-gmail.html). I'm proud of this. Particularly because Google's IMAP is a difficult technology to build on top of:

* Concurrent connections are limited.
* Accounts are frequently throttled.
* Sessions can terminate unexpectedly.

Building resilient software, in the face of these restrictions, has been a challenge.

In this post, I want to share some of the techniques I've picked up for building software which depends heavily on third party APIs.

1. Unit testing is more important than ever
--------------------------------------------

Gracefully recovering from exceptions can significantly increase your application's cyclomatic complexity (spaghetti factor). This sucks, but might be a necessary evil.

It's important to get these multiple paths of execution under test. I've found that if [TDD](http://en.wikipedia.org/wiki/Test-driven_development) is used from the start, it makes this way easier.

Start with integration tests:

* log all the responses coming back from an external API.
* try your damnedest to cause a hypothesized exception to occur.
* create a mock version of the API that simulates this behavior.
* only now start working on a fix.

If you don't approach things methodically, you'll just make things worse -- trust me.

An example
----------
We needed to handle throttled IMAP accounts.

From an integration test, we determined that ```typ, data = self.connection.check()``` would return _THROTTLED_, when accounts were in a throttled state.

From here we went on to create a unit test around the behavior:

```python
def test_iterate_sets_a_throttle_backoff_timestamp(self):
    FakeGmailCrawler.THROTTLED = True
    self.connection.clerk_test.rules.insert({
        'user_uuid': 'aaabbb'
    }, safe=True)
    crawl_iterator = CrawlIterator(database='clerk_test', rule_tester=FakeRuleTester, crawler_map={'gmail_oauth': FakeGmailCrawler, 'g_apps_oauth': FakeGmailCrawler}, client_id=0, client_count=1)
    crawl_iterator.iterate()
    crawl_status_objects = self.connection.clerk_test.crawl_status.find({
        'user_uuid': 'aaabbb'
    })
    self.assertTrue(crawl_status_objects[0]['throttle_backoff_timestamp'] > 1330636773)
```

2. Extra layers of abstraction help
-----------------------------------

We've used Redis to build an abstraction layer on top of the IMAP crawling process. We take a transactional approach:

* when we start crawling an email account we populate a stack in Redis:

```python
def _track_with_redis(self):
	typ, ids = self.connection.uid('search', '(X-GM-RAW has:attachment)')
	for id in ids:
		self.redis.rpush(self.redis_key, id)
```

* as we iterate over the account we grab ids from redis:

```python
message_id = self.redis.rpop(self.redis_key)
```

* we have a monitoring layer that observes keys in Redis, and proactively ensures that crawls complete.

3. Retry operations
---------------------------------------

When a third-party API throws an exception, there are a lot of situations where trying again is your best course of action.

I built the library _groundhogday_ for simplifying this process:

* it allows you to retry a method a set number of times.
* sleeps a set period of time, rather than immediately performing the operation a second time.
* it exposes hooks to help with proactively recovering from exceptions.

Here's an example:

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
```

4. Airbrake is really helpful
----------------------------

Airbrake is a service that centrally aggregates the exceptions your projects throw. It handles notifying you by email, and provides a historical view of exceptions that have occurred.

* We've been much more proactive about fixing problems, since starting to use Airbrake -- getting hassled via email goes a long way.
* Airbrake's historical record of exceptions helps a ton when building mock responses for unit tests.

_groundhogday_ also has an Airbrake decorator, which we lean on heavily:

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

My experiences wrestling with IMAP were my motivation for building _groundhogday_, which I'm just starting to pull into some of our projects.

I hope you've found some of these tips, and the library itself, useful. Please don't hesitate to contact and/or flame me:

[Ben Coe](http://twitter.com/#/benjamincoe)