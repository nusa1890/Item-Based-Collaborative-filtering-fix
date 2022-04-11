import os

from flask import Flask, request, session
from flask import render_template
from flask_babel import Babel, gettext

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
        )

    # change babel defaults
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    babel = Babel(app)


    @babel.localeselector
    def get_locale():
        if request.args.get('lang'):
            session['lang'] = request.args.get('lang')
        return session.get('lang', 'en')

        #return request.accept_languages.best_match(['en', 'es', 'de'])

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return render_template('../index.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    from . import language
    app.register_blueprint(language.bp)

    from . import recommender
    app.register_blueprint(recommender.bp)


    # this is index hence this is where the movie recommendations will go?
    app.add_url_rule('/', endpoint = 'index')

    # adding movies you have watched will be add /watched ?

    return app


