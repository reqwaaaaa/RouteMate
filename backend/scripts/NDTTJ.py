import collections


def NDTTJ(trajectories, kmin, mmin):
    """
    NDTTJ（N-Degree Trajectory Table Join）算法实现，用于从轨迹数据中挖掘热点路径。

    参数：
    - trajectories: 轨迹列表，每个轨迹是一个包含 'nodes' 和 'trajectory_id' 的字典。
    - kmin: 最小路径长度（节点数量）。
    - mmin: 最小频繁度（路径出现的最小轨迹数）。

    返回：
    - hotspot_paths: 热点路径列表，每个路径是轨迹点的列表。
    """

    if not trajectories:
        raise ValueError("轨迹数据为空或无效")

    # 步骤 1：初始化 1 阶路径表（长度为 2 的路径）
    path_table = collections.defaultdict(set)
    for trajectory in trajectories:
        trajectory_id = trajectory['trajectory_id']
        nodes = trajectory['nodes']
        for i in range(len(nodes) - 1):
            # 只使用经纬度作为比较键，忽略时间戳
            point1 = (nodes[i]['latitude'], nodes[i]['longitude'])
            point2 = (nodes[i + 1]['latitude'], nodes[i + 1]['longitude'])
            path = (point1, point2)
            path_table[path].add(trajectory_id)

    # 初始剪枝：移除频繁度小于 mmin 的路径
    pruned_table = {
        path: traj_ids
        for path, traj_ids in path_table.items()
        if len(traj_ids) >= mmin
    }

    k = 2  # 当前路径长度
    result_paths = dict(pruned_table)

    # 步骤 2：迭代生成更长的路径
    while pruned_table:
        next_path_table = collections.defaultdict(set)
        paths = list(pruned_table.keys())
        for path1 in paths:
            for path2 in paths:
                # 检查路径是否可以连接
                if path1[1:] == path2[:-1]:
                    new_path = path1 + (path2[-1],)
                    combined_ids = pruned_table[path1].intersection(pruned_table[path2])
                    if len(combined_ids) >= mmin:
                        next_path_table[new_path] = combined_ids

        pruned_table = next_path_table
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
