#!/usr/bin/env python


from gevent import monkey; monkey.patch_socket()
from gevent import Greenlet as greenlet, sleep

from os import urandom, getpid
from socket import gethostname
from sys import exit

from logging import info, debug, warn, error, INFO, DEBUG, WARN, ERROR, \
    getLogger as get_logger

from feedparser import parse
from itsdangerous import URLSafeTimedSerializer as url_serializer

from random import randint
from datetime import datetime
from json import dumps, loads, load
from hashlib import sha256

from requests import get, post, ConnectionError, request, Response
#not sure how to working gevent support here
#not sure it's needed, but maybe later

'''
fetch is the part of the site that does all of the feedparsing stuff.
As an experiment, it doesn't bother with mongodb at all, just uses the 
private sync API.

It's quite possible that this is the most horrible way ever to do this, 
but it does have the compelling feature that it's more or less no work 
to move it to a totally different machine.

Dividing the load shouldn't even be that hard, if you add some API-side 
smarts for dividing up the work.

'''

minute = 60
hour = minute * 60 
day = hour * 24
week = day * 7

user_agent = 'triage/alpha http://no-url-yet.com/'

class feed_watcher(greenlet): 
    def __init__(self, feed_json, server_addr):
        greenlet.__init__(self)

        # feed is a json dict
        self.xml_url = feed.get('xml_url')
        self.etag = feed.get('etag')
        self.modified = feed.get('modified')
        self.last_updated = feed.get('last_updated')
        self.next_update = feed.get('next_update')
        self.avg_interval = feed.get('avg_interval')
        self.feed_id = feed.get('feed_id')
        self.new = feed.get('new')

        self.posts_queue = []

    def update(self):
        # determine if we should check for new posts

        if time() > self.next_update:
            update = parse(self.xml_url, 
                           agent = user_agent, 
                           etag = self.etag,
                           modified = self.modified) 
            if not update.status == 304:
                self.etag = update.etag
                self.modified = update.modified
                
                #push an update to the feed state
                
                #will need some non-compliance detection here.


        for post in self.posts_queue:
            sleep(1)
            rest_call('POST', '/fetch/feed/%s/' % self.feed_id,
                      {})
            
        self.posts_queue  = []

        return day

    def _run(self):
        while True:
            til_next = self.update()
            sleep(til_next)
            

class feed_getter(greenlet):
    def __init__(self, server_addr, name, serializer):
        greenlet.__init__(self)
        debug('init feed_getter: ' + server_addr + ' ' + name)#, serializer)
        self.server_addr = server_addr 
        self.name = name
        self.serializer = serializer

        self.watchers = []

    def register(self):
        # if the server goes away or loses our registration,
        # we should try again
        ret = rest_call(self.server_addr, 'register/', 'POST',
                        self.serializer,
                        values = { 'name':self.name, 
                                   'pid':getpid(),
                                   'addr':self.server_addr })
        
        if ret.status_code == 200:
            return True
        else: 
            return False
            #check for name conflict and reregister if need be
            
        

    def _run(self):
        debug('starting up the main feed getter')
        while not self.register():
            sleep(5)

        while True:
            # see if the server has a feed for us
            ret = rest_call(self.server_addr, 'feed/', 'GET',
                            self.serializer, params = {'name':self.name})
            try: 
                if ret and ret.content:
                    feed_url = loads(ret.content)
                    feed = feed_watcher(feed_url, self.server_addr) 
                    feed.spawn()
                    feed.start()
                else:
                    ret = None
            except Exception, e:
                print e 
                
            if not ret: 
                sleep(10)


def rest_call(host, path, method, serializer, params = {}, values = {}):

    values = dict([ (x, unicode(y)) for x, y in values.items() ])

    cksum = sha256(repr(values)).hexdigest()
    cryptkey = serializer.dumps(cksum)
    params.update({ 'key' : cryptkey })

    debug('values: ' + repr(values))

    try: 
        if method == "POST":
            rep = post(host + '/fetch/' + path, params=params, data=values)
        elif method == "GET":
            rep = get(host + '/fetch/' + path, params=params)
    except ConnectionError:
        #not sure this is really the right thing to do
        dummy = Response()
        dummy.status_code = 500
        return dummy
        

    if rep.status_code == 200:
        print rep.content
        if rep.content:
            data = loads(rep.content)
            print data
    else: 
        error('got status code %s' % rep.status_code)

    return rep

# global for ease of use.
serializer = None

def main():
    global serializer, name

    name = 'fetcher' + str(randint(100, 9999))

    cfg = load(open('/etc/fetch/fetch.cfg'))

    server_addr = cfg['server_addr']

    serializer = url_serializer(cfg['key'])

    get_logger().name = name
    get_logger().setLevel(cfg['log_level'])

    info('starting up')

    fg = feed_getter(server_addr, name, serializer)
    fg.start()
    fg.join()

    warn('not sure why we\'re here')
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(0)

