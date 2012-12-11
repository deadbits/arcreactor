#!/usr/bin/env python
#
# osint collection for AlienVault OTX reputation db
# stand-alone version from ArcReactor
#
# ohdae [ams]
# http://github.com/ohdae/ArcReactor/
#

import requests
import re, sys
import socket

# define some stuff
config = {
    # alienvault's reputation db to use. i find snort format easier to parse
    'otx': 'http://reputation.alienvault.com/reputation.snort',
    # syslog host
    'host': '127.0.0.1',
    # syslog port
    'port': '512'
}

def send_syslog(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # %d in the syslog msg is the syslog level + facility * 8
    # 29 is the default for notice + daemon * 8 or 5 + 3 * 8
    # data = '<%d>%s' % (level + facility*8, message)
    # change this if you feel the need
    data = '<%d>%s' % (29, msg)
    sock.sendto(data, (config['host'], int(config['port'])))
    sock.close()

def gather_data():
    # why anyone would use urllib when we have the requests lib, idk.
    data = requests.get(config['otx']).content
    try:
        print("[~] attempting to parse reputation data...")
        for line in data.split("\n"):
            # we really dont need that format checking function.
            # lets just look for comments and blank lines first then parse
            if not line.startswith("#") and line != "":
                try:
                    # snort format is: ip-address # message
                    d = line.split("#")
                    addr, info = d[0], d[1]
                    print("[~] sending syslog event for %s - %s" % (info, addr))
                    cef = 'CEF:O|OSINT|ArcReactor|1.0|100|%s|1|src=%s msg=%s' % (info, addr, config['otx'])
                    send_syslog(cef)
                except IndexError:
                    continue
    except:
        print("[!] error retrieving otx database")
        sys.exit(1)


print("\n\n")
print("\t open-source data gathering ")
print("\t   source >> alienvault.com   ")
print("\t    author: ohdae [ams] ")
print("\n\thttp://github.com/ohdae/arcreactor")
print("\n\n")

print("[~] starting collecting of OTX reputation database...")
# the alienvault otx db is updated every 60 minutes
# if you want a constantly updated activelist in esm,
# either run this script as a cronjob every hour or
# change this to add a simple time.sleep(3600)
# and repeat the gather_data() function
gather_data()


