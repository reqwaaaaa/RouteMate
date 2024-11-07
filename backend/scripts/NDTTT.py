import collections
from datetime import datetime


def NDTTT(trajectories, kmin, mmin):
    if not trajectories:
        raise ValueError("轨迹数据为空或无效")

    # 初始化1阶路径表
    path_table = collections.defaultdict(int)
    for trajectory in trajectories:
        for point in trajectory:
            path = (tuple(point.values()),)
            path_table[path] += 1

    # 初始剪枝
    path_table = {path: count for path, count in path_table.items() if count >= mmin}

    k = 1  # 当前路径长度（节点数量）
    result_paths = dict(path_table)

    while path_table:
        next_path_table = collections.defaultdict(int)
        for trajectory in trajectories:
            trajectory_points = [tuple(point.values()) for point in trajectory]
            trajectory_length = len(trajectory_points)
            for i in range(trajectory_length - k):
                current_path = tuple(trajectory_points[i:i + k])
                if current_path in path_table:
                    extended_path = current_path + (trajectory_points[i + k],)
                    next_path_table[extended_path] += 1

        # 剪枝
        path_table = {path: count for path, count in next_path_table.items() if count >= mmin}

        # 更新结果路径
        result_paths.update(path_table)

        k += 1  # 增加路径长度

    # 收集满足kmin的路径
    final_paths = {path: count for path, count in result_paths.items() if len(path) >= kmin}

    # 转换为所需的输出格式
    hotspot_paths = []
    for path in final_paths.keys():
        hotspot_path = []
        for item in path:
            hotspot_path.append({'lat': item[0], 'lon': item[1], 'timestamp': item[2]})
        hotspot_paths.append(hotspot_path)

    return hotspot_paths
