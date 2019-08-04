# stellarium-control
Use Stellarium to send slew instructions to a telescope controller over tcp.  The target telescope system is the Acre Road 
21-cm telescope (colloquially the 'SRT' in memory of a deceased predecessor), controlled by Norman's QP code on an arduino. See
http://www.astro.gla.ac.uk/users/norman/distrib/qp/doc/index.html.

Currently just some test files to show proof of principle.

To do:
 - send serial messages to QP reflecting the slew command received from Stellarium
 - receive pointing data from QP and relay it back to Stellarium for the graticule
 - gui allowing tracking on/off and up/down/left/right nudges to check the pointing offsets
 - auto startup and shutdown with Stellarium
 - simple full control with remote stellarium: tracking always on.  If alt<0 then stow.
