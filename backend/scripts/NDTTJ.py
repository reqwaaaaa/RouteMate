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


def NDTTJ(trajectories, kmin, mmin):
    """
    基于 N 度路径表连接的轨迹热点挖掘算法
    适用于稀疏轨迹数据，基于 Apriori-like 方法通过连接路径表生成更长路径。

    参数：
    - trajectories: 轨迹集合，每个轨迹为字典形式的节点序列 {'lat', 'lon', 'timestamp'}
    - kmin: 最小路径长度阈值
    - mmin: 频繁度阈值

    返回：
    - 热点路径集合
    """
    # 数据预处理，清洗异常值并转换时间戳
    trajectories = preprocess_trajectory_data(trajectories)

    if not trajectories:
        raise ValueError("轨迹数据为空或经过预处理后无有效数据")

    # Step 1: 初始化 1 阶路径表，记录每条长度为 2 的路径的出现频率
    path_table = collections.defaultdict(int)
    for trajectory in trajectories:
        for i in range(len(trajectory) - 1):
            path = (tuple(trajectory[i].items()), tuple(trajectory[i + 1].items()))
            path_table[path] += 1

    # 剪枝操作，去除不满足频繁度的路径
    path_table = {path: count for path, count in path_table.items() if count >= mmin}

    # Step 2: 迭代生成更长的路径，直到满足 kmin
    k = 2  # 当前路径长度
    while k < kmin and path_table:
        # 生成候选路径集合
        candidates = {}
        paths = list(path_table.keys())
        for i in range(len(paths)):
            for j in range(len(paths)):
                # 如果两个路径的前 k-1 个节点相同，则可以连接
                if paths[i][:-1] == paths[j][:-1]:
                    new_path = paths[i] + (paths[j][-1],)
                    candidates[new_path] = 0

        # 统计候选路径的出现频率
        for trajectory in trajectories:
            trajectory_points = [tuple(point.items()) for point in trajectory]
            trajectory_length = len(trajectory_points)
            for candidate in candidates.keys():
                candidate_length = len(candidate)
                for idx in range(trajectory_length - candidate_length + 1):
                    if tuple(trajectory_points[idx:idx + candidate_length]) == candidate:
                        candidates[candidate] += 1

        # 剪枝操作
        path_table = {path: count for path, count in candidates.items() if count >= mmin}
        k += 1

    # 返回结果
    result_paths = [[dict(items) for items in path] for path in path_table.keys()]
    return result_paths
