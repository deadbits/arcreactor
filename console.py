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
# to the 
#

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
    'help': 'display this menu',
    'quit': 'exit the console',
    'exit': 'exit the console',
    'exec': 'execute os command',
    'about': 'display basic information',
    'clear': 'clears the screen',
    'config sources': 'manage osint sources',
    'config keywords': 'manage your keywords',
    'config syslog': 'manage siem syslog settings',
    'modules': 'list all collection module information',
    'keywords': 'show loaded keywords',
    'start all': 'start all available modules',
    'stop all': 'stop all running modules',
    'start <module>': 'launch the selected module',
    'stop <module>': 'stop the selected module',
    'info tasks': 'view stats on running and queued tasks',
    'info reactor': 'view general ArcReactor stats',
    'data <module>': 'view information on data collected by module',
    'dashboard': 'launch web dashboard [experimental]'
}

class Completer:
    def __init__(self):
        self.words = [ 'help', 'quit', 'exit', 'about', 'clear', 'config', 'sources', 'keywords', 'syslog', 'modules',
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
        # perform session start-up
        reactor.status('info', 'arcreactor', 'initializing new console session')
        reactor.status('info', 'arcreactor', 'loading configuration files')
        # load the config files into this module
        keywords = reactor.load_keywords(reactor.PATH_CONF+'/keywords.cfg')
        sources = reactor.load_sources(reactor.PATH_CONF+'/sources.cfg')
        options = reactor.load_config(reactor.PATH_CONF+'/syslog.cfg')
        self.console()

    def kill_session(self):
        reactor.status('info', 'arcreactor', 'shutting down ArcReactor console')
        sys.exit(0)

    def check_command(self, cmd):
        # verify that command is valid. this is a super hack job.
        # TODO: fix this horrible, ugly function
        if cmd in help.keys() or ' ' in cmd and cmd.split(' ')[0] in help.keys():
            return True
        return False

    def dispath_command(self, cmd):
        if ' ' in cmd:
            cmd = cmd.split(' ')

    def pre_command(self, cmd):
        # pre_command takes care of the basic functions.
        # this handles alot of the simple, non-collection and
        # non-statistics stuff. this way we only need to send
        # the more actionable commands to the main dispatcher
        if cmd == 'quit' or cmd == 'exit': 
            self.kill_session()
        elif cmd == 'help':
            print('ArcReactor Commands')
            for key, value in help.iteritems():
                print('%s\t\t\t%s' % (key, value))
            print('\n')
        elif cmd == 'clear': 
            os.system('clear')
        elif cmd.startswith('exec'):
            # remove 'exec' from the command and run the rest
            self.exec_output = commands.getout(' '.join(cmd.split(' ')[1:]))
            print self.exec_output
        elif cmd == 'keywords':
            if len(keywords) > 0:
                print('\nWatch-List Keywords')
                for word in keywords:
                    print word
            else: print('[*] keyword list is empty')
        elif cmd == 'sources':
            if len(sources) > 0:
                print('\nExternal Sources')
                for src in sources:
                    print src
            else: print('[*] source list is empty')
        else:
            self.dispatch_command()

    def console(self):
        print reactor.ascii
        print('Welcome to the ArcReactor console!')
        print('type 'help' to get started\n')

        while True:
            completer = Completer()
            readline.set_completer(completer.complete)
            cmd = raw_input(prompt)

            if self.check_command(cmd):
                self.pre_command(cmd)
            else:
                print('[!] '%s' is not a valid command. type 'help' for assistance')
            





