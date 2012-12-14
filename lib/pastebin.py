#!/usr/bin/env python
#
# osint collection for pastebin
# stand-alone version of the scraper from ArcReactor
#
# ohdae [ams]
# http://github.com/ohdae/ArcReactor/
#

import requests
import re, string
import os, sys
import time
import reactor


archive = "http://www.pastebin.com/archive"
raw = "http://pastebin.com/raw.php?i="

queue = []
found = {}
watch_list = []
regex = re.compile('<td><img src="/i/t.gif" .*?<a href="/(.*?)">(.*?)</a></td>.*?<td>(.*?)</td>', re.S)

def load_words():
    watch_list = reactor.load_text(reactor.PATH_CONF+"/watchlist.conf")
    if len(watch_list) > 0:
        reactor.status("info", "pastebin", "%d keywords added to watch list" % (len(watch_list)))
        return True
    return False

def gather_archive():
    try:
        # pull down the http content and check regex all in one line
        posts = regex.findall(requests.get(archive).content)
        for p in posts:
            post_id, post_title = p[0], p[1]
            if post_id not in queue:
                # if this post has not been seen, add it to our post queue
                reactor.status("info", "pastebin", "post id %s added to queue" % post_id)
                queue.append(post_id)
        reactor.status("info", "pastebin", "total posts added to queue: %d" % len(queue))
    except:
        reactor.status("error", "pastebin", "failed to fetch pastebin archive")

def gather_content(post_id):
    try:
        # pull down the http content for raw pb post
        raw = requests.get("http://pastebin.com/raw.php?i=%s" % post_id).content
        queue.remove(post_id)
        if not "Unknown Paste ID!" in raw:
            reactor.status("info", "pastebin", "searching post id %s" % post_id)
            # check if this is a multi-lined post
            if "\r\n" in raw:
                # if this is multi-lined (which they usually are) check each line
                # one at a time for our keyword. this process is actually pretty fast
                # for performing a one to one search
                lines = raw.split("\r\n")
                for line in lines:
                    search_raw(line, post_id)
            else:
                # if its only one line, search that line
                search_raw(raw, post_id)
    except:
        reactor.status("error", "pastebin", "failed to fetch post id %s" % post_id)

def search_raw(data, post_id):
    # search the input data for any word from our watchlist
    for word in watch_list:
        if word in data:
            # if we find a hit, add it to our found hash
            # in the form: post_id = data. this will be used
            # later on when displaying the output
            #
            # if found != {}:
            #     for key, value in found.iteritems():
            #         print("post: %s" % key)
            #         print("data: %s" % value)
            #
            found[post_id] = data
            reactor.status("info", "pastebin", "found %s in pastebin post %s" % (word, post_id))


#def start_all():
#    # this function will perform the entire process
#    # from start to finish. i added this function so
#    # we can still call each function individually if
#    # needed, while using the reactor console.
#    #
#    # gather_words populates the queue
#    if gather_words():
#        # gather_archive pulls down the post list
#        # and automatically performs
#        gather_archive()
#        if len(queue) > 0:
#            for post in queue:
#                gather_content(post)
#    return found




