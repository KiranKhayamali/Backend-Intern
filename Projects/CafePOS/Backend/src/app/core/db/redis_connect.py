import redis

from ..config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
    socket_timeout=settings.REDIS_TIMEOUT,
    decode_responses=True
)

try:
    redis_client.ping()
    print("Connected to Redis successfully!")
except redis.ConnectionError as e:
    print(f"Failed to connect to Redis: {e}")