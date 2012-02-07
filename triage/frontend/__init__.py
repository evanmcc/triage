
from flask import Flask, request, session, url_for, redirect, abort, g, \
    make_response, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = '\xa5\x07\xa8\xd4\x9f\x9e\xcd]r%\xe1\x88Va\xbdB\r"\x06\xe6;\x11\x18\x9f'
from .view import splash
#from .ajax import news_item, login_chunk, user_status

