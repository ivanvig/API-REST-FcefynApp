import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, make_response, current_app, jsonify
from datetime import datetime, timedelta
from functools import update_wrapper

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database/fcefynapp.db'),
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
def get_noticias():
    db = get_db()
    cur = db.execute('SELECT id, title FROM PUBLICACIONES ORDER BY ID DESC')
    entries = cur.fetchall()
    return jsonify(publicaciones=dict(publicacion=[dict(id=entry['id'], title=entry['title']) for entry in entries]))


@app.route('/publicaciones/<int:publicacion_id>/', methods=['GET'])
@crossdomain(origin='*')
def get_noticia(publicacion_id):
    db = get_db()
    cur = db.execute('SELECT title, content FROM PUBLICACIONES WHERE id == ?', publicacion_id)
    entries = cur.fetchall()
    entries = entries[0]
    return jsonify(publicacion=dict(title=entries['title'], content=entries['content'], fecha=entries['fecha']))


@app.route('/publicaciones/', methods=['POST'])
def crear_noticia():                                                              # TODO: implementar seguridad
    if not request.json or 'title' not in request.json:
        abort(400)

    title = request.json['title']
    content = request.json['content']
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    db.execute('INSERT INTO PUBLICACIONES (title, content, fecha) VALUES (?,?,?)', [title, content, fecha])
    db.commit()
    return jsonify(publicacion=dict(title=title, content=content, fecha=fecha)), 201


@app.route('/publicaciones/<int:publicacion_id>/', methods=['DELETE'])
def delete_noticia(publicacion_id):                                             # TODO: implementar seguridad
    db = get_db()
    db.execute('DELETE FROM PUBLICACIONES WHERE id == ?', publicacion_id)
    db.commit()

    return jsonify(True)

# TODO: implementar modificar una publicacion