
from flask import Flask, request, session, url_for, redirect, abort, g, \
    make_response
from pymongo import Connection
from json import dumps


API_VERSION = 1

app = Flask(__name__)
app.config.from_object(__name__)

connection = Connection()

sync_db = connection.sync_db 
posts = sync_db.posts
# a note is a comment with public == False
comments = sync_db.comments
assertions = sync_db.assertions

user_db = connection.users 
users = user_db.users

@app.route('/')
def api_index():
    return 'API VERSION: %s \nAPI doc goes here' % API_VERSION

# add/delete feed subscription
@app.route('/feeds/<username>/')
@app.route('/feeds/<username>/<int:feed_id>', 
           methods = ['GET', 'POST', 'DELETE'])
def feed(username, feed_id = None): 
    """Feed support several methods:
     - GET: returns whether or not the user named is 
       subscribed to the feed"""
    if request.method == 'POST':
        # got a new feed to add, validate
        title = request.form.get('title')
        alias = request.form.get('alias')
        xml_url = request.form.get('xml_url')
        http_url = request.form.get('http_url')
        feed_type = request.form.get('feed_type')
        
        if not xml_url:
            abort(400)
        # if it doesn't exist in the global list, add it
        poss_matches = feeds.find({'xml_url':xml_url})
        
        if not poss_matches:
            # it's OK that some of these are None or blank, feedparser 
            # will fix it up for us in the background.
            new_feed = {'title':title, 'alias':alias, 'xml_url':xml_url, 
                        'http_url':http_url, 'feed_type':feed_type}
            new_feed_id = feeds.insert(new_feed)
            
        else:
            if len(poss_mathches) == 1:
                pass
            else:
                #can we try to resolve here?
                abort(404) #need to explain this in the docs
        # return the resource
        response = make_reponse('%s' % feed_id )
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass
    # otherwise we're in GET
    # eventually should add public/private feeds here

    if session.get('username') == username: 
        #you're you, so you can see your feeds
        if not feed_id: 
            #we just want a list
            user = users.find_one({'username':username})
            if not user:
                abort(401)

            return dumps(user['feeds'])
    else:
        abort(401)
    return 'foo'


# mark/unmark post as read

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
