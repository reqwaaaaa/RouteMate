import pandas as pd
from datetime import datetime
import os

# 设置包含.plt文件的文件夹路径
folder_path = "C:\\Users\\86138\Downloads\\Geolife Trajectories 1.3\\Geolife Trajectories 1.3\Data\\140\\Trajectory"  # 替换为实际的文件夹路径
output_folder = "C:\\Users\\86138\\Desktop\\RouteMate\\DataSets"  # 替换为保存清洗后文件的路径

# 如果输出文件夹不存在，创建它
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def clean_plt_file(file_path):
    # 读取.plt文件，跳过前6行的头部信息
    data = pd.read_csv(file_path, skiprows=6, header=None)

    # 为数据列命名
    data.columns = ["latitude", "longitude", "altitude", "speed", "julian_time", "date", "time"]

    # 合并 'date' 和 'time' 列为一个新的datetime列
    data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'], format='%Y-%m-%d %H:%M:%S')

    # 将合并后的datetime转换为UNIX时间戳
    data['timestamp'] = data['datetime'].apply(lambda x: int(datetime.timestamp(x)))

    # 保留必要的列
    cleaned_data = data[['latitude', 'longitude', 'timestamp']]

    return cleaned_data

# 设定用户ID（假设整个文件夹对应一个用户）
user_id = 100000  # 可以根据实际情况调整(对应本地数据库中的id)

# 初始化一个DataFrame用于存储合并的轨迹数据
all_trajectory_data = pd.DataFrame()

# 遍历文件夹中的所有.plt文件
for file_name in os.listdir(folder_path):
    if file_name.endswith('.plt'):
        file_path = os.path.join(folder_path, file_name)
        cleaned_data = clean_plt_file(file_path)

        # 为每个清洗后的数据添加 user_id 和轨迹日期列
        cleaned_data['user_id'] = user_id
        cleaned_data['trajectory_date'] = file_name.replace('.plt', '')  # 用文件名表示轨迹日期

        # 将清洗后的数据合并到总DataFrame中
        all_trajectory_data = pd.concat([all_trajectory_data, cleaned_data], ignore_index=True)

# 将合并的轨迹数据保存为一个CSV文件
output_file_path = os.path.join(output_folder, f"user_{user_id}_trajectory.csv")
all_trajectory_data.to_csv(output_file_path, index=False)
print(f"已清洗并保存用户 {user_id} 的轨迹数据至文件：{output_file_path}")
