import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.track.models import Trajectory, HotspotTrajectory
from backend.app import db, cache
from backend.scripts.NDTTJ import ndttj_algorithm
from backend.scripts.NDTTT import ndttt_algorithm
from backend.scripts.TSPMG_B import tspmg_b_algorithm
import json

track_bp = Blueprint('track', __name__)

@track_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_trajectory():
    try:
        data = request.get_json()
        if not data or 'trajectory' not in data:
            return jsonify({'status': 'error', 'message': 'Missing trajectory data'}), 400

        user_id = get_jwt_identity()
        trajectory_data = data['trajectory']

        if not isinstance(trajectory_data, list):
            return jsonify({'status': 'error', 'message': 'Invalid trajectory format. Expected a list.'}), 400

        new_trajectory = Trajectory(user_id=user_id, trajectory_data=json.dumps(trajectory_data))
        db.session.add(new_trajectory)
        db.session.commit()

        return jsonify({'message': 'Trajectory uploaded successfully!'}), 201

    except Exception as e:
        logging.error(f"Error uploading trajectory: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@track_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_trajectory():
    try:
        # 检查请求体是否为有效的 JSON 数据
        data = request.get_json()
        if data is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON data'}), 400

        # 获取 min_support 和 min_length
        min_support = data.get('min_support', 2)
        min_length = data.get('min_length', 2)

        user_id = get_jwt_identity()

        # 获取用户的轨迹数据
        user_trajectories = Trajectory.query.filter_by(user_id=user_id).all()
        if not user_trajectories:
            return jsonify({'message': 'No trajectory data available for analysis'}), 404

        # 将用户的轨迹数据转换为 Python 对象
        trajectory_list = [json.loads(t.trajectory_data) for t in user_trajectories]

        # 校验数据是否符合期望格式
        if not all(isinstance(traj, list) for traj in trajectory_list):
            return jsonify({'status': 'error', 'message': 'Invalid trajectory data format'}), 400

        # 自动选择合适的算法
        selected_algorithm = choose_best_algorithm(trajectory_list)

        # 根据选择的算法进行分析
        if selected_algorithm == 'NDTTJ':
            analysis_result = ndttj_algorithm(trajectory_list, min_support, min_length)
        elif selected_algorithm == 'NDTTT':
            analysis_result = ndttt_algorithm(trajectory_list, min_support, min_length)
        else:
            analysis_result = tspmg_b_algorithm(trajectory_list, min_support)

        # 存储分析结果
        for result in analysis_result:
            hotspot = HotspotTrajectory(user_id=user_id, hotspot_data=json.dumps(result))
            db.session.add(hotspot)

        # 缓存分析结果
        cache.set(f"hotspot_trajectories_{user_id}", analysis_result, timeout=3600)

        db.session.commit()
        return jsonify({'analysis_result': analysis_result}), 200

    except Exception as e:
        logging.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


def choose_best_algorithm(trajectory_list):
    """
    根据轨迹数据的特征自动选择最佳的分析算法。
    """
    total_trajectories = len(trajectory_list)
    avg_length = sum(len(traj) for traj in trajectory_list) / total_trajectories if total_trajectories > 0 else 0

    if total_trajectories < 10 and avg_length < 5:
        return 'NDTTJ'  # 数据稀疏时选择NDTTJ
    elif avg_length >= 5 and avg_length <= 15:
        return 'NDTTT'  # 数据密集但轨迹不复杂时选择NDTTT
    else:
        return 'TSPMG_B'  # 轨迹复杂且节点较多时选择TSPMG_B
