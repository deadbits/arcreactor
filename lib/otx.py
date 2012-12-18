#!/usr/bin/env python
#
# AlienVault OTX collection module
# part of ArcReactor
#
# http://github.com/ohdae/arcreactor/
#

import reactor

count = 0

def gather_data():
    try:
        data = reactor.http_request('http://reputation.alienvault.com/reputation.snort')
        if data is not None:
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
        reactor.status('warn', 'OTX', 'failed to retrieve OTX database')
        return False









