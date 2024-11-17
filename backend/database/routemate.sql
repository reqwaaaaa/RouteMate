-- 创建数据库
CREATE DATABASE IF NOT EXISTS RouteMate;
USE RouteMate;

-- 用户表 (User)
CREATE TABLE IF NOT EXISTS User
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(255) NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phone_number  VARCHAR(15)
);

-- 轨迹表 (Trajectory)
CREATE TABLE IF NOT EXISTS Trajectory
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT  NOT NULL,
    trajectory_data JSON NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (id) ON DELETE CASCADE,
    CHECK (
        JSON_VALID(trajectory_data) AND
        JSON_CONTAINS_PATH(trajectory_data, 'all', '$.trajectory_id') AND
        JSON_CONTAINS_PATH(trajectory_data, 'all', '$.nodes[*].latitude') AND
        JSON_CONTAINS_PATH(trajectory_data, 'all', '$.nodes[*].longitude') AND
        JSON_CONTAINS_PATH(trajectory_data, 'all', '$.nodes[*].timestamp')
    )
);

-- 热点轨迹表 (HotspotTrajectory)
CREATE TABLE IF NOT EXISTS HotspotTrajectory
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT  NOT NULL,
    hotspot_data LONGTEXT NOT NULL, -- 修改数据类型为LONGTEXT
    hotspot_hash VARCHAR(255), -- 添加热点轨迹哈希字段
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (id) ON DELETE CASCADE,
    CHECK (
        JSON_VALID(hotspot_data) AND
        JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*][*].latitude') AND
        JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*][*].longitude')
    )
);

-- 为 HotspotTrajectory 表添加唯一索引，确保每个用户的热点数据唯一
CREATE UNIQUE INDEX idx_user_hotspot ON HotspotTrajectory (user_id, hotspot_hash);

-- 推荐结果表 (Recommendation)
CREATE TABLE IF NOT EXISTS Recommendation
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT  NOT NULL,
    recommendation_data TEXT NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (id) ON DELETE CASCADE
);

-- 删除 Trajectory 表中的所有数据
DELETE FROM Trajectory;

-- 删除 HotspotTrajectory 表中的所有数据
DELETE FROM HotspotTrajectory;
