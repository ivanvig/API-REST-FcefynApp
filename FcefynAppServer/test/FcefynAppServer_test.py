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

    def sim_logged(self):
        with self.app as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True

    def setUp(self):
        self.db_fd, FcefynAppServer.app.config['DATABASE'] = tempfile.mkstemp()
        FcefynAppServer.app.config['SERVER_NAME'] = 'localhost'
        FcefynAppServer.app.testing = True
        self.app = FcefynAppServer.app.test_client()
        with FcefynAppServer.app.app_context():
            FcefynAppServer.init_db()
            self.filldb()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(FcefynAppServer.app.config['DATABASE'])

    def test_get_publicacion(self):
        '''
        Testea la funcion para rotornar una publicacion.
            ->OK: Se envia un id valido, devuelve el json de la pub correspondiente
            ->OK: Se envia un id invalido, devuelve codigo 404
        '''
        response = self.app.get('/publicaciones/2/')
        with FcefynAppServer.app.app_context():
            esperado = dict(
                publicacion=dict(
                    id=FcefynAppServer.public_id(2),
                    title='test2',
                    content='testing 2testing2',
                    fecha='2017-06-24 13:49:22'
                )
            )
        self.assertEqual(json.loads(response.get_data()), esperado)
        response = self.app.get('/publicaciones/22/')
        self.assertEqual(response.status_code, 404)

    def test_get_allpub(self):
        '''
        Testea la funcion para rotornar todas las publicaciones.
            ->OK: Se hace la peticion, se retorna la lista completa
        '''
        response = self.app.get('/publicaciones/')
        self.assertEqual(len(json.loads(response.get_data())['publicaciones']['publicacion']), 3)

    def test_login_logout(self):
        '''
        Testea las funciones login y logout.
            ->OK: Se recibe un json con datos correctos, se le da el estado de logeado en la sesion
            ->OK: Se recibe un json con datos correctos, se retorna un json con "logged" : True
            ->OK: Se hace la peticion para deslogear, se elimina el estado de logeado en la sesion
            ->OK: Se hace la peticion para deslogear, se retorna un json con "logged_out" : True
        '''
        with self.app:
            response = self.app.post(
                '/login/',
                data=json.dumps(dict(usuario=dict(acc='re', pwd='test'))),
                content_type='application/json'
            )
            self.assertTrue(flask.session['logged_in'])
        self.assertTrue(json.loads(response.get_data())['logged'])

        with self.app as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True

            response = c.get('/logout/')
            self.assertNotIn('logged_in', flask.session)
        self.assertTrue(json.loads(response.get_data())['logged_out'])

    def test_delete_publicacion(self):
        '''
        Testea la funcion para eliminar publicacion.
            ->OK: Se intenta eliminar sin estar logeado, retorna codigo 401
            ->OK: Se intenta eliminar estando logeado, se elimina y se retorna un json con la pub eliminada
        '''
        response = self.app.delete('/publicaciones/2/')
        self.assertEqual(response.status_code, 401)

        with self.app as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True
            response = self.app.delete('/publicaciones/2/')
            self.assertEqual(json.loads(response.get_data())['publicacion']['id'], FcefynAppServer.public_id(2))

    def test_modify_publicacion(self):
        '''
        Testea la funcion para modificar un publicacion
            ->OK: Se intenta modificar sin permisos, retorna 401
            ->OK: Se intenta modificar con un paquete invalido, retorna 400
            ->OK: Se intenta modificar con permisos, se modifica y se retorna un json con la pub modificada
        '''
        response = self.app.put(
            '/publicaciones/2/',
            data=json.dumps(dict(publicacion=dict(title='nuevo', content='nuevo content'))),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

        with self.app as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.app.put(
                '/publicaciones/2/',
                data=json.dumps('algo')
            )
            self.assertEqual(response.status_code, 400)

            response = self.app.put(
                '/publicaciones/2/',
                data=json.dumps('algo'),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

            response = self.app.put(
                '/publicaciones/2/',
                data=json.dumps(dict(publicacion=dict(title='nuevo', content='nuevo content'))),
                content_type='application/json'
            )
            self.assertEqual(json.loads(response.get_data())['publicacion']['id'], FcefynAppServer.public_id(2))

    def test_crear_publicacion(self):
        '''
        Testea la funcion para crear un publicacion
            ->OK: Se intenta crear sin permisos, retorna 401
            ->OK: Se intenta crear con un paquete invalido, retorna 400
            ->OK: Se intenta crear con permisos, se crea y se retorna un json con la pub creada
        '''
        response = self.app.post(
            '/publicaciones/',
            data=json.dumps(dict(publicacion=dict(title='nuevo', content='nuevo content'))),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

        with self.app as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True

            response = self.app.post(
                '/publicaciones/',
                data=json.dumps('algo')
            )
            self.assertEqual(response.status_code, 400)

            response = self.app.post(
                '/publicaciones/',
                data=json.dumps('algo'),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

            response = self.app.post(
                '/publicaciones/',
                data=json.dumps(dict(publicacion=dict(title='nuevo', content='nuevo content'))),
                content_type='application/json'
            )
            self.assertEqual(json.loads(response.get_data())['publicacion']['id'], FcefynAppServer.public_id(4))


if __name__ == '__main__':
    unittest.main()
