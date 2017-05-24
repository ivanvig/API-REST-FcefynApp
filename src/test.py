from flask import Flask, jsonify

app = Flask(__name__)

ROOT_PATH = ''

noticias = [
    {
        'id': 1,
        'title': u'La ruta del dinero G',
        'description': u'Gopez Laston investigado por desvio de fondos de la UNC',
        'fecha': u'Antes'
    },
    {
        'id': 2,
        'title': u'Condena firme para Gopez',
        'description': u'Gopez Laston sentenciado a prision por aceptar dadivas',
        'fecha': u'Antes'
    }
]


@app.route(ROOT_PATH + '/')
def index():
    return 'Index'


@app.route(ROOT_PATH + '/noticias/', methods=['GET'])
def get_noticias():
    return jsonify({'noticias': [noticia['title'] for noticia in noticias]})
if __name__ == '__main__':
    app.run()


@app.route(ROOT_PATH + '/noticias/<int:noticia_id>', methods=['GET'])
def get_noticia(noticia_id):
    return jsonify({'noticias': [noticia for noticia in noticias if noticia['id'] == noticia_id]})
if __name__ == '__main__':
    app.run()
