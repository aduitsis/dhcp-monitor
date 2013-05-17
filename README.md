# DHCP Usage monitor for Cisco devices

###OVERVIEW

This is a very simple script to monitor DHCP pool usage on your cisco device. Its exit codes follow the correct convention in order for it to be used as a nagios plugin, if this is desired. 

To use this script:

* There must be access to the output of the 'show ip dhcp pools' command. Since I haven't been able to get this piece of info using SNMP, I was forced to use the clogin command from the excellent rancid tool. The output must be saved in a file ("config file"). If the config file becomes older than a configurable period the script can happily execute the clogin command for you and save the config file. The config file is used to ascertain the size and name of each pool, i.e. the configuration of the DHCP pools.
* The dhcp bindings file ("addresses file") must also be present. Your Cisco router can automatically upload this file to your host via tftp in regular intervals. This file is used to measure the usage of each pool. 

###USAGE 

To actually use the script, simply execure

`bindings_parser.py -r <your router hostname> -b <your dhcp bindings file> `

* The file config.your-router-hostname.txt will be created or recreated if it doesn't exist or is too old respectively. At this point I've set the oldness thresshold to 2 days. Adjust as needed. You can also override the file name by using the -c option
* The DHCP bindings file can be specified via the -b option. It defaults to dhcp.bindings in the script directory. Change as necessary.
* The thresshold above which any pool's usage is considered critical can be defined via the -t option.
* The clogin command can be defined with the -l option.

###NOTES

This is actually the first python program I'm writing, so please bear. If you find it useful, so much the better. 

###AUTHOR

Athanasios Douitsis, 2013

aduitsis@cpan.org
