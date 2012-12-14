#!/usr/bin/env python

from lib import reactor
import readline
import sys, os 
import commands
from optparse import OptionParser

# obviously incomplete file
# this will be the main launcher utility
# might even remove this completely and just offer
# two scripts, one for the console and one for command line control
# meh meh meh.

usage = """

Usage: ./launch.py [--interactive] [--collect] [--daemon] [--no-usage]

This is the main launcher for ArcReactor.
All of the output collected by the modules below is parsed into CEF format and sent via syslog
to an ArcSight manager or connector appliance. The configuration file for sending these events
is located in the /opt/arcreactor/conf directory.

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


