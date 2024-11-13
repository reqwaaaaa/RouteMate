from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
from backend.app.track.models import HotspotTrajectory
from backend.app.auth.models import User
from geopy.distance import geodesic
from scipy.spatial import KDTree
import numpy as np

recommendations_bp = Blueprint('recommendations', __name__)


def compute_similarity(hotspots1, hotspots2, distance_threshold=100):
    def create_kd_tree(points):
        """将路径点集构建为KDTree，以加速距离查询"""
        coords = [(point['latitude'], point['longitude']) for point in points]
        return KDTree(np.radians(coords))

    def calculate_min_distance(path1, path2_tree, distance_threshold):
        """计算路径1中的每个点到路径2的最小距离并过滤低于阈值的点"""
        matches = 0
        for point1 in path1:
            coord1 = (point1['latitude'], point1['longitude'])
            distance, _ = path2_tree.query(np.radians([coord1]), distance_upper_bound=np.radians(distance_threshold / 6371))  # 使用地球半径（6371 km）归一化
            if distance < distance_threshold / 6371:  # 转换为弧度
                matches += 1
        return matches

    total_matches = 0
    total_pairs = 0

    # 遍历每条路径，对比当前用户和其他用户的路径
    for path1 in hotspots1:
        path1_tree = create_kd_tree(path1)  # 创建KDTree加速距离计算
        for path2 in hotspots2:
            path2_tree = create_kd_tree(path2)  # 创建另一条路径的KDTree
            match_count1 = calculate_min_distance(path1, path2_tree, distance_threshold)
            match_count2 = calculate_min_distance(path2, path1_tree, distance_threshold)

            # 如果任意一侧匹配足够的点，视为路径相似
            if match_count1 > len(path1) * 0.5 or match_count2 > len(path2) * 0.5:  # 超过50%匹配则判为相似
                total_matches += 1
            total_pairs += 1

    similarity_score = total_matches / total_pairs if total_pairs > 0 else 0
    return similarity_score


@recommendations_bp.route('carpool', methods=['POST'])
@jwt_required()
def get_carpool_recommendations():
    user_id = get_jwt_identity()

    # 获取请求中的参数，提供默认空字典以避免 NoneType 错误
    data = request.get_json() or {}
    similarity_threshold = data.get('similarity_threshold', 0.7)  # 调整到合理默认值

    user_hotspot = HotspotTrajectory.query.filter_by(user_id=user_id).first()
    if not user_hotspot or not user_hotspot.hotspot_data:
        return jsonify({"message": "No hotspot data found for the user"}), 404

    # 限制用户热点轨迹数量为前30条
    user_hotspots = user_hotspot.hotspot_data[:30]

    similar_users = []
    highest_similarity_user = None
    highest_similarity_score = 0
    debug_info = []  # 用于存储调试信息

    # 遍历其他用户并计算相似度
    for other_user in User.query.filter(User.id != user_id).all():
        other_user_hotspot = HotspotTrajectory.query.filter_by(user_id=other_user.id).first()
        if not other_user_hotspot or not other_user_hotspot.hotspot_data:
            continue

        # 限制其他用户的热点轨迹数量为前30条
        other_user_hotspots = other_user_hotspot.hotspot_data[:30]
        similarity = compute_similarity(user_hotspots, other_user_hotspots)

        # 添加调试信息
        debug_info.append(f"User ID {other_user.id} similarity with current user: {similarity}")

        # 检查是否超过阈值
        if similarity >= similarity_threshold:
            similar_users.append({
                "id": other_user.id,
                "phone": other_user.phone_number,
                "email": other_user.email,
                "similarity": similarity
            })

        # 记录相似度最高的用户
        if similarity > highest_similarity_score:
            highest_similarity_score = similarity
            highest_similarity_user = {
                "id": other_user.id,
                "phone": other_user.phone_number,
                "email": other_user.email,
                "similarity": similarity
            }

    # 如果没有超过阈值的用户，则返回相似度最高的用户
    if not similar_users and highest_similarity_user:
        similar_users.append(highest_similarity_user)

    # 返回相似用户列表和调试信息
    return jsonify({"similar_users": similar_users, "debug_info": debug_info}), 200


@recommendations_bp.route('poi', methods=['POST'])
@jwt_required()
def get_poi_recommendations():
    user_id = get_jwt_identity()

    user_hotspot = HotspotTrajectory.query.filter_by(user_id=user_id).first()
    if not user_hotspot or not user_hotspot.hotspot_data:
        return jsonify({"message": "No hotspot data found for the user"}), 404

    # hotspots 数据已经是列表格式，直接使用即可
    hotspots = user_hotspot.hotspot_data
    filtered_hotspots = []

    # 判断热点路径数量
    if len(hotspots) <= 50:
        # 如果少于等于50条，不清洗直接返回
        filtered_hotspots = hotspots
    else:
        # 清洗热点轨迹，增大距离阈值以减少保留点数量
        distance_threshold = 200  # 调整清洗条件的距离阈值
        for path in hotspots:
            filtered_path = []
            last_point = None

            for point in path:
                current_point = {
                    "latitude": point['latitude'],
                    "longitude": point['longitude'],
                }

                if last_point:
                    distance = geodesic(
                        (current_point['latitude'], current_point['longitude']),
                        (last_point['latitude'], last_point['longitude'])
                    ).meters

                    # 如果距离大于distance_threshold则保留该点
                    if distance > distance_threshold:
                        filtered_path.append(current_point)
                        last_point = current_point
                else:
                    filtered_path.append(current_point)
                    last_point = current_point

            filtered_hotspots.append(filtered_path)

        # 如果清洗后的热点条数仍然多于50条，可以进一步减少
        while len(filtered_hotspots) > 50:
            filtered_hotspots = filtered_hotspots[:50]

    return jsonify({"filtered_hotspots": filtered_hotspots}), 200

