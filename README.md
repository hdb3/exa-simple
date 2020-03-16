# exa-simple
trivial exaBGP applications

## exa-relay
Copy anouncements and withdrawals between two souce and sink BGP sessions.
Do simple substitution on the neighbour address to redirect messages between the peers.

## notes
run as:
exabag/sbin/exabgp relay.conf
exabgp.env should be in exabgp/etc/exabgp/.  The --env argument doesn't seem to work.
