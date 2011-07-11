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
Connection using Basic Authentication

::

 from restkit.filters import BasicAuth
 from rtkit import RTResource, set_logging, RTResourceError
 import logging
 
 set_logging('debug')
 logger = logging.getLogger('rtkit')
 auth = BasicAuth(<USER>, <PWD>)
 resource = RTResource('http://<HOST>/REST/1.0/',filters=[auth,])

References
================
* `Best Practical RT`_
* `Request Tracker Wiki`_
* restkit_

.. _Best Practical RT: http://bestpractical.com/rt/
.. _Request Tracker Wiki: http://requesttracker.wikia.com/wiki/REST
.. _restkit: http://restkit.org/
