from langgraph.checkpoint.redis import RedisSaver
from config.logger import logger
from config.settings import settings

_redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"

_ttl_config = {
    "default_ttl": settings.redis_ttl_minutes,  
    "refresh_on_read": True,  
}

logger.info(f"Connecting Redis checkpointer | url={_redis_url} | ttl_minutes={settings.redis_ttl_minutes}")

checkpointer_cm = RedisSaver.from_conn_string(_redis_url, ttl=_ttl_config)
checkpointer = checkpointer_cm.__enter__()
checkpointer.setup()  
logger.info("Redis checkpointer ready")