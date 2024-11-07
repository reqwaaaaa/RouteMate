import collections
from datetime import datetime


def build_graph(trajectories):
    graph = collections.defaultdict(lambda: collections.defaultdict(int))
    for trajectory in trajectories:
        for i in range(len(trajectory) - 1):
            node = tuple(trajectory[i].values())
            next_node = tuple(trajectory[i + 1].values())
            graph[node][next_node] += 1
    return graph


def TTHS(trajectories, kmin, mmin):
    if not trajectories:
        raise ValueError("轨迹数据为空或无效")

    graph = build_graph(trajectories)
    result_paths = set()

    def dfs(current_path, frequency):
        last_node = current_path[-1]
        if len(current_path) >= kmin and frequency >= mmin:
            result_paths.add(tuple(current_path))
        for neighbor, freq in graph[last_node].items():
            min_freq = min(frequency, freq)
            if min_freq >= mmin:
                dfs(current_path + [neighbor], min_freq)

    for node in graph.keys():
        dfs([node], float('inf'))

    # 转换为所需的输出格式
    hotspot_paths = []
    for path in result_paths:
        if len(path) >= kmin:
            hotspot_path = []
            for item in path:
                hotspot_path.append({'lat': item[0], 'lon': item[1], 'timestamp': item[2]})
            hotspot_paths.append(hotspot_path)

    return hotspot_paths


