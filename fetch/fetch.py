
from gevent import monkey; monkey.patch_socket()
from gevent import Greenlet as greenlet, sleep

from os import urandom, getpid
from socket import gethostname
from sys import exit

from logger import info, debug, warn, error, INFO, DEBUG, WARN, ERROR, \
    getLogger as get_logger, setLevel as set_level

from feedsync import parse
from itsdangerous import URLSafeTimedSerializer as url_serializer

from datetime import datetime
from json import dumps, loads, load
from urllib import urlencode 
from urllib2 import Request as request, urlopen, HTTPError, URLError
from httplib import HTTPConnection as http_connection

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
        self.server_addr = server_addr 
        self.name = name
        self.serializer = serializer

        self.watchers = []

    def register(self):
        # if the server goes away or loses our registration,
        # we should try again
        ret =  rest_call(self.server_addr, 'register/', 'POST',
                         self.serializer,
                         { 'name':self.name, 
                           'pid':getpid(),
                           'host':gethostname() })
        
        if ret != 200, 'OK':
            #check for name conflict and reregister if need be
            exit(2)

    def _run(self):
        self.register()
        while True:
            feeds = self.get_feeds()
            for feed in feeds: 
                feed = feed_watcher(feed, self.server_addr) 
                feed.spawn()
                feed.start()
            if not feeds:
                sleep(30)



def rest_call(host, path, method, serializer, values = None):
    if values:
        values = urlencode(values)
    con = http_connection(server_addr)

    cryptkey = serializer.dumps(urandom(8))
    con.request(method, '/fetch/' + path + '?key=' + cryptkey, values)

    response = con.getresponse()

    if response.status == 200:
        data = loads(response.data)
    else: 
        raise Exception('blar')
    return response

# global for ease of use.
serializer = None

def main():
    global serializer 

    name = 'fetcher' + str(randint(100, 9999))

    cfg = load(open('fetch.cfg'))

    server_addr = cfg['server_addr']

    serializer = url_serializer(cfg['key'])

    get_logger().name = name
    get_logger().set_level(cfg['log_level'])

    fg = feed_getter(server_addr, name, serializer)
    fg.spawn()
    fg.join()

    

if __name__ == '__main__':
    main()

