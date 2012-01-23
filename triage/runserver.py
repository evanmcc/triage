from site import app as site_app
from feedsync import app as fs_app
from site import 

site_app.run(debug=True)
fs_app.run(debug=True)

