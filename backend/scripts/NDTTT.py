import collections


def NDTTT(trajectories, kmin, mmin):
    """
    NDTTT（N-Degree Trajectory Table Traversal）算法实现，用于从轨迹数据中挖掘热点路径。

    参数：
    - trajectories: 轨迹列表，每个轨迹是一个包含 'nodes' 和 'trajectory_id' 的字典。
    - kmin: 最小路径长度。
    - mmin: 最小频繁度。

    返回：
    - hotspot_paths: 热点路径列表。
    """

    if not trajectories:
        raise ValueError("轨迹数据为空或无效")

    # 步骤 1：初始化 1 阶路径表（单个点的路径）
    path_table = collections.defaultdict(set)
    for trajectory in trajectories:
        trajectory_id = trajectory['trajectory_id']
        nodes = trajectory['nodes']
        for node in nodes:
            point_tuple = (node['latitude'], node['longitude'])
            path = (point_tuple,)
            path_table[path].add(trajectory_id)

    # 初始剪枝：移除频繁度小于 mmin 的路径
    pruned_table = {
        path: traj_ids
        for path, traj_ids in path_table.items()
        if len(traj_ids) >= mmin
    }

    k = 1  # 当前路径长度
    result_paths = dict(pruned_table)

    # 步骤 2：遍历并生成更长的路径
    while pruned_table:
        next_path_table = collections.defaultdict(set)
        for trajectory in trajectories:
            trajectory_id = trajectory['trajectory_id']
            nodes = trajectory['nodes']
            trajectory_points = [(node['latitude'], node['longitude']) for node in nodes]
            trajectory_length = len(trajectory_points)
            for i in range(trajectory_length - k):
                current_path = tuple(trajectory_points[i:i + k])
                if current_path in pruned_table and trajectory_id in pruned_table[current_path]:
                    extended_path = current_path + (trajectory_points[i + k],)
                    next_path_table[extended_path].add(trajectory_id)

        # 剪枝：移除频繁度小于 mmin 的路径
        pruned_table = {
            path: traj_ids
            for path, traj_ids in next_path_table.items()
            if len(traj_ids) >= mmin
        }
        result_paths.update(pruned_table)
        k += 1  # 增加路径长度

    # 收集满足 kmin 的路径
    final_paths = {
        path: traj_ids
        for path, traj_ids in result_paths.items()
        if len(path) >= kmin
    }

    # 转换为所需的输出格式
    hotspot_paths = []
    for path in final_paths.keys():
        hotspot_path = []
        for item in path:
            hotspot_path.append({
                'latitude': item[0],
                'longitude': item[1]
            })
        hotspot_paths.append(hotspot_path)

    return hotspot_paths
