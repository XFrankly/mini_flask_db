from flask import Flask
import os
from __path__ import project_path, data_path

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    # app = connexion.App(__name__)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(data_path, "commp.sqlite"),    # default app.instance_path
        # SERVER_NAME="0.0.0.0:8881",
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        pass

    else:
        # load the test config if passed in
        app.config.update(test_config)
        # ensure the instance folder exists
    from commp.src import db
    db.init_app(app)
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    from commp.blog import blog
    from commp.blog import auth
    from commp.users import people
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)   # 如果不注册蓝图到app中，app就无法访问到 蓝图所在的所有路由
    app.register_blueprint(people.api)
    app.add_url_rule("/", endpoint="index")
    # app.add_url_rule("/summ", endpoint="summ")
    print(f"app config:{app.config}, run:{app.run}")
    return app


def run():
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    http_server = HTTPServer(WSGIContainer(create_app()))  # WSGIContainer less scalability  WSGIContainer 是同步接口，扩展性比较差
    http_server.listen(port=8889)   #
    IOLoop.instance().start()

if __name__ == '__main__':
    pass
    app = create_app()  # {"SERVER_NAME":"0.0.0.0:8881"}
    app.run(debug=True)
    # run()