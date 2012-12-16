#!/usr/bin/env python
#
# osint collection for AlienVault OTX reputation db
# stand-alone version from ArcReactor
#
# ohdae [ams]
# http://github.com/ohdae/ArcReactor/
#

import requests
import reactor

count = 0

def gather_data():
    try:
        data = requests.get('http://reputation.alienvault.com/reputation.snort').content
        reactor.status('info', 'OTX', 'attempting to parse reputation data')
        for line in data.split('\n'):
            if not line.startswith('#') or not len(line) == 0:
                try:
                    d = line.split('#')
                    addr, info = d[0], d[1]
                    cef = 'CEF:0|OSINT|ArcReactor|1.0|100|%s|1|src=%s msg=%s' % (info, addr, 'http://reputation.alienvault.com/reputation.snort')
                    reactor.status('info', 'OTX', 'sending CEF syslog for %s - %s' % (info, addr))
                    reactor.send_syslog(cef)
                    count += 1
                except IndexError:
                    continue
        reactor.status('info', 'OTX', 'sent %d total events' % count)
        return True
    except:
        reactor.status('info', 'OTX', 'failed to retrieve OTX database')
        return False









