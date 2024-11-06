from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from backend.scripts.NDTTJ import NDTTJ
from backend.scripts.NDTTT import NDTTT
from backend.scripts.TTHS import TTHS
from backend.app import db
from backend.app.track.models import Trajectory, HotspotTrajectory

track_bp = Blueprint('track', __name__)


@track_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_trajectory():
    user_id = get_jwt_identity()

    # 从数据库中获取当前用户的所有轨迹数据
    trajectories = Trajectory.query.filter_by(user_id=user_id).all()
    if not trajectories:
        return jsonify({"message": "No trajectory data found for this user"}), 404

    trajectory_data = trajectories[0].trajectory_data  # 假设每个用户的所有轨迹数据都在这一行
    processed_data = [{'lat': point['latitude'], 'lon': point['longitude'], 'timestamp': point['timestamp']}
                      for point in trajectory_data]

    processed_data = [processed_data]

    total_points = len(processed_data[0])

    # 从请求中获取算法的参数
    data = request.get_json()
    min_support = data.get('min_support', 2)
    min_length = data.get('min_length', 2)

    print("Processed data for analysis (first 5 points):", processed_data[:5])
    print("Total points in processed data:", len(processed_data))

    # 根据轨迹数据大小选择合适的算法
    if total_points < 10000:
        hotspots = NDTTJ(processed_data, kmin=min_length, mmin=min_support)  # 使用 NDTTJ 算法
    elif 10000 <= total_points <= 100000:
        hotspots = NDTTT(processed_data, kmin=min_length, mmin=min_support)  # 使用 NDTTT 算法
    else:
        hotspots = TTHS(processed_data, kmin=min_length, mmin=min_support)  # 使用 TTHS 算法

    # 将热点数据转换为 JSON 格式并生成哈希值
    hotspots_json = json.dumps(hotspots)
    hotspot_hash = HotspotTrajectory.generate_hash(hotspots)  # 使用模型中的 generate_hash

    # 检查 HotspotTrajectory 表中是否已存在相同的热点数据
    existing_hotspot = HotspotTrajectory.query.filter_by(user_id=user_id, hotspot_hash=hotspot_hash).first()
    if existing_hotspot:
        return jsonify({"message": "Hotspot data already exists, no new data was added"}), 200

    # 如果是新数据，插入 `HotspotTrajectory` 表
    new_hotspot = HotspotTrajectory(user_id=user_id, hotspot_data=hotspots_json, hotspot_hash=hotspot_hash)
    db.session.add(new_hotspot)
    db.session.commit()

    return jsonify({"hotspots": hotspots}), 200
