import hashlib
import json


class KV():
    ENCODING = 'utf-8'

    def __init__(this, backend):
        this.backend = backend

    def _to_key(self, v):
        return hashlib.md5(bytes(v, self.ENCODING)).digest()

    def delete(self, key: str):
        self.backend.delete(self._to_key(key))

    def get(self, key: str):
        v = self.backend.get(self._to_key(key))
        if not v:
            return None
        return json.loads(v.decode('utf-8'))

    def put(self, key: str, val: str):
        self.backend.put(self._to_key(key),
                         bytes(json.dumps(val), self.ENCODING))
