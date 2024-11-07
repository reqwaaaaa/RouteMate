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

    # 处理所有轨迹
    processed_data = []
    for trajectory in trajectories:
        # 获取 trajectory_data 并解析为 Python 对象
        trajectory_data_json = trajectory.trajectory_data
        if isinstance(trajectory_data_json, str):
            trajectory_data = json.loads(trajectory_data_json)
        else:
            trajectory_data = trajectory_data_json  # 已经是字典或列表

        # 处理轨迹点
        processed_trajectory = []
        for point in trajectory_data:
            processed_point = {
                'lat': point.get('lat') or point.get('latitude'),
                'lon': point.get('lon') or point.get('longitude'),
                'timestamp': point.get('timestamp') or point.get('time')
            }
            # 确保时间戳是整数类型
            if isinstance(processed_point['timestamp'], str):
                processed_point['timestamp'] = int(processed_point['timestamp'])
            else:
                processed_point['timestamp'] = int(processed_point['timestamp'])

            processed_trajectory.append(processed_point)

        # 确保轨迹点按照时间排序
        processed_trajectory.sort(key=lambda x: x['timestamp'])

        # 将处理好的轨迹添加到列表中
        processed_data.append(processed_trajectory)

    # 至此，processed_data 就是算法需要的 trajectories 变量
    # 例如：
    # processed_data = [
    #     [   # 第一条轨迹
    #         {'lat': ..., 'lon': ..., 'timestamp': ...},
    #         # 更多轨迹点
    #     ],
    #     [   # 第二条轨迹
    #         {'lat': ..., 'lon': ..., 'timestamp': ...},
    #         # 更多轨迹点
    #     ],
    #     # 更多轨迹
    # ]

    total_points = sum(len(traj) for traj in processed_data)

    # 从请求中获取算法的参数
    data = request.get_json()
    min_support = data.get('min_support', 2)
    min_length = data.get('min_length', 2)

    print("Total points in processed data:", total_points)

    # 根据轨迹数据大小选择合适的算法
    if total_points < 5000:
        hotspots = NDTTJ(processed_data, kmin=min_length, mmin=min_support)  # 使用 NDTTJ 算法
    elif 5000 <= total_points <= 10000:
        hotspots = NDTTT(processed_data, kmin=min_length, mmin=min_support)  # 使用 NDTTT 算法
    else:
        hotspots = TTHS(processed_data, kmin=min_length, mmin=min_support)  # 使用 TTHS 算法

    # 将热点数据转换为 JSON 格式并生成哈希值
    hotspots_json = json.dumps(hotspots)
    hotspot_hash = HotspotTrajectory.generate_hash(hotspots)

    existing_hotspot = HotspotTrajectory.query.filter_by(user_id=user_id, hotspot_hash=hotspot_hash).first()
    if existing_hotspot:
        return jsonify({"message": "Hotspot data already exists, no new data was added"}), 200

    # 如果是新数据，插入 `HotspotTrajectory` 表
    new_hotspot = HotspotTrajectory(user_id=user_id, hotspot_data=hotspots_json, hotspot_hash=hotspot_hash)
    db.session.add(new_hotspot)
    db.session.commit()

    return jsonify({"hotspots": hotspots}), 200
