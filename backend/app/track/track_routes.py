from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
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

    # 从数据库中获取用户的所有轨迹数据
    trajectory_records = Trajectory.query.filter_by(user_id=user_id).all()
    if not trajectory_records:
        return jsonify({"message": "No trajectory data found for this user"}), 404

    # 整合每个用户的多条轨迹数据，形成嵌套结构
    processed_data = []
    for idx, trajectory in enumerate(trajectory_records, start=1):
        trajectory_data = trajectory.trajectory_data.get('nodes', [])
        if trajectory_data:
            processed_data.append({
                "trajectory_id": idx,
                "nodes": trajectory_data
            })

    print("Processed data for algorithm:", processed_data)

    # 从请求中获取算法的参数
    data = request.get_json() or {}
    min_support = data.get('min_support', 6)
    min_length = data.get('min_length', 3)

    # 根据轨迹数量选择合适的算法
    try:
        if len(processed_data) == 0:
            return jsonify({"message": "No trajectory data to analyze"}), 400

        total_trajectories = len(processed_data)
        print("Total trajectories in processed data:", total_trajectories)

        if total_trajectories < 50:
            hotspots = NDTTJ(processed_data, kmin=min_length, mmin=min_support)  # 使用 NDTTJ 算法
        elif 50 <= total_trajectories <= 1000:
            hotspots = NDTTT(processed_data, kmin=min_length, mmin=min_support)  # 使用 NDTTT 算法
        else:
            hotspots = TTHS(processed_data, kmin=min_length, mmin=min_support)  # 使用 TTHS 算法

    except Exception as e:
        print("Error running the algorithm:", str(e))
        return jsonify({"message": "Error running the algorithm", "error": str(e)}), 500

    # 检查是否已存在相同的热点数据
    hotspot_hash = HotspotTrajectory.generate_hash(hotspots)
    existing_hotspot = HotspotTrajectory.query.filter_by(user_id=user_id, hotspot_hash=hotspot_hash).first()

    if existing_hotspot:
        return jsonify({"hotspots": hotspots, "message": "Hotspot data already exists, no new data was added"}), 200

    # 如果是新数据，插入 `HotspotTrajectory` 表
    new_hotspot = HotspotTrajectory(user_id=user_id, hotspot_data=hotspots, hotspot_hash=hotspot_hash)
    db.session.add(new_hotspot)
    db.session.commit()

    return jsonify({"hotspots": hotspots}), 200
