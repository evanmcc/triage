
import feedsync
from pymongo import Connection

from unittest import main, TestCase as test_case
from os import urandom

con = Connection()

class api_test(test_case):
    
    def setUp(self): 
        #nuke test db & recreate
        con.drop_database(con.test)
        users = con.test.users
        feeds = con.test.feeds
        comments = con.test.comments
        assertions = con.test.assertions

        #poke it into the module 
        feedsync.users = users
        feedsync.feeds = feeds
        feedsync.comments = comments
        feedsync.assertions = assertions

        feedsync.app.debug = True
        self.app = feedsync.app.test_client()
        users.insert({'username':'evan', 'password':'evanpass', 'feeds':[]})
        feedsync.app.secret_key = urandom(24)

    def login(self):
        self.app.post('/login', 
                      data = {'user':'evan', 
                              'pass':'evanpass'})
    def logout(self):
        self.app.get('/logout')



    def test_login(self):
        
        response = self.app.get('/login')
        assert response.status == '401 UNAUTHORIZED'
        response = self.app.post('/login', data = {'username':'evan'})
        assert response.status == '400 BAD REQUEST'

        response = self.app.post('/login', 
                                 data = {'user':'evan', 
                                         'pass':'wrong'})
        assert response.status == '401 UNAUTHORIZED'

        response = self.app.post('/login', 
                                 data = {'user':'nonuser', 
                                         'pass':'wrong'})
        assert response.status == '401 UNAUTHORIZED'

        response = self.app.post('/login', 
                                 data = {'user':'evan', 
                                         'pass':'evanpass'})
        assert response.status == '200 OK'

        response = self.app.get('/login')
        assert response.status == '200 OK'

    def test_logout(self):

        response = self.app.get('/logout')
        assert response.status == '200 OK'

        self.login()
        response = self.app.get('/login')
        assert response.status == '200 OK'

        response = self.app.get('/logout')
        assert response.status == '200 OK'

        response = self.app.get('/login')
        assert response.status == '401 UNAUTHORIZED'
        
    def test_feed(self):
        
        response = self.app.get('/feeds/evan/')
        assert response.status == '401 UNAUTHORIZED'

        self.login()

        response = self.app.get('/feeds/evan/')
        assert response.status == '200 OK'
        assert response.data == '[]'

        data1 = { 'title' : 'fooblog',
                  'alias' : 'fb',
                  'xml_url' : 'http://example.com/rss/',
                  'http_url' : 'http://example.com/',
                  'feed_type' : 'rss' }
        
        data2 = {'alias':"Jacob Kaplan-Moss - Writing",
                 'title':"Jacob Kaplan-Moss - Writing",
                 'feed_type':"rss",
                 'xml_url':"http://jacobian.org/feed/",
                 'html_url':"http://www.jacobian.org/writing/"}

        response = self.app.delete('/feeds/evan/1')
        assert response.status == '404 NOT FOUND'

        response = self.app.post('/feeds/evan/', data= data1)
        assert response.status == '201 CREATED'
        assert response.data == '1'

        response = self.app.post('/feeds/evan/', data = data2)
        assert response.status == '201 CREATED'
        assert response.data == '2'

        response = self.app.get('/feeds/evan/')
        assert response.status == '200 OK'
        assert response.data == '[1, 2]'

        response = self.app.delete('/feeds/evan/1')
        assert response.status == '200 OK'

        response = self.app.get('/feeds/evan/')
        assert response.status == '200 OK'
        assert response.data == '[2]'

        response = self.app.delete('/feeds/evan/blar')
        assert response.status == '404 NOT FOUND'

        response = self.app.delete('/feeds/evan/22')
        assert response.status == '404 NOT FOUND'


    def tearDown(self):
        con.drop_database(con.test)

if __name__ == "__main__":
    main()
