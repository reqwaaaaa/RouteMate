import collections
from datetime import datetime


def preprocess_trajectory_data(trajectories):
    """
    数据预处理函数：处理经纬度和时间戳数据
    过滤掉异常数据，并将时间戳转换为 datetime 对象
    """
    cleaned_trajectories = []
    for trajectory in trajectories:
        cleaned_trajectory = []
        for point in trajectory:
            lat, lon, timestamp = point.get('lat'), point.get('lon'), point.get('timestamp')
            if lat is None or lon is None or timestamp is None:
                continue
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):  # 经纬度范围验证
                continue
            try:
                # 时间戳解析
                time_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                cleaned_trajectory.append({'lat': lat, 'lon': lon, 'timestamp': time_obj})
            except ValueError:
                continue
        if cleaned_trajectory:
            cleaned_trajectories.append(cleaned_trajectory)
    return cleaned_trajectories


def build_graph(trajectories):
    """
    构建轨迹图，节点为轨迹点，边为相邻点的连接，边上附带出现频率
    """
    graph = collections.defaultdict(lambda: collections.defaultdict(int))
    for trajectory in trajectories:
        for i in range(len(trajectory) - 1):
            node = tuple(trajectory[i].items())
            next_node = tuple(trajectory[i + 1].items())
            graph[node][next_node] += 1
    return graph


def TTHS(trajectories, kmin, mmin):
    """
    基于 DFS 的轨迹热点搜索算法
    适用于具有图结构的轨迹数据，利用图进行深度优先搜索和剪枝。

    参数：
    - trajectories: 轨迹集合，每个轨迹为字典形式的节点序列 {'lat', 'lon', 'timestamp'}
    - kmin: 最小路径长度阈值
    - mmin: 频繁度阈值

    返回：
    - 热点路径集合
    """
    # 数据预处理
    trajectories = preprocess_trajectory_data(trajectories)

    if not trajectories:
        raise ValueError("轨迹数据为空或经过预处理后无有效数据")

    # 构建轨迹图
    graph = build_graph(trajectories)

    # 缓存每条路径的频繁度
    path_frequency = {}

    # 结果集合
    result_paths = set()

    # 深度优先搜索函数
    def dfs(current_path, current_node):
        if len(current_path) >= 2:
            # 计算当前路径的频繁度（路径上所有边的最小频率）
            freq = min(
                [graph[tuple(current_path[i])][tuple(current_path[i + 1])] for i in range(len(current_path) - 1)])
            if freq >= mmin:
                if len(current_path) >= kmin:
                    result_paths.add(tuple(current_path))
            else:
                return  # 剪枝：频繁度不满足要求
        for neighbor, count in graph[current_node].items():
            if count >= mmin:
                dfs(current_path + [dict(neighbor)], neighbor)

    # 遍历所有节点，启动 DFS
    for node in graph.keys():
        dfs([dict(node)], node)

    # 返回结果
    result_paths = [path for path in result_paths if len(path) >= kmin]
    return result_paths
