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
    # 数据预处理
    trajectories = preprocess_trajectory_data(trajectories)

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
