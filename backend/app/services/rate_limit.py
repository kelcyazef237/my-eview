"""Redis-backed sliding-window rate limiting."""

import time

import redis

from app.config import get_settings

settings = get_settings()


def _get_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def is_allowed(key: str, window_seconds: int, max_calls: int) -> bool:
    r = _get_redis()
    now = time.time()
    window_start = now - window_seconds
    # Remove entries outside the window
    r.zremrangebyscore(key, 0, window_start)
    # Count current entries
    current = r.zcard(key)
    if current >= max_calls:
        return False
    # Add current request
    r.zadd(key, {str(now): now})
    r.expire(key, window_seconds)
    return True


def public_lookup_domain_allowed(domain: str) -> bool:
    key = f"myeview:public_lookup:domain:{domain.lower()}"
    return is_allowed(key, settings.public_lookup_per_domain_days * 86400, 1)


def public_lookup_ip_allowed(ip: str) -> bool:
    key = f"myeview:public_lookup:ip:{ip}"
    return is_allowed(key, settings.public_lookup_per_ip_window_seconds, settings.public_lookup_per_ip_max)
