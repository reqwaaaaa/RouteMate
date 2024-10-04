from backend.app import db

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommendation_data = db.Column(db.Text, nullable=False)  # 存储推荐数据
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
