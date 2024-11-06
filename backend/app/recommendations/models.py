from backend.app import db

class Recommendation(db.Model):
    __tablename__ = 'Recommendation'  # 确保与数据库表名一致

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    recommendation_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
