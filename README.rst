====================
python-rtkit
====================
`Best Practical RT`_ (Request Tracker) data access python module for REST interface.


Installation
================

Rest Api Summary
================
More detailed version: `Request Tracker Wiki`_

::

 [01][-W] Create ticket                     | ticket/new
 [02][RW] Read/Update ticket                | ticket/<ticket-id>
 [03][-W] Create ticket comment             | ticket/<ticket-id>/comment
 [04][RW] Read/Update ticket links          | ticket/<ticket-id>/links
 [05][R-] Read ticket attachments           | ticket/<ticket-id>/attachments
 [06][R-] Read ticket attachment            | ticket/<ticket-id>/attachments/<attachment-id>
 [07][R-] Read ticket attachment content    | ticket/<ticket-id>/attachments/<attachment-id>/content
 [08][R-] Read ticket history               | ticket/<ticket-id>/history
 [09][R-] Read detailed ticket history      | ticket/<ticket-id>/history?format=l
 [10][R-] Read ticket history item          | ticket/<ticket-id>/history/id/<history-id>
 [11][R-] Read user by id                   | user/<user-id>
 [12][R-] Read user by name                 | user/<user-Name>
 [13][R-] Read queue by id                  | queue/<queue-id>
 [14][R-] Read queue by name                | queue/<queue-Name>
 [15][R-] Search tickets                    | search/ticket?query=<query>&orderby=<sort-order>&format=<format>

Low Level Layer Examples
================
0) Connection using Basic Authentication

::

 from restkit.filters import BasicAuth
 from rtkit import RTResource, set_logging, RTResourceError
 import logging
 
 set_logging('debug')
 logger = logging.getLogger('rtkit')
 auth = BasicAuth(<USER>, <PWD>)
 resource = RTResource('http://<HOST>/REST/1.0/',filters=[auth,])

1) Create ticket

::

 try:
     message = '''My useless
 text on
 three lines.'''
     message = '\n'.join(' '+m for m in message.splitlines())
     content = {
         'Queue': 1,
         'Subject' : 'New Ticket',
         'Text' : message,
     }
     response = resource.post(
         path='ticket/new',
         payload=content,
     )
     logger.info(response.parsed)
 except RTResourceError as e:
     logger.error(e.response.status_int)
     logger.error(e.response.status)
     logger.error(e.response.parsed)

::

 #OK
 [2011-07-11 16:51:42][DEBUG] POST ticket/new
 [2011-07-11 16:51:42][DEBUG] {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain', 'User-Agent': 'pyRTkit/0.0.1'}
 [2011-07-11 16:51:42][DEBUG] u'content=Queue: 1\nText:  My useless\n text on\n three lines.\nSubject: New Ticket\n'
 [2011-07-11 16:51:42][INFO] HTTP_STATUS: 200 OK
 [2011-07-11 16:51:42][INFO] RESOURCE_STATUS: 200 Ok
 [2011-07-11 16:51:42][DEBUG] 'RT/3.8.10 200 Ok\n\n# Ticket 17 created.\n\n'
 [2011-07-11 16:51:42][INFO] [[('id', 'ticket/17')]]

::

 #WRONG OR MISSING QUEUE
 [2011-07-11 17:22:39][DEBUG] POST ticket/new
 [2011-07-11 17:22:39][DEBUG] {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain', 'User-Agent': 'pyRTkit/0.0.1'}
 [2011-07-11 17:22:39][DEBUG] u'content=Queue: \nText:  My useless\n text on\n three lines.\nSubject: New Ticket\n'
 [2011-07-11 17:22:39][INFO] HTTP_STATUS: 200 OK
 [2011-07-11 17:22:39][DEBUG] 'RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# Could not create ticket. Queue not set\n\n'
 [2011-07-11 17:22:39][INFO] RESOURCE_STATUS: 400 Could not create ticket
 [2011-07-11 17:22:39][ERROR] 400
 [2011-07-11 17:22:39][ERROR] 400 Could not create ticket
 [2011-07-11 17:22:39][ERROR] []

References
================
* `Best Practical RT`_
* `Request Tracker Wiki`_
* restkit_

.. _Best Practical RT: http://bestpractical.com/rt/
.. _Request Tracker Wiki: http://requesttracker.wikia.com/wiki/REST
.. _restkit: http://restkit.org/
