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
#import atexit
from datetime import datetime
from Queue import Queue
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



job_stats = {}
#job_stats keeps track of which module is doing what. 
#this hash is also used when we pull and output the job statistics using the 'info' cmd. 
#example:
#job_stats = {
#    'pastebin': {
#        'status': 'running',
#        'message': 'retrieving newest archive',
#        'started': '2012-12-16 12:34:20',
#        'ended': '',
#        'events': 0,
#    }
#}

def receive(command):
    if command.startswith('start'):
        module = command.split(' ')[1]
        Jobs.start_module(module)
    #elif command.startswith('kill'):
    #    task = command.split(' ')[1]
    #    if task == 'all':
    #        Jobs.kill_all()
    #    elif task in reactor.modules.keys():
    #        Jobs.kill_job(task)
    #    else:
    #        reactor.status('warn', 'arcreactor', '%s is not a valid option')
    elif command == 'info tasks':
        Jobs.get_stats()
    elif command.startswith('cfg'):
        conf = command.split(' ')[1]
        Config.manage(conf)
    else:
        reactor.status('warn', 'arcreactor', '%s is not a valid command')


class Jobs:
    def __init__(self):
        """
        Handles job interaction tasks.

        This class is responsible for the overall management and monitoring of any major tasks
        within ArcReactor. Smaller, static functions do not need to be included within this
        management class.
        Features:
            - start/stop collection modules
            - create job queues and assign workers
            - collect statistics on running jobs
            - ensure safe shutdown of jobs

        """
        self.running = []

    def start_module(self, module):
        """
        Start execution of collection modules

        This functions only purpose is to take a module name as input, verify that the module
        exists, find the correct function from the Module() class and then execute. There are
        various checks to ensure only valid module names are being passed up until this point,
        so any input we receive here should be valid.

        """
        if module in self.running:
            arcreactor.status('info', 'arcreactor', 'collection module %s is all ready running' % module)
        
        elif module in reactor.modules.keys():
            if module == 'all':
                for self.name in reactor.modules.keys():
                    reactor.statux('info', 'arcreactor', 'starting collection module %s' % module)
                    self.running.append(self.name)
                Module.run_pastebin()
                Module.run_knownbad()
                Module.run_otx()
            elif module == 'pastebin':
                Module.run_pastebin()
            elif module == 'otx':
                Module.run_otx()
            elif module == 'knownbad':
                Module.run_knownbad()
            else:
                reactor.status('warn', 'arcreactor', '%s is not a valid collection module' % module)
        else:
            reactor.status('warn', 'arcreactor', '%s is not a valid collection module' % module)

    #def kill_all(self):
    #    """
    #    Safely kill all running and queued jobs.
    #
    #    Ensures safe shutdown of ArcReactor jobs. This function is also registered as an
    #    atexit function so it will be called everytime ArcReactor exits - whether by user
    #    intervention or signal interrupts.
    #
    #    """
    #    if len(job_stats) > 0:
    #        for self.job in job_stats.keys():
    #            reactor.status('info', 'arcreactor', 'killing %s' % self.job)
    #            if self.job in self.running or self.queue:
    #                self.queue[self.job].stop()
    #                job_stats.remove(job)
    #                return True
    #    else:
    #        reactor.status('info', 'arcreactor', 'no running jobs')
    #        return False


    #def kill_job(self, job):
    #    """ Safely kill a specific running or queued job. """
    #    if job in job_stats.keys():
    #        reactor.status('info', 'arcreactor', 'stopping %s' % job)
    #        if job in self.running or self.queue:
    #            self.queue[job].stop()
    #            job_stats.remove(job)
    #            return True
    #    reactor.status('info', 'arcreactor', '%s does not seem to exist' % job)
    #    return False

    def get_stats(self, type='all'):
        """
        Gather statistics on running and queued jobs.

        Jobs.get_stats() interacts with the job_stats hash to pull down information
        on running, paused and queued jobs. This function will only be called when the
        user passes the console comamnd 'info tasks'. 

        """
        if len(job_stats) > 0:
            if type == 'all':
                for self.job_title in job_stats.keys():
                    print('\n%s => ' % self.job_title)
                    for self.key, self.value in job_stats[self.title].iteritems():
                        print('{0:12}: \t {1:16}'.format(self.key, self.value))
            elif type in job_stats.keys():
                print('\n%s => ' % type)
                for self.key, self.value in job_stats[type].iteritems():
                    print('{0:12}: \t {1:16}'.format(self.key, self.value))
            else:
                reactor.status('info', 'arcreactor', 'cannot find job %s' % type)
        else:
            reactor.status('info', 'arcreactor', 'no running or queued jobs')


class Module:
    def __init__(self):
        self.running = 0
        self.queued = 0

    def run_knownbad(self):
        jobs_stats['knownbad'] = {
            'status': 'running',
            'started': str(datetime.now()).split('.')[0],
            'message': 'loading sources',
            'events': 0
        }
        if knownbad.load_sources():
            for src in knownbad.sources:
                job_stats['knownbad'] = { 'message': 'gathering data from sources' }
                self.host, self.source = knownbad.gather_data(src)
                if not self.host == "":
                    job_stats['knownbad'] = { 'message': 'sending syslog events' }
                    self.cef = 'CEF:0|OSINT|ArcReactor|1.0|100|Known Malicious Host|1|src=%s msg=%s' % (self.host, self.source)
                    reactor.send_syslog(self.cef)
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












