
from feedsync import app, request, session, abort, \
    url_for, redirect, make_response, users, feeds, dumps

from flask.views import MethodView

# feed utility functions
def add_feed_to_master_list(feed):
    candidates = [ x for x in feeds.find({'xml_url':feed['xml_url']})]
    if len(candidates) == 0:
        #add a new thing
        feed['subscribers'] = 1
        feed['new'] = True
        gfid = feeds.insert(feed)
    elif len(candidates) == 1:
        gfid = candidates[0]['id']
        #increment 
    else: 
        abort(406) #need a better code here
    return gfid 

def add_feed_to_user(user, global_id):
    uf = user.get('feeds')
    if not uf:
        user['feeds'] = []
        user['next_id'] = 2
        res = 1
    else:
        res = user['next_id']
        user['next_id'] += 1

    user['feeds'].append({'feed_id':res, 'global_id':global_id})
    users.save(user)
       
    return res

class feed(MethodView):
    def user_validate(self, username): 
        user = users.find_one({'username':username})
        if session.get('username') != username or not user:
            abort(401)
        return user

    def get(self, username, feed_id = None):
        user = self.user_validate(username)
        if not feed_id: 
        #we just want a list
            return dumps([ x['feed_id'] for x in user['feeds'] ])
        else:
            return '' #dumps(user[feeds        pass

    def post(self, username, feed_id = None):  
        user = self.user_validate(username)
        # got a new feed to add, validate
        title = request.form.get('title')
        alias = request.form.get('alias')
        xml_url = request.form.get('xml_url')
        http_url = request.form.get('http_url')
        feed_type = request.form.get('feed_type')
        
        if not xml_url:
            abort(400)
        
        # it's OK that some of these are None or blank, feedparser 
        # will fix it up for us in the background.
        new_feed = {'title':title, 'alias':alias, 'xml_url':xml_url, 
                    'http_url':http_url, 'feed_type':feed_type}

        global_feed_id = add_feed_to_master_list(new_feed)
        if not global_feed_id:
            abort(500) #need to explain this in the docs
        user_feed_id = add_feed_to_user(user, global_feed_id)

        # return the resource
        return '%s' % user_feed_id, 201

    def delete(self, username, feed_id = None): 
        user = self.user_validate(username)
        if not feed_id:
            abort(400)
        uf = user.get('feeds')
        if not uf: 
            abort(404)
        removed = False
        for i, feed in enumerate(uf):
            if feed['feed_id'] == int(feed_id):
                del uf[i]
                removed = True
        if not removed: 
            abort(404)
        users.save(user)
        return ''

app.add_url_rule('/feeds/<username>/', view_func=feed.as_view('feed'))
app.add_url_rule('/feeds/<username>/<int:feed_id>', view_func=feed.as_view('feed_w_id'))
