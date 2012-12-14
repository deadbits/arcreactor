#!/usr/bin/env python
#
# part of the ArcReactor application
# http://github.com/ohdae/ArcReactor
#
# 'Known Bad' collection module
# this module reads a list of public
# sources from the sources.cfg file
# and then scrapes those websites for
# IP addresses and domain names. these
# collected hosts are sent via syslog
# to the ArcSight ESM system in our config
#

import requests
import os, re
import reactor

results = {}
sources = []

ip_regex = re.compile(r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
dom_regex = re.compile(r'([\d\w.][-\d\w.]{0,253}[\d\w.]+\.)+(AC|AD|AE|AERO|AF|AG|AI|AL|AM|AN|AO|AQ|AR|ARPA|AS|ASIA|AT|AU|AW|AX|AZ|BA|BB|BD|BE|BF|BG|BH|BI|BIZ|BJ|BM|BN|BO|BR|BS|BT|BV|BW|BY|BZ|CA|CAT|CC|CD|CF|CG|CH|CI|CK|CL|CM|CN|COM|COOP|CR|CU|CV|CX|CY|CZ|DE|DJ|DK|DM|DO|DZ|EC|EDU|EE|EG|ER|ES|ET|EU|FI|FJ|FK|FM|FO|FR|GA|GB|GD|GE|GF|GG|GH|GI|GL|GM|GN|GOV|GP|GQ|GR|GS|GT|GU|GW|GY|HK|HM|HN|HR|HT|HU|ID|IE|IL|IM|INFO|INT|IO|IQ|IR|IS|IT|JE|JM|JO|JOBS|JP|KE|KG|KH|KI|KM|KN|KP|KR|KW|KY|KZ|LA|LB|LC|LI|LK|LR|LS|LT|LU|LV|LY|MA|MC|MD|ME|MG|MH|MIL|MK|ML|MM|MN|MO|MOBI|MP|MQ|MR|MS|MT|MU|MUSEUM|MV|MW|MX|MY|MZ|NA|NAME|NC|NET|NF|NG|NI|NL|NO|NP|NR|NU|NZ|OM|ORG|PA|PE|PF|PG|PH|PK|PL|PM|PN|PR|PRO|PS|PT|PW|PY|QA|RE|RO|RS|RU|RW|SA|SB|SC|SD|SE|SG|SH|SI|SJ|SK|SL|SM|SN|SO|SR|ST|SU|SV|SY|SZ|TC|TD|TEL|TF|TG|TH|TJ|TK|TL|TM|TN|TO|TP|TR|TRAVEL|TT|TV|TW|TZ|UA|UG|UK|US|UY|UZ|VA|VC|VE|VG|VI|VN|VU|WF|WS|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|YE|YT|YU|ZA|ZM|ZW)', re.IGNORECASE)
comment_regex = re.compile ("#.*?\n")
comment2_regex = re.compile ("//.*?\n")

def load_sources():
    sources = reactor.load_sources(reactor.PATH_CONF+"/sources.conf")
    if len(sources) > 0:
        reactor.status("info", "known bad", "%d sources added to queue" % len(sources))
        return True
    return False

def gather_data(source):
    try:
        reactor.status("info", "known bad", "retrieving hosts from %s" % source)
        raw = requests.get(source).content
        data = re.findall(ip_regex, raw)
        if data == "":
            data = re.findall(dom_regex, raw)
        results[data] = source
    except:
        reactor.status("error", "known bad", "failed to retrieve hosts from %s" % source)

def send_events():
    if len(results) > 0:
        for bad_host, src_info in results.iteritems():
            cef = 'CEF:0|OSINT|ArcReactor|1.0|100|Known Malicious Host|1|src=%s msg=%s' % (bad_host, src_info)
            reactor.status("info", "known bad", "sending CEF syslog for %s" % bad_host)
            reactor.send_syslog(cef)
    else:
        reactor.status("error", "known bad", "")


def main():
    if read_config() and len(sources) > 0:
        for src in sources:
            gather_data(src, ip_regex)
            gather_data(src, dom_regex)
        if len(results) > 0:
            for bad_host, info_src in results.iteritems():
                cef = 'CEF:0|OSINT|ArcReactor|1.0|100|Known Malicious Host|1|src=%s msg=%s' % (bad_host, info_src)
                reactor.status("info", "Known Bad", "sending CEF syslog for %s" % bad_host)
            reactor.status("info", "Known Bad", "sent %d total events" % len(results))
        else:
            reactor.status("error", "Known Bad", "collected host list appears to be empty")
    else:
        reactor.status("error", "Known Bad", "collected source list appears to be empty")


