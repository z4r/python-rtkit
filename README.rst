====================
python-rtkit
====================
`Best Practical RT`_ (Request Tracker) data access python module for REST interface.


Installation
================

Examples
================

Rest Api Summary
================
More detailed version: `Request Tracker Wiki`_

::

 [01] ticket/new                                                         | W
 [02] ticket/<ticket-id>                                                 | RW
 [03] ticket/<ticket-id>/comment                                         | W
 [04] ticket/<ticket-id>/links                                           | RW
 [05] ticket/<ticket-id>/attachments                                     | R
 [06] ticket/<ticket-id>/attachments/<attachment-id>                     | R
 [07] ticket/<ticket-id>/attachments/<attachment-id>/content             | R
 [08] ticket/<ticket-id>/history                                         | R
 [09] ticket/<ticket-id>/history?format=l                                | R
 [10] ticket/<ticket-id>/history/id/<history-id>                         | R
 [11] user/<user-id>                                                     | R
 [12] user/<user-Name>                                                   | R
 [13] queue/<queue-id>                                                   | R
 [14] queue/<queue-Name>                                                 | R
 [15] search/ticket?query=<query>&orderby=<sort-order>&format=<format>   | R

References
================
* `Best Practical RT`_
* `Request Tracker Wiki`_
* restkit_

.. _Best Practical RT: http://bestpractical.com/rt/
.. _Request Tracker Wiki: http://requesttracker.wikia.com/wiki/REST
.. _restkit: http://restkit.org/
