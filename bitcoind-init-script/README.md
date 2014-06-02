# bitcoind init script

Init script for running official Bitcoin Core client daemon.

Runs the bitcoin client as a system daemon with DATADIR in /var/lib/bitcoind,
config file /etc/bitcoind/bitcoin.conf and pid file in /var/run/bitcoind/ and
under user `bitcoind` (configurable through /etc/defaults/bitcoind).

With a custom action `command` for sending commands to the daemon,
e.g. `service bitcoind command getinfo`

LSB standard init script format, tested on Debian Jessie.
