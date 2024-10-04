
## RM后端模块详细分析

### 1. **Flask 应用初始化**

文件：`app/__init__.py`

- **功能**：初始化 Flask 应用，加载配置，注册数据库、JWT、CORS 等依赖项，并注册路由蓝图。
- **实现**：
  - 初始化 Flask 应用实例。
  - 配置数据库连接和 JWT。
  - 注册 `auth`, `recommendations`, `track` 模块的路由蓝图。

### 2. **用户认证模块**

目录：`/app/auth`

#### 文件：
- `auth_routes.py`：处理用户的注册和登录请求。
- `models.py`：定义用户模型，用于数据库交互。

#### 路由分析：
- **`POST /auth/register`**
  - **功能**：用户注册。
  - **请求数据**：
    ```json
    {
      "username": "user123",
      "password": "securePassword",
      "email": "user123@example.com"
    }
    ```
  - **响应数据**：
    ```json
    {
      "message": "User registered successfully",
      "user_id": 1
    }
    ```

- **`POST /auth/login`**
  - **功能**：用户登录，返回 JWT 令牌。
  - **请求数据**：
    ```json
    {
      "username": "user123",
      "password": "securePassword"
    }
    ```
  - **响应数据**：
    ```json
    {
      "message": "Login successful",
      "token": "eyJhbGciOiJIUzI1NiIsInR5..."
    }
    ```

### 3. **推荐系统模块**

目录：`/app/recommendations`

#### 文件：
- `recommendations_routes.py`：处理拼车推荐和 POI 推荐的路由。
- `models.py`：定义推荐结果的数据模型。

#### 路由分析：
- **`POST /recommendations/carpool`**
  - **功能**：根据用户轨迹推荐拼车伙伴。
  - **请求数据**：
    ```json
    {
      "user_id": 1,
      "trajectory_id": "traj123",
      "current_location": {
        "lat": 39.9042,
        "lon": 116.4074
      }
    }
    ```
  - **响应数据**：
    ```json
    {
      "recommendations": [
        {
          "user_id": 2,
          "similarity": 0.89,
          "name": "John Doe",
          "location": {
            "lat": 39.903,
            "lon": 116.408
          }
        },
        {
          "user_id": 3,
          "similarity": 0.72,
          "name": "Jane Smith",
          "location": {
            "lat": 39.905,
            "lon": 116.406
          }
        }
      ]
    }
    ```

- **`POST /recommendations/poi`**
  - **功能**：根据用户位置推荐 POI。
  - **请求数据**：
    ```json
    {
      "current_location": {
        "lat": 39.9042,
        "lon": 116.4074
      }
    }
    ```
  - **响应数据**：
    ```json
    {
      "poi_suggestions": [
        {
          "name": "Great Wall",
          "category": "Historical Site",
          "lat": 40.4322,
          "lon": 116.5704
        },
        {
          "name": "Forbidden City",
          "category": "Museum",
          "lat": 39.9163,
          "lon": 116.3972
        }
      ]
    }
    ```

### 4. **轨迹管理模块**

目录：`/app/track`

#### 文件：
- `track_routes.py`：处理轨迹上传、分析、历史查询。
- `models.py`：定义轨迹数据模型。

#### 路由分析：
- **`POST /track/upload`**
  - **功能**：上传用户轨迹数据。
  - **请求数据**：
    ```json
    {
      "user_id": 1,
      "trajectory_data": [
        {"lat": 39.9042, "lon": 116.4074, "timestamp": "2024-01-01T10:00:00Z"},
        {"lat": 39.9052, "lon": 116.4084, "timestamp": "2024-01-01T10:05:00Z"}
      ]
    }
    ```
  - **响应数据**：
    ```json
    {
      "message": "Trajectory uploaded successfully",
      "trajectory_id": "traj123"
    }
    ```

- **`POST /track/analyze`**
  - **功能**：分析上传的轨迹，识别出热点区域。
  - **请求数据**：
    ```json
    {
      "trajectory_id": "traj123"
    }
    ```
  - **响应数据**：
    ```json
    {
      "hotspots": [
        {"lat": 39.9042, "lon": 116.4074, "weight": 0.8},
        {"lat": 39.9052, "lon": 116.4084, "weight": 0.7}
      ]
    }
    ```

- **`GET /track/history`**
  - **功能**：获取用户的历史轨迹。
  - **响应数据**：
    ```json
    {
      "trajectories": [
        {
          "trajectory_id": "traj123",
          "points": [
            {"lat": 39.9042, "lon": 116.4074, "timestamp": "2024-01-01T10:00:00Z"},
            {"lat": 39.9052, "lon": 116.4084, "timestamp": "2024-01-01T10:05:00Z"}
          ]
        }
      ]
    }
    ```

### 5. **轨迹分析算法模块**

目录：`/scripts`

#### 文件：
- `NDTTJ.py`：基于 N 度路径连接的轨迹分析算法。
- `NDTTT.py`：基于 N 度遍历的轨迹分析算法。
- `TSPMG_B.py`：基于深度优先搜索的频繁模式检测算法。

#### 功能：
- 这些脚本实现了不同的轨迹分析算法，用于分析用户上传的轨迹数据并识别热点或推荐路径。

### 6. **缓存模块**

文件：`app/cache.py`

- **功能**：缓存轨迹分析结果，提高分析效率，避免对同样的轨迹数据进行重复计算。

### 7. **数据库**

文件：`database/routemate.sql`

- **功能**：初始化数据库表，包括用户表、轨迹表、推荐结果表等。
- **表结构**：
  - **用户表**：存储用户的基本信息（用户名、邮箱、密码哈希等）。
  - **轨迹表**：存储用户的轨迹数据。
  - **推荐表**：存储推荐的拼车伙伴和 POI 结果。

### 8. **配置文件**

文件：`config.py`

- **功能**：配置数据库连接、JWT 认证、Celery 等重要配置。
- **配置项**：
  - 数据库 URI
  - JWT 秘钥和过期时间
  - Celery 任务队列配置

### 9. **Flask 应用入口**

文件：`app.py`

- **功能**：Flask 应用的入口文件，注册所有蓝图，并启动服务器。
- **依赖项**：包括 Flask、SQLAlchemy、JWT、CORS 等。




