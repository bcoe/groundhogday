Dealing With Sketchy APIs
=========================

[Attachments.me](http://attachments.me) has built a lot of cool tech on top of Gmail's [XOAUTH IMAP API](http://googlecode.blogspot.com/2010/03/oauth-access-to-imapsmtp-in-gmail.html). I'm proud of this. Having said that, Google's IMAP is a frustrating technology to build on top of. 

* Gmail is limited to 10 concurrent connections.
* IMAP connections can become throttled.
* Connections frequently close unexpectedly.

Building resilient software in this paradigm has been a difficult challenge. In this post, I'll share some of the strategies I've picked up along the way.

1. Unit testing is more important than ever
--------------------------------------------

2. Not all exceptions are exceptions
------------------------------------

3. Extra layers of abstraction help
-----------------------------------

4. Retry operations, but be smart about it
------------------------------------------

5. Airbrake is really helpful
----------------------------

[Ben Coe](http://twitter.com/#/benjamincoe)