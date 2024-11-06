from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
from backend.app.track.models import Trajectory
from backend.app.auth.models import User
from geopy.distance import geodesic

recommendations_bp = Blueprint('recommendations', __name__)


def compute_similarity(hotspots1, hotspots2, time_threshold=timedelta(minutes=5), distance_threshold=100):
    if not hotspots1 or not hotspots2:
        return 0

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

    index1 = 0
    index2 = 0
    matched_count = 0
    total_matched = 0

    while index1 < len(points1) and index2 < len(points2):
        time_diff = abs(points1[index1]['timestamp'] - points2[index2]['timestamp'])
        if time_diff <= time_threshold:
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

    if total_matched == 0:
        return 0

    similarity = matched_count / total_matched
    return similarity


@recommendations_bp.route('/recommendation/carpool', methods=['POST'])
@jwt_required()
def get_carpool_recommendations():
    user_id = get_jwt_identity()

    # 获取请求中的参数
    data = request.get_json()
    min_support = data.get('min_support', 2)
    min_length = data.get('min_length', 2)

    # 获取当前用户的热点数据
    user_trajectory = Trajectory.query.filter_by(user_id=user_id).first()
    if not user_trajectory or not user_trajectory.hotspot_data:
        return jsonify({"message": "No hotspot data found for the user"}), 404

    user_hotspots = json.loads(user_trajectory.hotspot_data)
    similarity_threshold = 0.5
    similar_users = []

    # 遍历数据库中的其他用户并计算相似度
    for other_user in User.query.filter(User.id != user_id).all():
        other_trajectory = Trajectory.query.filter_by(user_id=other_user.id).first()
        if not other_trajectory or not other_trajectory.hotspot_data:
            continue

        other_user_hotspots = json.loads(other_trajectory.hotspot_data)
        similarity = compute_similarity(user_hotspots, other_user_hotspots)

        if similarity >= similarity_threshold:
            similar_users.append({
                "id": other_user.id,
                "phone": other_user.phone,
                "email": other_user.email,
                "similarity": similarity
            })

    return jsonify({"similar_users": similar_users}), 200


@recommendations_bp.route('/recommendation/poi', methods=['POST'])
@jwt_required()
def get_poi_recommendations():
    user_id = get_jwt_identity()

    # 获取请求中的参数
    data = request.get_json()
    min_support = data.get('min_support', 2)
    min_length = data.get('min_length', 2)

    # 获取当前用户的热点数据
    user_trajectory = Trajectory.query.filter_by(user_id=user_id).first()
    if not user_trajectory or not user_trajectory.hotspot_data:
        return jsonify({"message": "No hotspot data found for the user"}), 404

    hotspots = json.loads(user_trajectory.hotspot_data)
    filtered_hotspots = []

    last_point = None
    for point in hotspots:
        if last_point:
            time_diff = abs(datetime.strptime(point['timestamp'], "%Y-%m-%d %H:%M:%S") -
                            datetime.strptime(last_point['timestamp'], "%Y-%m-%d %H:%M:%S")).total_seconds()
            distance = geodesic((point['lat'], point['lon']),
                                (last_point['lat'], last_point['lon'])).meters

            if time_diff > 300 or distance > 100:
                filtered_hotspots.append(point)
                last_point = point
        else:
            filtered_hotspots.append(point)
            last_point = point

    return jsonify({"filtered_hotspots": filtered_hotspots}), 200
