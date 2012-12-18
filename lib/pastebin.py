#!/usr/bin/env python
#
# pastebin collection module
# part of ArcReactor
#
# ohdae [ams]
# http://github.com/ohdae/arcreactor/
#

import reactor
import re

archive = "http://www.pastebin.com/archive"
raw = "http://pastebin.com/raw.php?i="

queue = []
found = {}
watch_list = []
regex = re.compile('<td><img src="/i/t.gif" .*?<a href="/(.*?)">(.*?)</a></td>.*?<td>(.*?)</td>', re.S)

def load_words():
    watch_list = reactor.load_keywords(reactor.PATH_CONF+'/keywords.cfg')
    if len(watch_list) > 0:
        reactor.status('info', 'pastebin', '%d keywords added to watch list' % (len(watch_list)))
        return True
    return False

def gather_archive():
    try:
        posts = reactor.http_request(archive)
        posts = regex.findall(posts)
        for p in posts:
            post_id, post_title = p[0], p[1]
            if post_id not in queue:
                reactor.status('info', 'pastebin', 'post id %s added to queue' % post_id)
                queue.append(post_id)
        reactor.status('info', 'pastebin', 'total posts added to queue: %d' % len(queue))
    except:
        reactor.status('warn', 'pastebin', 'failed to fetch pastebin archive')

def gather_content(post_id):
    try:
        raw = reactor.http_request('http://pastebin.com/raw.php?i=%s' % post_id)
        queue.remove(post_id)
        if not 'Unknown Paste ID!' in raw and raw is not None:
            reactor.status('info', 'pastebin', 'searching post id %s' % post_id)
            if '\r\n' in raw:
                lines = raw.split('\r\n')
                for line in lines:
                    search_raw(line, post_id)
            else:
                search_raw(raw, post_id)
    except:
        reactor.status('warn', 'pastebin', 'failed to fetch post id %s' % post_id)

def search_raw(data, post_id):
    for word in watch_list:
        if word in data:
            found[post_id] = data
            reactor.status('info', 'pastebin', 'found %s in pastebin post %s' % (word, post_id))




