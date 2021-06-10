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


def get_wallet(tg_id: int):
    # wallets = get_user_wallets(tg_id)
    # return wallets[wallet_id]
    wallets = get_user_wallets(tg_id)
    for i in wallets:
        if wallets[i]["status"] == "active":
            return wallets[i]


def read_user_cache(tg_id: int, option: str):
    pckl_cache = cache.get(f":1:cache:{tg_id}")
    if not pckl_cache:
        return False
    return pickle.loads(cache.get(f":1:cache:{tg_id}"))[option]


def write_user_cache(tg_id: int, option: str, value: int or str):
    user_cache = pickle.loads(cache.get(f":1:cache:{tg_id}"))
    user_cache[option] = value
    cache.set(f":1:cache:{tg_id}", pickle.dumps(user_cache))


def get_fee():
    fee = pickle.loads(cache.get(f":1:fee"))
    if fee:
        return int(fee["fee"])
    return 1


def add_refcode(refcode):
    cds = cache.get(f":1:refcode")
    if not cache.get(f":1:refcode"):
        cds = []
    else:
        cds = pickle.loads(cds)
    cds.append(refcode)
    cache.set(f":1:refcode", pickle.dumps(cds))


def get_refcodes():
    return pickle.loads(cache.get(f":1:refcode"))


def del_refcode(refcode):
    cds = cache.get(f":1:refcode")
    if refcode in pickle.loads(cds):
        cds = pickle.loads(cds)
        cds.remove(refcode)
        cache.set(f":1:refcode", pickle.dumps(cds))


def get_user_profile(tg_id):
    return pickle.loads(cache.get(":1:users"))[tg_id]