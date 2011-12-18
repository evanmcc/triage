
from flask import Flask, request, session, url_for, redirect, abort, g, \
    make_response


app = Flask(__name__)
app.config.from_object(__name__)


from .view import splash
from .ajax import news_item, login_chuck, user_status
