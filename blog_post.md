Adventures with IMAP: building for third party APIs
=========================

Attachments.me has created a ton of cool tech on top of Gmail's [XOAUTH IMAP API](http://googlecode.blogspot.com/2010/03/oauth-access-to-imapsmtp-in-gmail.html). I'm proud of this. Particularly because Google's IMAP is a difficult technology to build on top of:

* It's limited to 10 concurrent connections.
* Accounts are frequently throttled.
* Sessions can terminate unexpectedly.

Building resilient software, in the face of these restrictions, has been a challenge.

In this post, I want to share some of the techniques I've picked up for building resilient software dependent on third party APIs.

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

Here's an example of a unit test I built around throttled IMAP accounts:

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

This test was built only after an integration test was built around an account which had fallen into a throttled state.

3. Extra layers of abstraction help
-----------------------------------

Take a step back, think of it in terms of what you need from the API.

* in our case, we needed to perform an initial index of all the attachments in a user's email account.

4. Retry operations, but be smart about it
------------------------------------------

5. Airbrake is really helpful
----------------------------

[Ben Coe](http://twitter.com/#/benjamincoe)