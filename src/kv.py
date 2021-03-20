"""
Provides persistent storage facade
"""

import json
import hashlib


class KV():
    """Key value storage interface"""
    ENCODING = 'utf-8'

    def __init__(self, backend):
        self.backend = backend

    def _to_key(self, val):
        return hashlib.md5(bytes(val, self.ENCODING)).digest()

    def close(self, ):
        """Closes the backend storage handle"""
        self.backend.close()

    def delete(self, key: str):
        "Clears key"
        self.backend.delete(self._to_key(key))

    def get(self, key: str):
        "Retrieves key"
        val = self.backend.get(self._to_key(key))
        if not val:
            return None
        return json.loads(val.decode('utf-8'))

    def put(self, key: str, val: str):
        """Stores value at key"""
        self.backend.put(self._to_key(key),
                         bytes(json.dumps(val), self.ENCODING))
