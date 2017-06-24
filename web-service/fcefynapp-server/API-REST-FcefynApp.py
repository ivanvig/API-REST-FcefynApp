import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, make_response, current_app, jsonify
from datetime import datetime, timedelta
from functools import update_wrapper


class Publicacion(object):                                  # TODO: Limitar setters

    def __init__(self):
        self._id = None
        self._title = None
        self._content = None
        self._fecha = None

    def loadfromdb(self, idd):
        db = get_db()
        cur = db.execute('SELECT title, content, fecha FROM PUBLICACIONES WHERE id == ?', (idd,))
        entries = cur.fetchall()
        entry = entries[0]
        self.setid(idd)
        self.settitle(entry['title'])
        self.setcontent(entry['content'])
        self.setfecha(entry['fecha'])

    def loadfromjson(self, json):
        pub = json['publicacion']
        self.settitle(pub.get('title', self.gettitle()))
        self.setcontent(pub.get('content', self.getcontent()))
        self.setfecha(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def getjson(self):
        return jsonify(publicacion=dict(id=self.getid(), title=self.gettitle(), content=self.getcontent(), fecha=self.getfecha()))

    def saveintodb(self):
        db = get_db()
        cur = db.execute('INSERT INTO PUBLICACIONES (title, content, fecha) VALUES (?,?,?)', (self.gettitle(), self.getcontent(), self.getfecha()))
        self.setid(cur.lastrowid)
        db.commit()

    def deletefromdb(self):
        db = get_db()
        db.execute('DELETE FROM PUBLICACIONES WHERE id == ?', (self.getid(),))
        db.commit()

    def updatedb(self):
        db = get_db()
        db.execute('UPDATE PUBLICACIONES SET title = ?, content = ?, fecha = ? WHERE id == ?', (self.gettitle(), self.getcontent(), self.getfecha(), self.getid()))
        db.commit()

    def settitle(self, title):
        self._title = title

    def setcontent(self, content):
        self._content = content

    def setfecha(self, fecha):
        self._fecha = fecha

    def setid(self, idd):
        self._id = idd

    def gettitle(self):
        return self._title

    def getcontent(self):
        return self._content

    def getfecha(self):
        return self._fecha

    def getid(self):
        return self._id


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '../database/fcefynapp.db'),
    KEY='dev',
    USERNAME='admin',
    PASSWORD='pass'
))
app.config.from_envvar('FCEFYNAPP_SETTINGS', silent=True)


def connect_db():
    """Conexion con la db"""

    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('DB inicializada')


def get_db():

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


"""
                CODIGO PARA CROSSDOMAIN
                
            http://flask.pocoo.org/snippets/56/
"""


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/publicaciones/', methods=['GET'])
@crossdomain(origin='*')
def get_allpub():
    db = get_db()
    cur = db.execute('SELECT id, title FROM PUBLICACIONES ORDER BY ID DESC')
    entries = cur.fetchall()
    return jsonify(publicaciones=dict(publicacion=[dict(id=entry['id'], title=entry['title']) for entry in entries]))


@app.route('/publicaciones/<int:publicacion_id>/', methods=['GET'])
@crossdomain(origin='*')
def get_publicacion(publicacion_id):
    pub = Publicacion()
    pub.loadfromdb(publicacion_id)
    return pub.getjson()


@app.route('/publicaciones/', methods=['POST'])
def crear_publicacion():                                                              # TODO: implementar seguridad
    if not request.is_json():
        abort(400)

    pub = Publicacion()
    pub.loadfromjson(request.get_json())
    pub.saveintodb()

    return pub.getjson(), 201


@app.route('/publicaciones/<int:publicacion_id>/', methods=['DELETE'])
def delete_publicacion(publicacion_id):                                             # TODO: implementar seguridad
    pub = Publicacion()
    pub.loadfromdb(publicacion_id)
    pub.deletefromdb()

    return pub.getjson()


@app.route('/publicaciones/<int:publicacion_id>', methods=['PUT'])
def modify_publicacion(publicacion_id):                                            # TODO: implementar seguridad
    if not request.is_json:
        abort(404)

    pub = Publicacion()
    pub.loadfromdb(publicacion_id)
    pub.loadfromjson(request.get_json())
    pub.updatedb()

    return pub.getjson()

