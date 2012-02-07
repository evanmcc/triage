from frontend import app, g, request, session, abort, \
    url_for

from pymongo import Connection

@app.route('/ajax/')
def splash():
    return ''
