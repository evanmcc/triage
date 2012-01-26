
from feedsync import app, g, request, session, abort, \
    url_for, feeds

from flask.views import MethodView

from itsdangerous import URLSafeTimedSerializer as url_serializer, \
    BadSignature

# feed utility functions
serializer = url_serializer("234jn13lk1jb4tgk4jg4kljgbq;lfasdFADFASDGj3rb3")
fetchers = {}


def signed_request(signstring): 
    print signstring
    try: 
        ret = serializer.loads(signstring, max_age=1.5)
        return ret
    except BadSignature, e: 
        app.logger.warning('someone tried to pass us a bogus request: %s' % e)
        # need more info there
        return False
    return False

def register(name, pid, hostname): 
    # make sure we're not already registered.
    if fetchers.get(name): 
        abort(403) #maybe different code?

    print hostname, request.remote_addr#, request.remote_host

    if request.remote_host != hostname: 
        abort(403) 
    fetchers['name'] = {'pid':pid, 'hostname':hostname}
    return True

def registered():
    name = request.form.get('name')
    pid = request.form.get('pid')
    host = request.form.get('host')
    if not name or not pid or not host:
        return False
    reg = fetchers.get(name)
    if not reg:
        return False
    if request.remote_host != host: 
        return False
    return True

class fetch_register(MethodView):
    def get(self):
        if signed_request(request.args.get('key')) and \
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

app.add_url_rule('/fetch/register/', view_func=fetch_register.as_view('fetch_register'))

class fetch_feed(MethodView):
    def get(self):
        if not signed_request(request.args.get('key')) or not registered():
            abort(403)
        # determine how well the load is balanced.

        # if this client doesn't need any more stuff, return nothing
            
        # otherwise, give it a couple of feeds.
        
        
app.add_url_rule('/fetch/feed/', view_func=fetch_feed.as_view('fetch_feed'))

