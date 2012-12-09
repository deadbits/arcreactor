#!/usr/bin/env python
#
# osint collection for pastebin
# stand-alone version of the scraper from ArcReactor
#
# ohdae [ams]
# http://github.com/ohdae/ArcReactor/
#

import requests
import re, sys
import time

# define some stuff
pb_archive = "http://www.pastebin.com/archive"
pb_raw = "http://pastebin.com/raw.php?i="
pb_regex = re.compile('<td><img src="/i/t.gif" .*?<a href="/(.*?)">(.*?)</a></td>.*?<td>(.*?)</td>', re.S)
pb_queue = []
found = {}

# this will eventually be changed to a config file where the user can define
# keywords to look out for, individually or in pairs. until then, edit this
# list to your liking.
# e.g.: 
# watch = 'hacked' + 'my company name'
# watch = 'myemail@address.here'
watch_words = ['hacked', 'corporate', 'owned', 'sql injection', 'password', 'leak', 'waffles']

def collect_posts():
    try:
        posts = pb_regex.findall(requests.get(pb_archive).content)
        for p in posts:
            paste_id, paste_title = p[0], p[1]
            if paste_id not in pb_queue:
                print("[~] collected ")
                print("    id: %s | title: %s" % (paste_id, paste_title))
                pb_queue.append(paste_id)
        print("[~] total posts in queue: %d" % len(pb_queue))
    except:
        print("[!] problem fetching pastebin archive.")
        print("    check your network connection and try again.")

def search_content(post_id):
    try:
        raw = requests.get("%s%s" % (pb_raw, post_id)).content
        pb_queue.remove(post_id)
        if "\r\n" in raw:
            data = raw.split("\r\n")
            for line in data:
                search_raw(line, post_id)
        else:
            search_raw(raw, post_id)
    except:
        print("[!] problem fetching post %s" % post_id)

def search_raw(data, post_id):
    for word in watch_words:
        if word in data:
            found[post_id] = data
            print("\n")
            print("[*] found:\t%s" % word)
            print("     post:\t%s" % post_id)
            print("     data:\t%s" % data)


def menu():
    print(" help  \tdisplay this command menu")
    print(" gather\tcollect new posts from pastebin.com/archive")
    print(" search\tsearch current post queue for keywords")
    print(" words \tview current keyword watch list")
    print(" posts \tview post queue information and entries")
    print(" found \tview all found data")
    print(" exit  \texit this application\n")

def main():
    menu()
    while True:
        r = raw_input("arc >> ")
        if r == "gather":
            collect_posts()
        elif r == "search":
            if pb_queue != "":
                start_queue = len(pb_queue)
                for post in pb_queue:
                    search_content(post)
                    print("\n[~] searched %s" % post)
                    time.sleep(0.5)
            else:
                print("[!] post queue is currently empty. try running 'gather' first.")
        elif r == "words":
            print("[~] keyword watch list: ")
            for word in watch_words:
                print word
        elif r == "posts":
            if pb_queue != "":
                print("[~] total queued posts: %d" % len(pb_queue))
            else:
                print("[!] post queue is currently empty. try running 'gather' first.")
        elif r == "exit" or r == "quit":
            print("[*] exiting application...")
            sys.exit(0)
        elif r == "found":
            if found != "":
                for key, value in found.iteritems():
                    print("\n")
                    print("post id: %s" % key)
                    print("   data: %s" % value)
        elif r == "help":
            menu()
        else:
            print("[!] this is not a valid command.")


print("\n\n")
print("\t open-source data gathering ")
print("\t   source >> pastebin.com   ")
print("\t    author: ohdae [ams] ")
print("\n\thttp://github.com/ohdae/arcreactor")
print("\n\n")
main()