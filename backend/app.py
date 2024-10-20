from app import create_app, db, make_celery  # 从app模块导入create_app、db 和 make_celery
from flask_migrate import Migrate
from flask_cors import CORS
# from celery import Celery
# 初始化 Flask app
app = create_app()
CORS(app)  # 允许所有来源的CORS请求
# 初始化数据库迁移工具
migrate = Migrate(app, db)
db.init_app(app)
# 初始化 Celery 实例
celery = make_celery(app)

# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True)
