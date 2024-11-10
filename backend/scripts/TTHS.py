import collections
import sys

# 增加递归深度限制
sys.setrecursionlimit(2000)


def TTHS(trajectories, kmin, mmin):
    """
    TTHS（Trajectory Traversal Hotspots Search）算法实现，用于在轨迹图中搜索热点路径。

    参数：
    - trajectories: 轨迹列表，每个轨迹是一个包含 'nodes' 和 'trajectory_id' 的字典。
    - kmin: 最小路径长度。
    - mmin: 最小频繁度。

    返回：
    - hotspot_paths: 热点路径列表。
    """

    if not trajectories:
        raise ValueError("轨迹数据为空或无效")

    # 构建轨迹图
    graph = build_graph(trajectories)
    result_paths = set()

    # 使用显式栈实现迭代版的 DFS
    def dfs_iterative(start_node, kmin, mmin):
        stack = [(start_node, [start_node], float('inf'))]  # 栈中存储 (当前节点, 当前路径, 当前频率)
        visited_paths = set()

        while stack:
            current_node, current_path, current_frequency = stack.pop()
            if tuple(current_path) in visited_paths:
                continue
            visited_paths.add(tuple(current_path))

            if len(current_path) >= kmin and current_frequency >= mmin:
                result_paths.add(tuple(current_path))

            for neighbor, freq in graph[current_node].items():
                min_freq = min(current_frequency, freq)
                if min_freq >= mmin:
                    stack.append((neighbor, current_path + [neighbor], min_freq))

    # 遍历所有节点，进行迭代版 DFS
    for node in graph.keys():
        dfs_iterative(node, kmin, mmin)

    # 转换为所需的输出格式
    hotspot_paths = []
    for path in result_paths:
        hotspot_path = []
        for item in path:
            hotspot_path.append({
                'latitude': item[0],
                'longitude': item[1]
            })
        hotspot_paths.append(hotspot_path)

    return hotspot_paths


def build_graph(trajectories):
    """
    构建轨迹图，节点为轨迹点，边的权重为两点之间的转移频率。

    参数：
    - trajectories: 轨迹列表。

    返回：
    - graph: 以邻接表形式存储的图结构。
    """
    graph = collections.defaultdict(lambda: collections.defaultdict(int))
    for trajectory in trajectories:
        nodes = trajectory['nodes']
        visited_edges = set()
        for i in range(len(nodes) - 1):
            node = (nodes[i]['latitude'], nodes[i]['longitude'])
            next_node = (nodes[i + 1]['latitude'], nodes[i + 1]['longitude'])
            edge = (node, next_node)
            if edge not in visited_edges:
                graph[node][next_node] += 1
                visited_edges.add(edge)
    return graph
