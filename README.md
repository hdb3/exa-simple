# exa-simple
trivial exaBGP applications

## exa-relay
Copy anouncements and withdrawals between two souce and sink BGP sessions.
Do simple substitution on the neighbour address to redirect messages between the peers.

## implementation notes
The script use JSON format input and generates a single packed (text) output for each JSON update object input.
The prefix packing is enabled by setting a  neighbor configuration parameter ‘group-updates true’, and using the alternate input format: 'attributes ...... nlri \[ <prefix> , <prefix>, ... ].  See source files for details.

## execution infrastructure requirement
The exaBGP runs as a passive BGP listener, waiting for two (active) peers to connect. The given 'relay.conf' configuration must match exactly the local and remote IP and AS numbers in the python script 'relay.py', in order for the switching between connected peers to operate correctly.  In the current example exa runs on local addresses 7.0.0.1 and 7.0.0.5 and expects peers to connect from 7.0.0.2 and 7.0.0.6 respectively.  All are in the same AS (65000).

## usage notes
run as:
exabag/sbin/exabgp relay.conf
exabgp.env should be in exabgp/etc/exabgp/.  The --env argument doesn't seem to work.
The script reports the number of updates and prefixes at intervals (100th update) and also when it receives End Of RIB.
In this configuration the daemon needs to listen on port 179, which requires either root privilege or something like 'sysctl net.ipv4.ip_unprivileged_port_start=179'.

## testing observations
To load and re-advertise a full internet route table  (130k paths, 800k prefixes) takes around 150 seconds.
