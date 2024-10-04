import concurrent.futures
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)


def ndttt_algorithm(trajectories, freq_threshold, max_steps):
    if not trajectories:
        raise ValueError("Trajectory data is empty.")

    logging.info("Initializing 1-degree path table.")

    # 初始化1阶路径表
    path_table = {}
    for traj in trajectories:
        if len(traj) < 2:
            logging.warning(f"Skipping trajectory due to insufficient length: {traj}")
            continue
        for i in range(len(traj) - 1):
            pair = (traj[i], traj[i + 1])
            if pair not in path_table:
                path_table[pair] = []
            path_table[pair].append(traj)

    # 剪枝：删除不满足频繁度阈值的路径
    path_table = {pair: trajs for pair, trajs in path_table.items() if len(trajs) >= freq_threshold}

    current_paths = list(path_table.keys())

    # 多次迭代，扩展路径
    for step in range(2, max_steps):
        logging.info(f"Starting step {step} with {len(current_paths)} current paths.")

        new_path_table = {}

        # 使用线程池并行扩展路径
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
                    logging.error(f"Error while extending path: {e}")

        # 剪枝：删除不满足频繁度阈值的路径
        new_path_table = {path: trajs for path, trajs in new_path_table.items() if len(trajs) >= freq_threshold}

        if not new_path_table:
            logging.info("No more frequent paths found. Ending.")
            break

        path_table = new_path_table
        current_paths = list(new_path_table.keys())

    logging.info("NDTTT Algorithm completed.")
    return current_paths


def extend_path_concurrently(path, path_table, step):
    new_paths = []
    for traj in path_table[path]:
        if len(traj) <= step:
            continue
        new_path = path + (traj[step],)
        new_paths.append((new_path, traj))
    return new_path, traj
