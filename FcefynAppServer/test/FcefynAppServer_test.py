import os
import FcefynAppServer
import unittest
import tempfile
import json
import flask

class FcefynAppServerTestCase(unittest.TestCase):

    def login(self, username, password):
        return self.app.post(
            '/login',
            data=FcefynAppServer.jsonify(usuario=dict(acc=username, pwd=password)),
            content_type='application/json'
        )

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    @staticmethod
    def filldb():
        db = FcefynAppServer.get_db()
        with FcefynAppServer.app.open_resource('../test/fixture.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

    def setUp(self):
        self.db_fd, FcefynAppServer.app.config['DATABASE'] = tempfile.mkstemp()
        FcefynAppServer.app.testing = True
        self.app = FcefynAppServer.app.test_client()
        with FcefynAppServer.app.app_context():
            FcefynAppServer.init_db()
            self.filldb()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(FcefynAppServer.app.config['DATABASE'])

    def test_get_publicacion(self):
        response = self.app.get('/publicaciones/2/')
        esperado = dict(publicacion=dict(id=2, title='test2', content='testing 2testing2', fecha='2017-06-24 13:49:22'))
        self.assertEqual(json.loads(response.get_data()), esperado)
        response = self.app.get('/publicaciones/22/')
        self.assertEqual(response.status_code, 404)

    def test_get_allpub(self):
        response = self.app.get('/publicaciones/')
        self.assertEqual(len(json.loads(response.get_data())['publicaciones']['publicacion']), 3)

    def test_login_logout(self):
        with self.app:
            response = self.app.post(
                '/login',
                data=json.dumps(dict(usuario=dict(acc='re', pwd='test'))),
                content_type='application/json'
            )
            self.assertTrue(not flask.session['logged_in'])
            self.assertTrue(json.loads(response.get_data())['logged'])


if __name__ == '__main__':
    unittest.main()
