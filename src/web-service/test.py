from flask import Flask, jsonify, request, abort, make_response, current_app
from datetime import datetime, timedelta
from functools import update_wrapper

app = Flask(__name__)

ROOT_PATH = ''

noticias = [
    {
        'id': 1,
        'title': u'La ruta del dinero G',
        'description': u'Gopez Laston investigado por desvio de fondos de la UNC, luego de una larga investigacion en la que participaron'
                       u'unidiades de la PFA, FPA y el grupo HALCON se allanaron hoy las oficinas del señor Gopez y se encontraron documentos'
                       u'compremetedores que demostrarian un desvio de fondo y un vaciamiento de las arcas de la FCEFyN',
        'fecha': u'Antes'
    },
    {
        'id': 2,
        'title': u'Condena firme para Gopez',
        'description': u'Gopez Laston sentenciado a 20 años de prision por delitos de corrupcion, ademas el Juez impuso un embargo de U$20.000',
        'fecha': u'Ahora'
    }
]

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


@app.route(ROOT_PATH + '/')
@crossdomain(origin='*')
def index():
    return jsonify({'lugar': 'index'})


@app.route(ROOT_PATH + '/noticias/', methods=['GET'])
@crossdomain(origin='*')
def get_noticias():
    return jsonify({'titulos': [{'id': noticia['id'], 'title': noticia['title']} for noticia in noticias]})


@app.route(ROOT_PATH + '/noticias/<int:noticia_id>', methods=['GET'])
@crossdomain(origin='*')
def get_noticia(noticia_id):
    return jsonify({'noticia': [noticia for noticia in noticias if noticia['id'] == noticia_id][0]})


@app.route(ROOT_PATH + '/noticias/', methods=['POST'])
def crear_noticia():
    if not request.json or 'title' not in request.json:
        abort(400)

    noticia = {
                'id': noticias[-1]['id'] + 1,
                'title': request.json['title'],
                'description': request.json['description'],
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    noticias.append(noticia)

    return jsonify(noticia), 201


@app.route(ROOT_PATH + '/noticias/<int:noticia_id>', methods=['DELETE'])
def delete_noticia(noticia_id):
    toremove = [noticia for noticia in noticias if noticia['id'] == noticia_id]
    if not len(toremove):
        abort(404)

    noticias.remove(toremove[0])

    return jsonify(True)


@app.router(ROOT_PATH + '/noticias/<int:noticia_id>', methods=['PUT'])
def modify_noticia(noticia_id):
    noticia = [noticia for noticia in noticias if noticia['id'] == noticia_id][0]
    if not len(noticia) or not request.json:        # AGREGAR MAS COSAS ACA, VER EN PAGINA
        abort(404)

    noticia['title'] = request.json.get('title', noticia['title'])
    noticia['description'] = request.json.get('description', noticia['description'])
    noticia['fecha'] = request.json.get('fecha', noticia['fecha'])


if __name__ == '__main__':
    app.run()
