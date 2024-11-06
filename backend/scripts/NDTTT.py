import collections
from datetime import datetime


def NDTTT(trajectories, kmin, mmin):
    """
    基于路径遍历扩展的轨迹热点挖掘算法
    适用于密集轨迹数据，通过遍历轨迹序列动态扩展路径。

    参数：
    - trajectories: 轨迹集合，每个轨迹为字典形式的节点序列 {'lat', 'lon', 'timestamp'}
    - kmin: 最小路径长度阈值
    - mmin: 频繁度阈值

    返回：
    - 热点路径集合
    """
    if not trajectories:
        raise ValueError("轨迹数据为空或经过预处理后无有效数据")

    # Step 1: 初始化 1 阶路径表，记录每个单节点的出现频率
    path_table = collections.defaultdict(int)
    for trajectory in trajectories:
        for point in trajectory:
            path = (tuple(point.items()),)
            path_table[path] += 1

    # 剪枝操作，去除不满足频繁度的路径
    path_table = {path: count for path, count in path_table.items() if count >= mmin}

    # 初始化结果集合
    result_paths = set()

    # Step 2: 路径扩展，直到达到最小路径长度 kmin
    k = 1  # 当前路径长度
    while k < kmin and path_table:
        next_path_table = collections.defaultdict(int)
        for trajectory in trajectories:
            trajectory_points = [tuple(point.items()) for point in trajectory]
            trajectory_length = len(trajectory_points)
            for i in range(trajectory_length - k):
                current_path = tuple(trajectory_points[i:i + k])
                if current_path in path_table:
                    extended_path = current_path + (trajectory_points[i + k],)
                    next_path_table[extended_path] += 1
        # 剪枝操作
        path_table = {path: count for path, count in next_path_table.items() if count >= mmin}
        k += 1

    # 收集满足条件的路径
    result_paths = [[dict(items) for items in path] for path in path_table.keys() if len(path) >= kmin]

    return result_paths
