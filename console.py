#!/usr/bin/env python
#
# part of ArcReactor [version 1.0]
# https://github.com/ohdae/arcreactor
# 
# Interactive console.
# this module handles all interactive console sessions
# here we provide the basic console functionality such
# as command input & output, editing configuration files,
# preliminary command verification and sending commands
# to the dispatch module
#
# TODO:
#   - config edit commands (configparser)
#   - fix keyword/source loading issues
#   - rewrite cmd verification and dispatch interaction
#   - create better environment check before starting new session

from lib import reactor
from lib import dispatch 
import os, sys
import readline
import signal
import commands

readline.parse_and_bind('tab: complete') 
keywords = []
sources = []
options = {}
prompt = 'reactor >> '
help = {
    'general': {
        'help': 'display this menu',
        'quit': 'exit the console',
        'about': 'display about dialog',
        'exec': 'execute os command',
        'modules': 'show description of all modules',
        'keywords': 'show current watchlist keywords'
    },
    'configuration': {
        'cfg syslog': 'manage siem and syslog settings',
        'cfg sources': 'manage external sources',
        'cfg keywords': 'manage watchlist keywords'
    },
    'statistics': {
        'info tasks': 'view stats on running and queued jobs',
        'info reactor': 'view general ArcReactor stats',
        'data <module>': 'view information on data collected by module'
    },
    'collection': {
        'start all': 'start all collection modules',
        #'stop all': 'stop all running collection modules',
        'start <module>': 'launch selected module',
        #'stop <module>': 'stop selected module',
        'dashboard': 'start the web dashboard [experimental]'
    }
}


class Completer:
    def __init__(self):
        self.words = [ 'help', 'quit', 'exit', 'about', 'clear', 'cfg', 'sources', 'keywords', 'syslog', 'modules',
            'start', 'stop', 'all', 'info', 'data', 'reactor', 'tasks', 'dashboard', 'pastebin', 'otx', 'exploits', 'twitter' ]
        self.prefix = ''

    def complete(self, prefix, index):
        if prefix != self.prefix:
            self.matching_words = [w for w in cmds if w.startswith(prefix)]
            self.prefix = prefix
        else: pass
        try:
            return self.matching_words[index]
        except IndexError:
            return None

class Session(object):
    def __init__(self):
        signal.signal(signal.SIGINT, reactor.signal_handler)

    def new(self):
        """
        Initializes a new console session

        Perform some simple environment checks to ensure that we can properly
        start a new interactive session, load needed configuration files and if
        these pass, we start our console.

        """
        reactor.status('info', 'arcreactor', 'initializing new console session')
        reactor.status('info', 'arcreactor', 'loading configuration files')
        keywords = reactor.load_keywords(reactor.PATH_CONF+'/keywords.cfg')
        sources = reactor.load_sources(reactor.PATH_CONF+'/sources.cfg')
        options = reactor.load_config(reactor.PATH_CONF+'/reactor.cfg')
        self.console()

    def kill_session(self):
        if len(dispatch.job_stats) > 0:
            print('[*] %d jobs are still running.' & len(dispatch.job_stats))
            print('are you sure you want to exit?')
            self.answer = raw_input('[y/n]')
            if self.answer == 'y': 
                pass
            elif self.answer == 'n':
                print('[*] returning to ArcReactor console')
                self.console()
            else:
                print('[!] invalid answer. returning to ArcReactor console.')
                self.console()
        reactor.status('info', 'arcreactor', 'shutting down ArcReactor console')
        sys.exit(0)

    def pre_command(self, cmd):
        """
        Handle basic functions before we send command to dispatch.

        Several commands do not need to be sent to dispatch to be executed,
        so we take care of the more basic/static commands here and only send
        the more actionable commands to the dispatch module.

        """
        if cmd == 'quit' or cmd == 'exit': 
            self.kill_session()
        elif cmd == 'help':
            print('\n\t  general')
            for self.c, self.i in help['general'].iteritems():
                print('{0:12} \t {1:26}'.format(self.c, self.i))
            print('\n\t  configuration')
            for self.c, self.i in help['configuration'].iteritems():
                print('{0:12} \t {1:26}'.format(self.c, self.i))
            print('\n\t  statistics')
            for self.c, self.i in help['statistics'].iteritems():
                print('{0:12} \t {1:26}'.format(self.c, self.i))
            print('\n\t  collection')
            for self.c, self.i in help['collection'].iteritems():
                print('{0:12} \t {1:26}'.format(self.c, self.i))
        elif cmd == 'clear': 
            os.system('clear')
        elif cmd.startswith('exec'):
            self.exec_output = commands.getoutput(' '.join(cmd.split(' ')[1:]))
            print self.exec_output
        elif cmd == 'keywords':
            if len(keywords) > 0:
                print('\nWatch-List Keywords')
                for self.word in keywords:
                    print self.word
            else:
                print('[*] keyword list is empty')
        elif cmd == 'sources':
            if len(sources) > 0:
                print('\nExternal Sources')
                for self.src in sources:
                    print self.src
            else: 
                print('[*] source list is empty')
        elif cmd == 'modules':
            print('\nAvailable Collection Modules')
            for self.mod_name, self.mod_info in reactor.modules.iteritems():
                print('%s\t\t%s' % (self.mod_name, self.mod_info))
        else:
            dispatch.receive(cmd)

    def check_command(self, args):
        try:
            cmd, arg = args.split(' ')
        except:
            cmd = args

        for title in help.keys():
            if cmd in help[title].keys():
                return True
        return False

    def console(self):
        print reactor.ascii
        print('Welcome to the ArcReactor console!')
        print('type `help` to get started\n')

        while True:
            completer = Completer()
            readline.set_completer(completer.complete)
            cmd = raw_input(prompt)

            if self.check_command(cmd):
                self.pre_command(cmd)


            





