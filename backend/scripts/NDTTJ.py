import collections
from datetime import datetime


def NDTTJ(trajectories, kmin, mmin):
    if not trajectories:
        raise ValueError("轨迹数据为空或无效")

    # 初始化1阶路径表
    path_table = collections.defaultdict(int)
    for trajectory in trajectories:
        for i in range(len(trajectory) - 1):
            path = (tuple(trajectory[i].values()), tuple(trajectory[i + 1].values()))
            path_table[path] += 1

    # 初始剪枝
    path_table = {path: count for path, count in path_table.items() if count >= mmin}

    k = 2  # 当前路径长度（节点数量）
    result_paths = dict(path_table)

    while path_table:
        # 生成候选路径
        candidates = collections.defaultdict(int)
        paths = list(path_table.keys())
        temp_candidates = set()
        for i in range(len(paths)):
            for j in range(len(paths)):
                if paths[i][1:] == paths[j][:-1]:
                    new_path = paths[i] + (paths[j][-1],)
                    temp_candidates.add(new_path)

        # 统计新路径的频繁度
        for candidate in temp_candidates:
            for trajectory in trajectories:
                trajectory_points = [tuple(point.values()) for point in trajectory]
                candidate_length = len(candidate)
                for idx in range(len(trajectory_points) - candidate_length + 1):
                    if tuple(trajectory_points[idx:idx + candidate_length]) == candidate:
                        candidates[candidate] += 1

        # 剪枝
        path_table = {path: count for path, count in candidates.items() if count >= mmin}

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
