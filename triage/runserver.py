#!/usr/bin/env python

from site import app as site_app
from feedsync import app as fs_app

site_app.run(debug=True)
fs_app.run(debug=True)

