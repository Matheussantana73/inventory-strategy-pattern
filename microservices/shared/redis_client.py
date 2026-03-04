"""Cliente Redis para cache e pub/sub"""

import os
import redis
import json
from typing import Optional, Any

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


class CacheService:
    """Serviço de cache usando Redis"""

    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.client = redis_client

    def _make_key(self, key: str) -> str:
        """Cria chave com prefixo"""
        return f"{self.prefix}:{key}" if self.prefix else key

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        data = self.client.get(self._make_key(key))
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Define valor no cache com expiração em segundos"""
        return self.client.setex(self._make_key(key), expire, json.dumps(value))

    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        return self.client.delete(self._make_key(key))

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalida todas as chaves que correspondem ao padrão"""
        keys = self.client.keys(self._make_key(pattern))
        if keys:
            return self.client.delete(*keys)
        return 0


class EventBus:
    """Barramento de eventos usando Redis Pub/Sub"""

    def __init__(self):
        self.client = redis_client
        self.pubsub = self.client.pubsub()

    def publish(self, channel: str, message: dict) -> int:
        """Publica evento em um canal"""
        return self.client.publish(channel, json.dumps(message))

    def subscribe(self, channel: str):
        """Inscreve-se em um canal"""
        self.pubsub.subscribe(channel)

    def listen(self):
        """Escuta mensagens dos canais inscritos"""
        for message in self.pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])
