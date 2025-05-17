from redis.asyncio import Redis
from arq.connections import RedisSettings

redis = Redis(
    host = "redis",
    port = 6379,
    db=0
)

redis_for_invalid = Redis(
    host="redis",
    port=6379,
    db=1
)

pool_settings = RedisSettings(
    host = "redis",
    port=6379,
    database=1
)

