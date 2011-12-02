
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
        #poke it into the module 
        feedsync.users = users
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

        data = { 'title' : 'fooblog',
                 'alias' : 'fb',
                 'xml_url' : 'http://example.com/rss/',
                 'http_url' : 'http://example.com/',
                 'feed_type' : 'rss' }

        response = self.app.post('/feeds/evan/', data= data)
        assert response.status == '201 CREATED'
        


    def tearDown(self):
        con.drop_database(con.test)

if __name__ == "__main__":
    main()
