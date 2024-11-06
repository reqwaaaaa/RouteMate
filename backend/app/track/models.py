from backend.app import db
import hashlib
import json


class Trajectory(db.Model):
    __tablename__ = 'Trajectory'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trajectory_data = db.Column(db.JSON, nullable=False)  # 使用JSON格式存储轨迹数据
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class HotspotTrajectory(db.Model):
    __tablename__ = 'HotspotTrajectory'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotspot_data = db.Column(db.JSON, nullable=False)  # 使用JSON格式存储热点数据
    hotspot_hash = db.Column(db.String(32), unique=True)  # 新增的hash字段，确保唯一性
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    @staticmethod
    def generate_hash(hotspot_data):
        """
        为热点数据生成唯一哈希值。
        """
        return hashlib.md5(json.dumps(hotspot_data, sort_keys=True).encode('utf-8')).hexdigest()
