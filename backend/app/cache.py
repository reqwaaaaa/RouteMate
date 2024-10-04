import redis
import json

# 初始化 Redis 连接
cache = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# ---------- 热点轨迹缓存逻辑 ----------

def cache_hotspot_trajectories(user_id, hotspots, expiration=3600):
    """
    将用户的热点轨迹数据缓存到 Redis 中，缓存时间默认设置为 1 小时。
    :param user_id: 用户的 ID
    :param hotspots: 热点轨迹数据 (Python 字典或列表)
    :param expiration: 缓存的有效时间 (秒)
    """
    try:
        cache_key = f"hotspots_{user_id}"
        cache.setex(cache_key, expiration, json.dumps(hotspots))
    except Exception as e:
        print(f"Error caching hotspot trajectories: {e}")

def get_cached_hotspots(user_id):
    """
    从 Redis 缓存中获取用户的热点轨迹数据。
    :param user_id: 用户的 ID
    :return: 如果缓存命中，返回热点轨迹数据 (Python 字典或列表)；否则返回 None。
    """
    try:
        cache_key = f"hotspots_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        print(f"Error retrieving cached hotspot trajectories: {e}")
        return None

def delete_cached_hotspots(user_id):
    """
    从 Redis 缓存中删除用户的热点轨迹数据。
    :param user_id: 用户的 ID
    """
    try:
        cache_key = f"hotspots_{user_id}"
        cache.delete(cache_key)
    except Exception as e:
        print(f"Error deleting cached hotspot trajectories: {e}")

# ---------- 拼车推荐缓存逻辑 ----------

def cache_recommendations(user_id, recommendations, expiration=3600):
    """
    将用户的拼车推荐数据缓存到 Redis 中，缓存时间默认设置为 1 小时。
    :param user_id: 用户的 ID
    :param recommendations: 推荐数据 (Python 字典或列表)
    :param expiration: 缓存的有效时间 (秒)
    """
    try:
        cache_key = f"recommendations_{user_id}"
        cache.setex(cache_key, expiration, json.dumps(recommendations))
    except Exception as e:
        print(f"Error caching recommendations: {e}")

def get_cached_recommendations(user_id):
    """
    从 Redis 缓存中获取用户的拼车推荐数据。
    :param user_id: 用户的 ID
    :return: 如果缓存命中，返回推荐数据 (Python 字典或列表)；否则返回 None。
    """
    try:
        cache_key = f"recommendations_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        print(f"Error retrieving cached recommendations: {e}")
        return None

def delete_cached_recommendations(user_id):
    """
    从 Redis 缓存中删除用户的拼车推荐数据。
    :param user_id: 用户的 ID
    """
    try:
        cache_key = f"recommendations_{user_id}"
        cache.delete(cache_key)
    except Exception as e:
        print(f"Error deleting cached recommendations: {e}")
