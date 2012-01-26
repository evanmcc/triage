
from flask import Flask, request, session, url_for, redirect, abort, g, \
    make_response


app = Flask(__name__)
app.config.from_object(__name__)


# just putting this here so I can close some tabs
#from flaskext.bcrypt import bcrypt_init, generate_password_hash, check_password_hash

#bcrypt_init(app)

#pw_hash = generate_password_hash('secret')
#check_password_hash(pw_hash, 'secret')

from pymongo import Connection
from json import dumps

from itsdangerous import URLSafeTimedSerializer as url_serializer

API_VERSION = 1

testing = False

connection = Connection()
if testing:
    sync_db = connection.sync_db 

    posts = sync_db.posts
    comments = sync_db.comments
    assertions = sync_db.assertions
    feeds = sync_db.feeds

    user_db = connection.users 
    users = user_db.users
else: 
    connection.drop_database(connection.test)
    posts = connection.test.posts
    comments = connection.test.comments
    assertions = connection.test.assertions
    feeds = connection.test.feeds
    users = connection.test.users

from .feed import feed
from .fetch import fetch_feed, fetch_register

@app.route('/')
def api_index():
    return 'API VERSION: %s \nAPI doc goes here' % API_VERSION

# mark/unmark post as read
@app.route('/posts/<username>/<int:feed_id>', methods = ['GET'])
@app.route('/posts/<username>/<int:feed_id>/<int:post_id>', methods = ['GET', 'PUT'])
def posts(username, feed_id, post_id):

    user = users.find_one({'username':username})
    if session.get('username') != username or not user:
        abort(401)

    if request.method == GET:
        uf = user.get('feeds')
        if not uf:
            abort(404)
        global_feed = None
        for feed in uf:
            if feed_id == feed['feed_id']:
                global_feed = feed['glbal_id']
                break
        if not global_id:
            abort(404)
        #if post_id:
         #   reutrn post info
        #else:
         #   return a list of post
        

    return ''


# mark all feed posts as read

# add comment to post

# add fact to post

# affirm/refute/comment on(?) an assertion

# add info to comment: abusive, metoo, suspicious

# import/export OPML
@app.route('/import', methods = ['GET', 'POST'])
def import_opml():
    if request.method == 'GET': 
        user = session.get('username')
        if not user:
            abort(401)

# login/log out
@app.route('/login', methods = ['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        user = request.form.get('user') 
        pw   = request.form.get('pass') 

        if user and pw:
            user_obj = users.find_one({'username':user})
            if not user_obj:
                abort(401)
            if user_obj['password'] == pw:
                #this should time out ?
                try:
                    session['username'] = user
                    session.permanent = True
                except Exception, e:
                    print e
                return ''
            else: 
                abort(401)
        else:
            abort(400)
    else:
        if session.get('username'): 
            return ''
        else:
            abort(401)
            
    abort(400)
        
@app.route('/logout')
def logout():
    if session.get('username'):
        session.pop('username')
    return ''

def main():
    # for development. for deployment, read from config file
    app.secret_key = '`V\x1db[|d|\xeb?\x18\x03\x13ewUQ@\xeb\xda\xa4\xfe\xf3\x08'
    app.debug = True
    print 'starting'
    app.run()

if __name__ == '__main__':
    main()
