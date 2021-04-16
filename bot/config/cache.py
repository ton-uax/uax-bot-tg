import redis
import pickle

cache = redis.Redis(host="redis")


def get_user_cache(tg_id):
    if not cache.get(f":1:{tg_id}"):
        return None
    return pickle.loads(cache.get(f":1:{tg_id}"))


def change_user_cache(tg_id: int, flag_name: str, value):
    user_cache = get_user_cache(tg_id)

    if user_cache:
        user_cache[flag_name] = value
        cache.set(f":1:{tg_id}", pickle.dumps(user_cache))

