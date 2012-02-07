
from site import app, g, request, session, abort, \
    url_for, feed

@app.route('/')
def splash():
    return ''
