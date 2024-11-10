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

-- DROP TABLE IF EXISTS Trajectory;
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

-- DROP TABLE IF EXISTS HotspotTrajectory;
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


-- 后续修改：

-- 排除重复热点轨迹数据
ALTER TABLE HotspotTrajectory
    ADD COLUMN hotspot_hash VARCHAR(32);
CREATE UNIQUE INDEX idx_user_hotspot ON HotspotTrajectory (user_id, hotspot_hash);
-- 移除原有的 CHECK 约束
ALTER TABLE HotspotTrajectory
    DROP CHECK hotspottrajectory_chk_1;
-- 重新添加不包含 'hotspot_level' 的新 CHECK 约束
ALTER TABLE HotspotTrajectory
    ADD CONSTRAINT hotspottrajectory_chk_1
        CHECK (
            JSON_VALID(hotspot_data) AND
            JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*].latitude') AND
            JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*].longitude') AND
            JSON_CONTAINS_PATH(hotspot_data, 'all', '$[*].timestamp')
            );

-- 删除原始轨迹数据表中所有数据
DELETE FROM Trajectory;



