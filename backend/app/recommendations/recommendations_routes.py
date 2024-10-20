from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.track.models import Trajectory
from backend.app.auth.models import User
from backend.app.recommendations.models import Recommendation
from backend.scripts.NDTTJ import NDTTJ
from backend.scripts.NDTTT import NDTTT
from backend.scripts.TTHS import TTHS
from backend.app import db
import json
from datetime import datetime, timedelta
from geopy.distance import geodesic

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
        return 'TTHS'  # 高密度/长轨迹序列


def compute_similarity(hotspots1, hotspots2, time_threshold=timedelta(minutes=5), distance_threshold=100):
    """
    计算两个用户的热点轨迹之间的相似度，考虑相同时间下的经纬度相似度。

    参数：
    - hotspots1, hotspots2: 两个用户的热点轨迹列表，每个元素是一个轨迹路径（列表），路径由轨迹点（字典）组成。
    - time_threshold: 时间差阈值，只有在时间差小于该阈值的情况下，才认为是时间匹配的点。
    - distance_threshold: 距离阈值（米），用于判断空间上的相似性。

    返回：
    - similarity: 相似度，范围在 [0, 1] 之间。
    """
    if not hotspots1 or not hotspots2:
        return 0

    # 将所有热点轨迹点展开，并按照时间排序
    points1 = []
    for path in hotspots1:
        for point in path:
            timestamp = point['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            points1.append({
                'lat': point['lat'],
                'lon': point['lon'],
                'timestamp': timestamp
            })
    points1.sort(key=lambda x: x['timestamp'])

    points2 = []
    for path in hotspots2:
        for point in path:
            timestamp = point['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            points2.append({
                'lat': point['lat'],
                'lon': point['lon'],
                'timestamp': timestamp
            })
    points2.sort(key=lambda x: x['timestamp'])

    # 开始匹配
    index1 = 0
    index2 = 0
    matched_count = 0
    total_matched = 0

    while index1 < len(points1) and index2 < len(points2):
        time_diff = abs(points1[index1]['timestamp'] - points2[index2]['timestamp'])
        if time_diff <= time_threshold:
            # 时间匹配，计算空间距离
            coord1 = (points1[index1]['lat'], points1[index1]['lon'])
            coord2 = (points2[index2]['lat'], points2[index2]['lon'])
            distance = geodesic(coord1, coord2).meters
            if distance <= distance_threshold:
                matched_count += 1
            total_matched += 1
            index1 += 1
            index2 += 1
        elif points1[index1]['timestamp'] < points2[index2]['timestamp']:
            index1 += 1
        else:
            index2 += 1

    # 防止除以零
    if total_matched == 0:
        return 0

    similarity = matched_count / total_matched
    return similarity


@recommendations_bp.route('/carpool', methods=['GET'])
@jwt_required()
def get_carpool_recommendations():
    user_id = get_jwt_identity()

    # 获取当前用户的轨迹数据
    user_trajectories = Trajectory.query.filter_by(user_id=user_id).all()
    if not user_trajectories:
        return jsonify({'message': 'No trajectories found for the user'}), 404

    # 提取并解析用户的轨迹数据
    user_trajectory_data = [json.loads(traj.trajectory_data) for traj in user_trajectories]

    # 确定要使用的算法
    selected_algorithm = determine_algorithm(user_trajectories)

    # 根据选择的算法运行热点分析
    if selected_algorithm == 'NDTTJ':
        hotspots = NDTTJ(user_trajectory_data, kmin=4, mmin=2)
    elif selected_algorithm == 'NDTTT':
        hotspots = NDTTT(user_trajectory_data, kmin=4, mmin=2)
    else:
        hotspots = TTHS(user_trajectory_data, kmin=4, mmin=2)

    # 查找轨迹相似的用户
    similar_users = []
    similarity_threshold = 0.5  # 设置相似度阈值

    for other_user in User.query.all():
        if other_user.id != user_id:
            other_user_trajectories = Trajectory.query.filter_by(user_id=other_user.id).all()
            if not other_user_trajectories:
                continue

            other_user_trajectory_data = [json.loads(traj.trajectory_data) for traj in other_user_trajectories]

            # 确定其他用户要使用的算法
            other_user_algorithm = determine_algorithm(other_user_trajectories)

            # 根据确定的算法运行热点分析
            if other_user_algorithm == 'NDTTJ':
                other_user_hotspots = NDTTJ(other_user_trajectory_data, kmin=4, mmin=2)
            elif other_user_algorithm == 'NDTTT':
                other_user_hotspots = NDTTT(other_user_trajectory_data, kmin=4, mmin=2)
            else:
                other_user_hotspots = TTHS(other_user_trajectory_data, kmin=4, mmin=2)

            # 计算热点轨迹之间的相似度，考虑时间同步
            similarity = compute_similarity(hotspots, other_user_hotspots)

            if similarity >= similarity_threshold:
                similar_users.append({
                    'id': other_user.id,
                    'username': other_user.username,
                    'similarity': similarity
                    # 可以添加其他个人信息，如用户自定义的个人信息
                })

    # 存储推荐结果
    recommendation_data = {
        'similar_users': similar_users,
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
