#!/usr//bin/env python 

import pickle
import fileinput
import re
from socket import inet_aton
from struct import unpack
import pprint
import os
import argparse
import sys
import subprocess
import time

clogin = '/usr/local/libexec/rancid/clogin'
thresshold = 0.9
stale_file_thress = 3600*24
router = 'router'
addresses_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dhcp.bindings' )
config_file = None

parser = argparse.ArgumentParser(description='check DHCP pools based on Cisco dhcp bindings file and show ip dhcp pools output')
parser.add_argument('-c', '--config')
parser.add_argument('-b', '--bindings')
parser.add_argument('-t', '--thresshold')
parser.add_argument('-l', '--clogin')
parser.add_argument('-r', '--router')
args = parser.parse_args()

if args.router:
	router = args.router	

if args.config:
	config_file = args.config

if args.bindings:
	addresses_file = args.bindings

if args.thresshold:
	thresshold = float( args.thresshold )

if args.clogin:
	clogin = args.clogin	

if not config_file:
	config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.' + router + '.txt' )

print router


reread = False

if not os.path.exists( config_file ):
	print config_file + ' does not exist'
	reread = True
else: 
	mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime = os.stat(config_file)
	old = time.time() - mtime 
	if old > stale_file_thress:
		print config_file + ' is more than ' + str(stale_file_thress) + ' seconds old'
		reread = True

if reread:
	clogin = subprocess.Popen([ clogin , '-c' , 'show ip dhcp pool' , router ], stdout=subprocess.PIPE )
	clogin_out, clogin_err = clogin.communicate()
	f = open( config_file, 'w' ) 
	f.write( clogin_out )
	f.close()

interface = None

flag = False

bindings = {}

config_f = open( config_file , 'r')

for line in config_f.readlines():
	line = line.rstrip('\n')
	m = re.match('Pool\s+(\S+)',line) 
	if m is not None:
		interface = m.group(1)
		#print m.group(1)
		bindings[ interface ] = { 'leased':0, 'size':0, 'utilization':0.0 , 'sets' : [] }
	m = re.match('\s*(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s*-\s*(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s*/\s*(\d+)',line)
	if m is not None:
		start = unpack('>L', inet_aton(m.group(2)))[0] 
		stop = unpack('>L', inet_aton(m.group(3)))[0] 
		#print m.group(2) + ' ' + str(start) + ' ' + m.group(3) + ' ' + str(stop)
		bindings[ interface ]['sets'].append( {'start':start, 'stop':stop, 'leased':0 , 'size': int(m.group(5)) , 'alert': False } )
		

#file = open('conf.pickle','w')
#pickle.dump(bindings,file)
#file.close()


addresses = open(addresses_file,'r')
for line in addresses.readlines():
	m = re.match('(\d+\.\d+\.\d+\.\d+)',line)
	if m is not None:
		address = unpack('>L', inet_aton(m.group(1)))[0]
		for interface in bindings:
			for addr_set in bindings[interface]['sets']:
				if addr_set['start'] <= address and addr_set['stop'] >= address:
					#print m.group(1) + ' is part of ' + interface
					addr_set['leased']+=1;
					if float(addr_set['leased'])/addr_set['size'] > thresshold:
						addr_set['alert'] = True
						flag = True
					#	print 'WARNING, interface ' + interface + ' is running out of addresses'

for interface in bindings:
	for addr_set in bindings[interface]['sets']:
		bindings[interface]['leased'] += addr_set['leased']
		bindings[interface]['size'] += addr_set['size']
		bindings[interface]['utilization'] = 100.0 * bindings[interface]['leased'] / bindings[interface]['size'] 
		#print interface + ' ' + str(int(bindings[interface]['utilization'])) + '%'

print ' '.join( [  '[ ' + interface + ' ' + str(int(bindings[interface]['utilization'])) + '% ]'  for interface in bindings ] )
	
if flag:
	sys.exit(2)

sys.exit( 0 ) 
#pprint.pprint( bindings )
