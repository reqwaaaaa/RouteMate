import os
from datetime import timedelta


class Config:
    # 从环境变量中获取密钥，如果环境变量未设置，程序将抛出异常
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # 可选：如果你希望程序在环境变量未设置时抛出更明显的错误，你可以进行手动检查：
    if not SECRET_KEY or not SQLALCHEMY_DATABASE_URI or not JWT_SECRET_KEY:
        raise ValueError("必须设置 SECRET_KEY, SQLALCHEMY_DATABASE_URI, 和 JWT_SECRET_KEY 环境变量")

    # JWT 配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 设置 Access Token 的过期时间为 1 小时
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 设置 Refresh Token 的过期时间为 30 天

    # Celery 配置
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # Redis 配置（如果使用 Redis 来存储会话或其他缓存）
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # 其他可选配置
    DEBUG = os.getenv('FLASK_DEBUG', False)
