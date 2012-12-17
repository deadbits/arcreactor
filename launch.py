#!/usr/bin/env python

from lib import reactor
from lib import dispatch 
import console
import argparse
import sys, os

# the usage block should explain itself.
# you *must* run this when starting ArcReactor, you can't run console.py by itself.
# eventually this whole application will be turned into an optional service and this
# launcher will control the 'start', 'stop', 'restart', etc commands for the service.

usage = """

This is the main launcher for ArcReactor.

Below is a full list of all available modules and explanations of both ArcReactor execution modes.
For further documentation or assistance, please refer to the online Wiki or the 'docs' directory.

Modules:
malicious  \tgathers known malicious ip addresses and hostnames from public sources
kippo      \tcollect attacker information from your kippo honeypots
otx        \tgathers known malicious ip addresses, hostnames and reputation data from AlienVault's OTX 
reddit     \tscrapes reddit posts for keywords defined in the watchlist configuration
twitter    \tscrapes public twitter timelines for keywords defined in the watchlist configuration
pastebin   \tscrapes public pastebin archives for keywords defined in the watchlist configuration
facebook   \tscrapes public facebook posts for keywords defined in the watchlist configuration
exploits   \tscrapes exploit-db for information on newly released remote, local and dos exploits

Options:
--interactive
    This command will start an interactive console where you can launch and interact with
    specific collection tasks, edit configuration files and have fine-tuned control over
    your data collection.
    This is the suggested method of use.

--collect
    This command will start all data collection tasks using the current configuration files.
    ArcReactor will attempt to execute each of the available modules and send syslog events for
    all data that is gathered.

--daemon
    Daemonize the process when used with the --collect command. All status and error messages
    will be logged to the /opt/arcreactor/var/log/reactor.log file.


"""

print usage
parser = argparse.ArgumentParser()
parser.add_argument("--interactive", help="start interactive console", action="store_true")
parser.add_argument("--collect", help="execute all collection modules", action="store_true")
parser.add_argument("--daemon", help="run --collect as background process", action="store_true")
args = parser.parse_args()

if args.interactive:
    session = console.Session()
    reactor.start_logger()
    session.new()
elif args.collect:
    if args.daemon:
        background_job = True
    launcher = dispatch.Module()
    jobs = dispatch.Jobs()
    reactor.status('info', 'arcreactor', 'launching all collection modules')
    launcher.run_knownbad()
    launcher.run_pastebin()
    launcher.run_otx()
    reactor.status('info', 'arcreactor', 'all collection modules finished')
    print('[*] Collection Statistics: ')
    jobs.get_stats()
    sys.exit(0)
else:
    print('[!] arcreactor - invalid argument!')
    sys.exit(1)










