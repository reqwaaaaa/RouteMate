#  [RouteMate](https://github.com/reqwaaaaa/Maybe-its-life/blob/main/%E8%BD%AF%E8%91%97%E8%AF%81%E4%B9%A6.pdf)

## 1. 项目概述

**RouteMate** 旨在为用户提供轨迹管理、热点轨迹挖掘、拼车服务与 POI 推荐功能。

### 主要功能
- 用户身份验证（基于 JWT）
- 轨迹数据的存储与管理
- 热点轨迹挖掘（NDTTJ、NDTTT、TTHS 算法）
- 拼车服务与 POI 推荐
- RESTful API 管理

### 技术栈
- 后端框架: Flask
- 数据库: MySQL
- 缓存: Redis
- 算法: NDTTJ、NDTTT、TTHS
- 身份验证: JWT

## 2. 系统架构

### 框架设计
采用模块化设计，将不同功能划分为多个模块，包括认证模块、轨迹管理模块、推荐模块等。各模块通过 Flask 蓝图 (`Blueprint`) 实现功能的隔离和解耦。

### 数据库结构
- **User 表**: 存储用户的基础信息，包括用户名、邮箱、密码哈希等。
- **Trajectory 表**: 存储用户的轨迹数据，以 JSON 格式保存节点信息。
- **HotspotTrajectory 表**: 存储用户的热点轨迹，包含轨迹点的纬度和经度。

数据库中对 JSON 数据类型进行验证和约束，确保轨迹数据的完整性和一致性。

### 模块划分与功能关系
- **认证模块**: 负责用户的注册、登录、JWT 令牌生成与验证。
- **轨迹管理模块**: 实现轨迹数据的上传、存储、热点轨迹挖掘与管理。
- **推荐模块**: 提供拼车推荐与 POI 推荐服务，基于轨迹数据的挖掘结果。

## 3. 核心功能实现

### 用户身份验证
- 使用 Flask-JWT-Extended 实现用户登录、注册和身份验证。
- 令牌设置了 1 小时的过期时间，支持 Refresh Token 延长用户会话时长。
- 密码哈希使用 `werkzeug.security` 提供的安全加密方式。

### 热点轨迹挖掘
- 根据用户轨迹数量选择不同的算法进行热点挖掘：
  - **NDTTJ**: 适用于小于 50 条轨迹的数据，基于路径表合并的方法。
  - **NDTTT**: 处理 50 到 1000 条轨迹的数据，通过构建更长路径进行挖掘。
  - **TTHS**: 适用于超过 1000 条轨迹的数据，通过轨迹图的深度优先搜索挖掘热点。
  
[***挖掘算法说明***](https://github.com/reqwaaaaa/Maybe-its-life/blob/main/%E7%83%AD%E7%82%B9%E8%BD%A8%E8%BF%B9%E6%8C%96%E6%8E%98.md)

### 拼车推荐
- 使用 KDTree 对用户的热点轨迹数据进行相似度分析，找到与当前用户热点轨迹相似的其他用户。
- 通过 `/carpool` 接口返回拼车推荐列表，包括用户 ID、电话、邮箱等信息。

[***相似度分析说明***](https://github.com/reqwaaaaa/Maybe-its-life/blob/main/%E8%BD%A8%E8%BF%B9%E7%9B%B8%E4%BC%BC%E5%BA%A6%E5%88%86%E6%9E%90.md)

### POI 推荐
- 通过 `/poi` 接口对用户热点轨迹进行过滤，去除大量无关的密集轨迹点。
- 返回筛选后的 POI 节点位置，以便用户获取更直观、简洁的路线建议。

### API 设计与调用
- 项目采用 RESTful 风格的 API 设计，支持常用的 GET、POST 方法。
- 认证路由 (`/auth`)、轨迹管理路由 (`/track`)、推荐路由 (`/recommendations`) 之间相互独立。

## 4. 补充

### 热点轨迹挖掘算法逻辑
- **NDTTJ 算法**: 基于 N 度路径表的连接与合并，适合于处理规模较小的轨迹数据，效率高且占用内存小。
- **NDTTT 算法**: 通过构造更长的路径，提高轨迹挖掘的深度，适用于中等规模数据，能够有效捕获复杂热点。
- **TTHS 算法**: 采用轨迹图的构建与遍历，适合于大规模数据，能够在合理时间内找到高频次热点轨迹。

### 数据缓存与性能优化
- 使用 Redis 实现对热点数据和推荐结果的缓存，有效减少对数据库的频繁访问。
- 缓存设置了 1 小时的自动过期时间，以保证数据的时效性和新鲜度。

### 数据库优化与约束条件
- 对轨迹表中存储的 JSON 数据进行路径校验，确保轨迹点包含经纬度和时间戳等必要字段。
- 通过外键约束，保证用户和轨迹数据之间的完整性。

### 目录
```
/backend
├── /app
│   ├── __init__.py                    # Flask 应用初始化
│   ├── /auth                          # 用户认证模块
│   │   ├── __init__.py
│   │   ├── auth_routes.py             # 认证相关路由
│   │   └── models.py                  # 用户相关数据库模型
│   ├── /recommendations               # 推荐系统模块
│   │   ├── __init__.py
│   │   ├── recommendations_routes.py  # 拼车与 POI 推荐的路由
│   │   └── models.py                  # 推荐相关数据库模型
│   ├── /track                         # 轨迹管理模块
│   │   ├── __init__.py
│   │   ├── models.py                  # 轨迹数据相关数据库模型
│   │   ├── track_routes.py            # 轨迹相关路由
│   └── cache.py                       # 轨迹分析结果缓存模块，与 `auth` 平行
├── /database
│   └── routemate.sql                  # 数据库初始化 SQL 脚本
├── /scripts                           # 轨迹分析算法相关脚本
│   ├── __init__.py
│   ├── NDTTJ.py                       # NDTTJ 算法脚本
│   ├── NDTTT.py                       # NDTTT 算法脚本
│   └── TTHS.py                        # TTHS 算法脚本
├── app.py                             # Flask 应用入口文件
└── config.py                          # 配置文件（包含数据库、JWT、Celery 配置）
```

### 前端链接
  
[***Vue版本***](https://github.com/reqwaaaaa/RM_Vue)
[***Flutter版本***](https://github.com/reqwaaaaa/RouteMate_Front)

### 后续研究计划

[***Research on Frequent Pattern Mining Based on Hotspot Trajectories***](https://reqwaaaaa.github.io/Maybe-its-life/%E5%88%9B%E6%96%B0%E5%AE%9E%E9%AA%8C%E7%90%86%E8%AE%BA.html)
