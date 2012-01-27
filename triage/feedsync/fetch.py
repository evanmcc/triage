
from feedsync import app, g, request, session, abort, \
    url_for, feeds

from flask.views import MethodView

from itsdangerous import URLSafeTimedSerializer as url_serializer, \
    BadSignature

from hashlib import sha256
from pymongo import Connection

# not sure this is thread-safe
serializer = url_serializer("234jn13lk1jb4tgk4jg4kljgbq;lfasdFADFASDGj3rb3")

fetchers = Connection().sync_db.fetchers

def signed_request(args, form): 
    #form = dict(form)
    signstring = args.get('key')

    #werkzeug does some weird value munging here, have to undo
    form = dict([ (x, y) for x, y in form.items() ])
    payload = sha256(repr(form)).hexdigest()

    try: 
        ret = serializer.loads(signstring, max_age=1.5)
        if payload == ret:
            return True
    except BadSignature, e: 
        app.logger.warning('someone tried to pass us a bogus request: %s' % e)
        # need more info there
        return False
    return False

def register(name, pid, addr): 
    

    # make sure we're not already registered.
    if fetchers.find_one({'name':name}): 
        app.log.warning('fetcher  %s already registered' % name)
        abort(403) #maybe different code?
    
    # we should also require that this is coming from the local subnet

    addr = addr.strip('http:/')
    if addr.find(':') != -1:
        addr = addr.split(':')[0]
    print request.remote_addr, addr     
    if request.remote_addr != addr: 
        abort(403) 
    fetchers.insert({'name':name, 'pid':pid, 'addr':addr})
    return True

def registered():
    name = request.args.get('name')

    reg = fetchers.find_one({'name':name})
    if not name or not reg:
        app.logger.debug('with %s, got %s' % (name, reg))
        return False

    if request.remote_addr != reg['addr']: 
        return False
    return True

class fetch_register(MethodView):
    def get(self):
        if signed_request(request.args, request.form) and \
                registered():
            return ''
        else: 
            abort(401)

    def post(self):
        if signed_request(request.args, request.form):
            name = request.form.get('name')
            pid = request.form.get('pid')
            addr = request.form.get('addr')

            if name and pid and addr:
                if register(name, pid, addr):
                    return ''

        abort(403)

app.add_url_rule('/fetch/register/', view_func=fetch_register.as_view('fetch_register'))

class fetch_feed(MethodView):
    def get(self):
        if not signed_request(request.args, request.form) or not registered():
            abort(403)
        # determine how well the load is balanced.

        # are there any unassigned feeds?
        unassigned = [ x for x in feeds.find({'cat':'unassigned'}) ]
        app.logger.debug('%s' % unassigned)
        if not unassigned: 
            return ''
        abort(401)
        # how many fetchers are alive?

        # how many feeds are there?

        # how many feeds are assigned to this fetcher?


        # if this client doesn't need any more stuff, return nothing
            
        # otherwise, give it a couple of feeds.
        
        
app.add_url_rule('/fetch/feed/', view_func=fetch_feed.as_view('fetch_feed'))

