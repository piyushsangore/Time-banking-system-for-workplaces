from flask import Flask, redirect, url_for

from config import Config
from routes.auth_routes import auth_bp
from routes.task_routes import task_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config['SECRET_KEY']

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
