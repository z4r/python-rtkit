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

**Get**::

 ticket/<ticket-id>                                     | Gets the data for a single ticket
 ticket/<ticket-id>/links                               | Gets the ticket links
 ticket/<ticket-id>/attachments                         | Gets a list of all ticket attachments
 ticket/<ticket-id>/attachments/<attachment-id>         | Gets the attachment data and content
 ticket/<ticket-id>/attachments/<attachment-id>/content | Gets the attachment content
 ticket/<ticket-id>/history                             | Gets a list of all ticket history
 ticket/<ticket-id>/history?format=l                    | Gets a detailed list of all ticket history
 ticket/<ticket-id>/history/id/<history-id>             | Gets the history item data
 user/<user-id>                                         | Gets the data for a single user
 user/<user-Name>                                       | Gets the data for a single user
 queue/<queue-id>                                       | Gets the data for a single queue
 queue/<queue-Name>                                     | Gets the data for a single queue

**Search**::

 search/ticket?query=<query>&orderby=<sort-order>&format=<format>

References
================
* `Best Practical RT`_
* `Request Tracker Wiki`_
* restkit_

.. _Best Practical RT: http://bestpractical.com/rt/
.. _REST - Request Tracker Wiki: http://requesttracker.wikia.com/wiki/REST
.. _restkit: http://restkit.org/
