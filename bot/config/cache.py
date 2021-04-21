import redis
import pickle

cache = redis.Redis(host="redis")


def get_user_flags(tg_id: int):
    if not cache.get(f":1:flags:{tg_id}"):
        return None
    return pickle.loads(cache.get(f":1:flags:{tg_id}"))


def change_user_flag(tg_id: int, flag_name: str, value):
    user_cache = get_user_flags(tg_id)

    if user_cache:
        user_cache[flag_name] = value
        cache.set(f":1:flags:{tg_id}", pickle.dumps(user_cache))


def get_user_wallets(tg_id: int):
    wallets = cache.get(f":1:wallets:{tg_id}")
    if not wallets:
        return {}
    return pickle.loads(wallets)


def get_active_wallet(tg_id: int):
    wallets = get_user_wallets(tg_id)
    for i in wallets:
        if wallets[i]["status"] == "active":
            return wallets[i]


def get_wallet(tg_id: int, wallet_id: int):
    wallets = get_user_wallets(tg_id)
    return wallets[wallet_id]


def read_user_cache(tg_id: int, option: str):
    return pickle.loads(cache.get(f":1:cache:{tg_id}"))[option]


def write_user_cache(tg_id: int, option: str, value: int or str):
    user_cache = pickle.loads(cache.get(f":1:cache:{tg_id}"))
    user_cache[option] = value
    cache.set(f":1:cache:{tg_id}", pickle.dumps(user_cache))