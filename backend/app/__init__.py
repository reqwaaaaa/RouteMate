from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from celery import Celery
from backend.config import Config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
celery = Celery()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化数据库和JWT
    db.init_app(app)
    jwt.init_app(app)

    # 注册蓝图
    from backend.app.auth.auth_routes import auth_bp
    from backend.app.track.track_routes import track_bp
    from backend.app.recommendations.recommendations_routes import recommendations_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(track_bp, url_prefix='/track')
    app.register_blueprint(recommendations_bp, url_prefix='/recommendations')

    # Celery 配置
    make_celery(app)

    return app


def make_celery(app):
    """
    创建并配置 Celery 实例，绑定 Flask 应用上下文。
    """
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND']
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# 初始化 Flask app 和 Celery
app = create_app()
migrate = Migrate(app, db)
