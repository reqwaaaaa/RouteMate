import logging
import concurrent.futures

# 配置日志
logging.basicConfig(level=logging.INFO)


def ndttt_algorithm(trajectories, freq_threshold, max_steps):
    if not trajectories:
        raise ValueError("Trajectory data is empty.")

    logging.info("初始化1阶路径表")

    # 初始化1阶路径表
    path_table = {}
    for traj in trajectories:
        if len(traj) < 2:
            continue
        for i in range(len(traj) - 1):
            pair = (traj[i], traj[i + 1])
            if pair not in path_table:
                path_table[pair] = []
            path_table[pair].append(traj)

    # 剪枝：删除不满足频繁度阈值的路径
    path_table = {pair: trajs for pair, trajs in path_table.items() if len(trajs) >= freq_threshold}
    current_paths = list(path_table.keys())

    # 多次迭代，沿轨迹序列遍历生成更高阶路径
    for step in range(2, max_steps):
        logging.info(f"第 {step} 步，当前路径数：{len(current_paths)}")

        new_path_table = {}

        # 并行处理路径扩展
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(extend_path_concurrently, path, path_table, step): path for path in
                       current_paths}
            for future in concurrent.futures.as_completed(futures):
                try:
                    new_path, trajs = future.result()
                    if new_path:
                        if new_path not in new_path_table:
                            new_path_table[new_path] = []
                        new_path_table[new_path].extend(trajs)
                except Exception as e:
                    logging.error(f"路径扩展时出错: {e}")

        # 剪枝：删除不满足频繁度阈值的路径
        new_path_table = {path: trajs for path, trajs in new_path_table.items() if len(trajs) >= freq_threshold}

        if not new_path_table:
            logging.info("未发现更多频繁路径，算法结束。")
            break

        path_table = new_path_table
        current_paths = list(new_path_table.keys())

    logging.info("NDTTT算法完成")
    return current_paths


def extend_path_concurrently(path, path_table, step):
    """
    扩展路径并返回新的路径和轨迹数据
    """
    new_paths = []
    for traj in path_table[path]:
        if len(traj) > step:
            new_path = path + (traj[step],)  # 继续扩展路径
            new_paths.append((new_path, traj))

    return new_path, traj
