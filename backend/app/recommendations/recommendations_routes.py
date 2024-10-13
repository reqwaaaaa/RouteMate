from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.track.models import Trajectory
from backend.app.auth.models import User
from backend.app.recommendations.models import Recommendation
from backend.scripts.NDTTJ import ndttj_algorithm
from backend.scripts.NDTTT import ndttt_algorithm
from backend.scripts.TTHS import tspmg_b_algorithm
from backend.app import db
import json

recommendations_bp = Blueprint('recommendations', __name__)

def determine_algorithm(trajectories):
    """
    根据轨迹数据的稀疏性或密集性选择合适的算法。
    """
    total_points = sum(len(json.loads(traj.trajectory_data)) for traj in trajectories)
    avg_points_per_trajectory = total_points / len(trajectories) if trajectories else 0

    # 简单阈值，区分稀疏与密集数据
    if avg_points_per_trajectory < 5:
        return 'NDTTJ'  # 稀疏数据
    elif avg_points_per_trajectory <= 20:
        return 'NDTTT'  # 中等密集度数据
    else:
        return 'TSPMG_B'  # 高密度/长轨迹序列

@recommendations_bp.route('/carpool', methods=['GET'])
@jwt_required()
def get_carpool_recommendations():
    user_id = get_jwt_identity()

    # 获取当前用户的轨迹数据
    user_trajectories = Trajectory.query.filter_by(user_id=user_id).all()
    if not user_trajectories:
        return jsonify({'message': 'No trajectories found for the user'}), 404

    # 确定要使用的算法
    selected_algorithm = determine_algorithm(user_trajectories)

    # 根据选择的算法运行热点分析
    if selected_algorithm == 'NDTTJ':
        hotspots = ndttj_algorithm([json.loads(traj.trajectory_data) for traj in user_trajectories], freq_threshold=2, max_steps=4)
    elif selected_algorithm == 'NDTTT':
        hotspots = ndttt_algorithm([json.loads(traj.trajectory_data) for traj in user_trajectories], freq_threshold=2, max_steps=4)
    else:
        hotspots = tspmg_b_algorithm([json.loads(traj.trajectory_data) for traj in user_trajectories], freq_threshold=2, kmin=4)

    # 查找轨迹相似的用户
    similar_users = []
    for other_user in User.query.all():
        if other_user.id != user_id:
            other_user_trajectories = Trajectory.query.filter_by(user_id=other_user.id).all()
            if not other_user_trajectories:
                continue

            other_user_algorithm = determine_algorithm(other_user_trajectories)

            # 根据确定的算法运行热点分析
            if other_user_algorithm == 'NDTTJ':
                other_user_hotspots = ndttj_algorithm([json.loads(traj.trajectory_data) for traj in other_user_trajectories], freq_threshold=2, max_steps=4)
            elif other_user_algorithm == 'NDTTT':
                other_user_hotspots = ndttt_algorithm([json.loads(traj.trajectory_data) for traj in other_user_trajectories], freq_threshold=2, max_steps=4)
            else:
                other_user_hotspots = tspmg_b_algorithm([json.loads(traj.trajectory_data) for traj in other_user_trajectories], freq_threshold=2, kmin=4)

            # 直接比较列表内容，不使用哈希
            if hotspots == other_user_hotspots:
                similar_users.append(other_user)

    # 存储推荐结果
    recommendation_data = {
        'similar_users': [{'id': user.id, 'username': user.username} for user in similar_users],
        'user_hotspots': hotspots
    }

    # 将推荐结果存入 Recommendation 模型
    new_recommendation = Recommendation(
        user_id=user_id,
        recommendation_data=json.dumps(recommendation_data)
    )
    db.session.add(new_recommendation)
    db.session.commit()

    # 返回拼车推荐和用户热点
    return jsonify(recommendation_data)

@recommendations_bp.route('/poi', methods=['GET'])
@jwt_required()
def get_poi_recommendations():
    user_id = get_jwt_identity()

    # 获取当前用户的轨迹数据
    user_trajectories = Trajectory.query.filter_by(user_id=user_id).all()
    if not user_trajectories:
        return jsonify({'message': 'No trajectories found for the user'}), 404

    # 确定要使用的算法
    selected_algorithm = determine_algorithm(user_trajectories)

    # 根据选择的算法运行 POI 推荐
    if selected_algorithm == 'NDTTJ':
        poi_hotspots = ndttj_algorithm([json.loads(traj.trajectory_data) for traj in user_trajectories], freq_threshold=2, max_steps=4)
    elif selected_algorithm == 'NDTTT':
        poi_hotspots = ndttt_algorithm([json.loads(traj.trajectory_data) for traj in user_trajectories], freq_threshold=2, max_steps=4)
    else:
        poi_hotspots = tspmg_b_algorithm([json.loads(traj.trajectory_data) for traj in user_trajectories], freq_threshold=2, kmin=4)

    # 存储 POI 推荐结果
    new_poi_recommendation = Recommendation(
        user_id=user_id,
        recommendation_data=json.dumps(poi_hotspots)
    )
    db.session.add(new_poi_recommendation)
    db.session.commit()

    # 返回 POI 推荐结果
    return jsonify({
        'poi_hotspots': poi_hotspots
    })
