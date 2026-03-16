import time

cache = {}

def set_cache(key, data):
    cache[key] = {
        "data": data,
        "time": time.time()
    }

def get_cache(key, ttl=60):
    if key not in cache:
        return None

    if time.time() - cache[key]["time"] > ttl:
        del cache[key]
        return None

    return cache[key]["data"]