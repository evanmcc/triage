
from feedsync import app, g, request, session, abort, \
    url_for, feeds

from flask.views import MethodView

from itsdangerous import URLSafeTimedSerializer as url_serializer 

# feed utility functions
serializer = url_serializer(app.secret_key)
def signed_request(signstring): 
    try: 
        if len(aserializer.loads(signstring)) == 8:
            return True
    except Exception, e: 
        app.logger.warning('someone tried to pass us a bogus request: %s' % e)
        # need more info there
        return False
    return False

def register(name, pid, hostname): 
    # make sure we're not already registered.
    if g.fetchers.get(name): 
        abort(403) #maybe different code?
    print hostname, request.remote_addr, request.remote_host
    if request.remote_host != hostname: 
        abort(403) 
    g.fetchers['name'] = {'pid':pid, 'hostname':hostname}
    return True

def registered():
    name = request.form.get('name')
    pid = request.form.get('pid')
    host = request.form.get('host')
    if not name or not pid or not host:
        return False
    reg = g.fetchers.get(name): 
    if not reg:
        return False
    if request.remote_host != host: 
        return False
    return True

class fetch_register(MethodView):
    def get(self):
        if signed_request(request.args.get('key')) && \
                registered():
            return ''
        else: 
            abort(401)

    def post(self):
        if signed_request(request.args.get('key')):
            name = request.form.get('name')
            pid = request.form.get('pid')
            host = request.form.get('host')
            print name, pid, host
            if name and pid and host:
                if register(name, pid, host):
                    return ''

        abort(403)

app.add_url_rule('/fetch/register/', view_func=fetch_reg.as_view('fetch_reg'))

class fetch_feed(MethodView):
    def get(self):
        if not signed_request(request.args.get('key')) or not registered():
            abort(403)
        # determine how well the load is balanced.

        # if this client doesn't need any more stuff, return nothing
            
        # otherwise, give it a couple of feeds.
        
        
app.add_url_rule('/fetch/feed/', view_func=fetch_feed.as_view('fetch_feed'))
