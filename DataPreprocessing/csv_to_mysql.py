import pandas as pd
from sqlalchemy import create_engine, text
import os
import json
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

def main():
    # 数据库连接设置
    database_uri = os.environ.get('DATABASE_URI')
    if not database_uri:
        raise ValueError("未找到环境变量'DATABASE_URI'，请检查环境变量设置。")

    try:
        engine = create_engine(database_uri)
        print("数据库连接已建立。")
    except SQLAlchemyError as e:
        print("数据库连接失败:", e)
        exit()

    uploaded_files_path = 'uploaded_files.json'

    if os.path.exists(uploaded_files_path):
        with open(uploaded_files_path, 'r', encoding='utf-8') as f:
            uploaded_files = json.load(f)
    else:
        uploaded_files = []

    folder_path = "C:\\Users\\86138\\Desktop\\RouteMate\\DataSets"

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            if file_name in uploaded_files:
                print(f"文件 {file_name} 已上传，跳过该文件。")
                continue

            try:
                user_id = int(file_name.split('_')[1])  # 提取用户ID
                file_path = os.path.join(folder_path, file_name)

                # 读取并检查数据
                data = pd.read_csv(file_path)
                if not all(column in data.columns for column in ['latitude', 'longitude', 'timestamp']):
                    raise ValueError(f"文件 {file_name} 缺少必要的列。")
                
                # 对经纬度进行四舍五入操作（小数点后四位）
                data['latitude'] = data['latitude'].round(4)
                data['longitude'] = data['longitude'].round(4)

                # 确保 timestamp 列为数值型并排序
                data['timestamp'] = pd.to_numeric(data['timestamp'], errors='coerce')
                data.dropna(subset=['timestamp'], inplace=True)
                data = data.sort_values(by='timestamp')

                # 设置时间阈值以划分轨迹
                time_threshold = 300  # 5分钟
                data['trajectory_id'] = (data['timestamp'].diff() > time_threshold).cumsum().fillna(0).astype(int)

                # 转换为 JSON 格式以插入数据库
                grouped_data = data.groupby('trajectory_id').apply(lambda x: {
                    "trajectory_id": int(x['trajectory_id'].iloc[0]),
                    "nodes": x[['latitude', 'longitude', 'timestamp']].to_dict(orient='records')
                }).tolist()

                # 将轨迹数据插入数据库
                with engine.connect() as conn:
                    query = text("""
                        INSERT INTO Trajectory (user_id, trajectory_data)
                        VALUES (:user_id, :trajectory_data)
                    """)
                    for traj in grouped_data:
                        conn.execute(query, {"user_id": user_id, "trajectory_data": json.dumps(traj)})
                
                print(f"用户 {user_id} 的数据已成功导入数据库")

                # 更新已上传的文件列表
                uploaded_files.append(file_name)
                with open(uploaded_files_path, 'w', encoding='utf-8') as f:
                    json.dump(uploaded_files, f, ensure_ascii=False, indent=4)

            except FileNotFoundError:
                print(f"文件 {file_name} 未找到，请检查路径。")
            except ValueError as ve:
                print(f"数据验证错误：{ve}")
            except SQLAlchemyError as se:
                print(f"数据库插入错误：用户 {user_id} - {se}")

    print("所有用户的轨迹数据已成功导入数据库。")

if __name__ == "__main__":
    main()
