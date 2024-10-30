-- CREATE DATABASE IF NOT EXISTS RouteMate;
-- DROP DATABASE routemate;
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
    -- JSON字段检查：确保包含经纬度和时间戳的数组格式
    CHECK (
        JSON_VALID(trajectory_data) AND
        JSON_CONTAINS_PATH(trajectory_data, 'all', '$[*].latitude') AND
        JSON_CONTAINS_PATH(trajectory_data, 'all', '$[*].longitude') AND
        JSON_CONTAINS_PATH(trajectory_data, 'all', '$[*].timestamp')
        )
);

-- 热点轨迹表 (HotspotTrajectory)
CREATE TABLE IF NOT EXISTS HotspotTrajectory
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT  NOT NULL,
    hotspot_data JSON NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (id) ON DELETE CASCADE,
    -- JSON字段检查：确保包含经纬度、时间戳和热点级别的数组格式
    CHECK (
        JSON_VALID(hotspot_data) AND
        JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*].latitude') AND
        JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*].longitude') AND
        JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*].timestamp') AND
        JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*].hotspot_level')
        )
);

-- 推荐结果表 (Recommendation)
CREATE TABLE IF NOT EXISTS Recommendation
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT  NOT NULL,
    recommendation_data TEXT NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (id) ON DELETE CASCADE
);
