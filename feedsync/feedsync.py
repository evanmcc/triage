
from flask import Flask, request, session, url_for, redirect, abort, g
from pymongo import Connection

app = Flask(__name__)
app.config.from_object(__name__)

connection = Connection()
db = connection.sync_db 
posts = db.posts
comments = db.comments
assertions = db.assertions

# add/delete feed subscription
@app.route('/<username>/feed/<int:feed_id>', 
           methods = ['GET', 'POST', 'PUT', 'DELETE'])
def sub(username, subid): 
    """Feed support several methods:
     - GET: returns whether or not the user named is 
       subscribed to the feed"""
    if request.method == 'POST':
        pass
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass
    # otherwise we're in GET
    pass

# mark/unmark post as read

# mark all feed posts as read

# add comment to post

# add fact to post

# affirm/refute/comment on(?) an assertion

# add info to comment: abusive, metoo, suspicious

# import/export OPML

# login/log out




def main():
    app.debug = False
    app.run()

if __name__ == ' __main__':
    main()
