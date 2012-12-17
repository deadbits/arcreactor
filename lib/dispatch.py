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
from datetime import datetime
import atexit
import threading
import reactor
import pastebin
import otx
import knownbad
#import exploits
#import twitter
#import facebook
#import reddit
#import kippo

"""
this module is under heavy development.
    - receive command from console.py interaction
    - determine which type of command we received
        * module execution (start, stop, data)
        * configuration (config *) <- these might go somewhere else
        * job management (info tasks, info reactor, etc)

    * if we get a module execution command:
        - create new job/workers to handle execution of that module
           * we can either send to bg and continue to interact w/ console
            or just run it, watch progress and wait until complete
        - job + reactor stats are updated to reflect mod being exec'd 
        - continue to update stats along the way
        - verify successful completion
        - remove job from running list and free up workers
    * configuration commands can be a simple ConfigParser function to update
      our cfg's and reload the files
    * job management stats are updated from the module executions so we simply
      read and print the stats.
      keep track of: running, status, time started/ended, total events sent,
      events sent per mod, format usage, syslog info, etc. 

TODO:
    - job clean-up functions
    - command receive function
    - build job execution queue
    - move over finished multithreading functions (testing/dispatch/multi.py)
    - standardize data output from modules
"""

job_stats = {}
"""
job_stats keeps track of which module is doing what. 
this hash is also used when we pull and output the job statistics using the 'info' cmd. 
example:
job_stats = {
    'pastebin': {
        'status': 'running',
        'message': 'retrieving newest archive',
        'started': '2012-12-16 12:34:20',
        'ended': '',
        'events': 0,
    }
}
"""

class Jobs:
    def __init__(self):
        """
        This class is used to manage all running modules, handle statistics,
        ensure proper execution and clean-up and so on.
        """
        self.running = []

    def start_module(self, module):
        """
        this is really just a placeholder to give a general idea of how this
        should work. use this function to start modules/jobs, track what is 
        running, assign workers if needed, etc.
        """
        if self.module in reactor.module.keys() and module not in self.running:
            reactor.status('info', 'arcreactor', 'starting collection module %s' % self.module)
            if self.module == 'pastebin':
                Module.run_pastebin()
            elif self.module == 'otx':
                Module.run_otx()
            elif self.module == 'knownbad':
                Module.run_knownbad()
            else:
                pass


    def kill_all(self):
        """
        this function will safely kill all running jobs.       
        should be registered as an atexit function when complete.
        """

    def kill_job(self, job):
        """
        this function will safely kill an individual job
        """

    def get_stats(self, type='all'):
        # check if we have any jobs running or paused
        if len(job_stats) > 0:
            if type == 'all':
                # iterate through all the keys and nested key/value pairs
                for j in job_stats.keys():
                    print('\n%s => ' % j)
                    for key, value in job_stats[j].iteritems():
                        print('%s:  \t%s' % (key, value))
            # check if non-standard 'type' is in the first set of keys
            elif type in job_stats.keys():
                print('\n%s => ' % type)
                # iterate through the key/value pairs for that job type
                for key, value in job_stats[type].iteritems():
                    print('%s:  \t%s' % (key, value))
            else:
                reactor.status('info', 'arcreactor', 'cannot find job %s' % type)
        else:
            reactor.status('info', 'arcreactor', 'no running jobs')


class Module:
    def __init__(self):
        # this entire class is for interacting with the collection modules
        self.running = 0
        self.queued = 0

    def run_knownbad(self):
        # launch the knownbad.py module
        # TODO: split malicious host and ip address sources/events
        jobs_stats['knownbad'] = {
            'status': 'running',
            'started': str(datetime.now()).split('.')[0],
            'message': 'loading sources',
            'events': 0
        }
        if knownbad.load_sources():
            # iterate through loaded sources
            for src in knownbad.sources:
                job_stats['knownbad'] = { 'message': 'gathering data from sources' }
                self.host, self.source = knownbad.gather_data(src)
                if not self.host == "":
                    job_stats['knownbad'] = { 'message': 'sending syslog events' }
                    self.cef = 'CEF:0|OSINT|ArcReactor|1.0|100|Known Malicious Host|1|src=%s msg=%s' % (self.host, self.source)
                    reactor.send_syslog(self.cef)
                    # add one to the event counter per syslog event sent
                    job_stats['knownbad'] = { 'events': job_stats['knownbad']['events'] + 1 }
            job_stats['knownbad'] = { 'status': 'finished', 'message': 'finished successfully', 'ended': str(datetime.now()).split('.')[0] }
        job_stats['knownbad'] = { 'message': 'finished with errors', 'ended': str(datetime.now()).split('.')[0] }

    def run_pastebin(self):
        job_stats['pastebin'] = {
            'status': 'running',
            'started': str(datetime.now()).split('.')[0],
            'message': 'loading keywords',
            'events': 0
        }
        reactor.status('info', 'pastebin', 'launching pastebin module')
        if pastebin.load_words():
            job_stats['pastebin'] = { 'message': 'collecting post archive' }
            pastebin.gather_archive()
            """
            this loop is needed due of an odd problem with the requests for post content.
            we collect 250 posts at a time from the archive, but during testing the search
            would stop half-way through the queued posts. collect 250, stop at 125, re-run
            with the remaining 125, stop at ~63 and so on. i am not sure why this happens. 
            to fix this, we set a loop that forces the gather_content/search_raw functions
            to execute until the post queue is all the way down to zero.
            """
            if len(pastebin.queue) > 0:
                for post in pastebin.queue:
                    job_stats['pastebin'] = { 'message': 'searching post %s' % post }
                    # the search_raw function is called from within gather_content
                    pastebin.gather_content(post)
            job_stats['pastebin'] = { 'events': len(pastebin.found) }
            if len(pastebin.found) > 0:
                for self.post_id, self.data in pastebin.found.iteritems():
                    job_stats['pastebin'] = { 'message': 'sending syslog events' }
                    self.cef = 'CEF:0|OSINT|ArcReactor|1.0|100|Watchlist Keyword Found|1|src=%s msg=%s' % (self.post_id, self.data)
                    reactor.send_syslog(self.cef)
            job_stats['pastebin'] = { 'status': 'finished', 'message': 'finished successfully', 'ended': str(datetime.now()).split('.')[0] }
        job_stats['pastebin'] = { 'status': 'finished', 'message': 'finished with errors', 'ended': str(datetime.now()).split('.')[0] }

    def run_otx(self):
        # run the otx.py module.
        # this module is very simple as it has only a single function
        # i would include the function here but i'd like to keep to the
        # standard of separating each module from back-end as much as possible.
        # TODO: split every 500-1000 entries and assign worker per entry group
        #       this might speed up the event sending, since we have alot of data from
        #       the otx rep db.
        reactor.status('info', 'otx', 'launching otx module')
        job_stats['otx'] = {
            'status': 'running',
            'started': str(datetime.now()).split('.')[0],
            'message': 'loading keywords',
            'events': 0
        }
        if otx.gather_data():
            job_stats['otx'] = {'status': 'finished', 'message': 'finished successfully', 'ended': str(datetime.now()).split('.')[0] }
            jobs_stats['otx'] = {'events': otx.count }
        else:
            job_stats['otx'] = { 'status': 'finished', 'message': 'finished with errors', 'ended': str(datetime.now()).split('.')[0] }









