Dealing With Sketchy APIs
=========================

Attachments.me has built a lot of cool tech on top of Gmail's [XOAUTH IMAP API](http://googlecode.blogspot.com/2010/03/oauth-access-to-imapsmtp-in-gmail.html). I'm proud of this. Having said that, Google's IMAP is a frustrating technology to build on top of:

* It's limited to 10 concurrent connections.
* Connections can become throttled.
* Connections frequently close unexpectedly.

Building resilient software in this paradigm has been a difficult challenge.

I want to share some of the strategies I've picked up along the way:

1. Unit testing is more important than ever
--------------------------------------------

Gracefully recovering from exceptions can significantly increase your application's cyclomatic complexity (spaghetti factor). This sucks, but might be a necessary evil.

It's important to get the many paths under test. I've found that if [TDD](http://en.wikipedia.org/wiki/Test-driven_development) is used from the start, it makes this way easier.

It can be  helpful to start with an integration test:

* log all the responses coming back from the external API.
* try your damnedest to cause a hypothesized exception to occur.
* create a mock version of the API that simulates this behavior.
* only now start working on your slick fix to the problem.

If you don't approach things methodically, you'll just make things worse -- trust me.

3. Extra layers of abstraction help
-----------------------------------

Here's a common Catch-22: an external API isn't stable, your application can't afford not to be stable.


4. Retry operations, but be smart about it
------------------------------------------

5. Airbrake is really helpful
----------------------------

[Ben Coe](http://twitter.com/#/benjamincoe)