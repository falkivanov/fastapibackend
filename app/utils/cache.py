# from fastapi_cache2 import FastAPICache
# from fastapi_cache2.backends.redis import RedisBackend
# from redis import asyncio as aioredis
# from app.config import get_settings

# settings = get_settings()

# async def setup_cache():
#     """
#     Initialisiert den Redis-Cache für die Anwendung.
#     """
#     redis = aioredis.from_url(
#         f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
#         password=settings.REDIS_PASSWORD,
#         db=settings.REDIS_DB,
#         encoding="utf8",
#         decode_responses=True
#     )
    
#     FastAPICache.init(
#         RedisBackend(redis),
#         prefix="fastapi-cache",
#         expire=300  # Standard-Cache-Zeit: 5 Minuten
#     ) 