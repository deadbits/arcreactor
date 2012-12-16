#!/usr/bin/env python
#
# part of the ArcReactor application
# http://github.com/ohdae/ArcReactor
#
# Module & task dispatch
# this module receives input from the interactive
# console. we take in requests to execute collection
# modules, verify the settings, execute the appropriate
# functions and return the output to be sent via syslog
# this is where the magic happens.
#

import os, sys
import commands
import reactor
#import exploits
import otx
import pastebin
#import reddit
import re, string

# keep track of which module is doing what
job_stats = {}
# keep track of total events sent per module
events = {}

class Command:
    def __init__(self):
        self.cmd = ''

class Module:
    def __init__(self):
        # this entire class is for interacting with the collection modules
        self.tasks = {
            'running': 0,
            'queued': 0,
            }

    def run_knownbad(self):
        # this launches the knownbad.py module.
        # first we load the list of external sources and then parse out the
        # ip addresses and domains from the sources. all the events are sent
        # via syslog with the CEF msg 'Known Malicious Host'
        # TODO: - separate malicious address and malicious domain.
        job_stats['knownbad'] = 'loading sources'
        if knownbad.load_sources():
            for src in knownbad.sources:
                job_stats['knownbad'] = 'gathering data from sources'
                host, source = knownbad.gather_data(src)
                if not host == "":
                    job_stats['knownbad'] = 'sending syslog event'
                    cef = 'CEF:0|OSINT|ArcReactor|1.0|100|Known Malicious Host|1|src=%s msg=%s' % (self.host, self.source)
                    reactor.send_syslog(cef)
                    events['knownbad'] += 1
            job_stats['knownbad'] = 'finished successfully'
        job_stats['knownbad'] = 'finished with errors'

    def run_pastebin(self):
        # all of the collected posts, raw data, found keywords, etc
        # is handled entirely within the pastebin module itself - not this function.
        # pastebin.py takes care of all the output, variable definitions and searching
        # on it's own. we are simply running the functions and, assuming nothing fails
        # along the way, we take the final pastebin.found hash and send it via syslog
        # to our SIEM
        job_stats['pastebin'] = 'loading keywords'
        reactor.status('info', 'pastebin', 'launching pastebin module')
        if pastebin.load_words():
            job_stats['pastebin'] = 'collecting post archive'
            pastebin.gather_archive()
            # this 'while' is needed because the 'requests' lib stops half-way through
            # the post queue. we collect 250 posts at a time, but during testing the
            # search would stop everytime at 125, then again at 63 (~125/2) and so on.
            # i am really not sure why this happens. during an strace of this function
            # everything looked completely normal. as a small fix for this, we set a
            # loop that forces the gather_content/search_raw until the queue is all the
            # way down to zero. 
            if len(pastebin.queue) > 0:
                for post in pastebin.queue:
                    job_stats['pastebin'] = 'collecting raw posts'
                    pastebin.gather_content(post)
                    job_stats['pastebin'] = 'searching post %s' % post
                    # the pastebin.search_raw command is called automatically
                    # from the pastebin.gather_content function.
            job_stats['pastebin'] = '%d matches found' % (len(pastebin.found))
            events['pastebin'] = len(pastebin.found)
            if len(pastebin.found) > 0:
                for post_id, data in pastebin.found.iteritems():
                    job_stats['pastebin'] = 'sending syslog event'
                    cef = 'CEF:0|OSINT|ArcReactor|1.0|100|Watchlist Keyword Found|1|src=%s msg=%s' % (post_id, data)
                    reactor.send_syslog(cef)
                    events['pastebin'] += 1
            job_stats['pastebin'] = 'finished successfully'
        job_stats['pastebin'] = 'finished with errors'

    def run_otx(self):
        # the otx module is very simple. it is only a single function.
        # i would just include the whole function right here but i'd like to
        # stick to the standard of keeping each module separate from the back-end
        # code. all we do here is call the module's function and wait for completion
        # to update the job status. the syslog events are sent from the otx module
        # as well. the reputation db has 100k+ entries, no point in moving that much
        # data all over our application if we can send the syslog events from their
        # original entry point.
        # TODO: rewrite otx module to split every 500-1000 entries and assign a worker
        # per entry group. this will be much quicker instead of sending one event per
        # and having to wait for the execution to finish
        reactor.status('info', 'otx', 'launching otx module')
        job_stats['otx'] = 'running otx data collection'
        if otx.gather_data():
            job_stats['otx'] = 'finished successfully'
            events['otx'] = otx.count
        else:
            job_stats['otx'] = 'finished with errors'









