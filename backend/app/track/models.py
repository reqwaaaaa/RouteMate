from backend.app import db


class Trajectory(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trajectory_data = db.Column(db.JSON, nullable=False)  # 使用JSON格式存储轨迹数据
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class HotspotTrajectory(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotspot_data = db.Column(db.JSON, nullable=False)  # 使用JSON格式存储热点数据
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
