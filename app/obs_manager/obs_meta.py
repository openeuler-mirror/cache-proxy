import threading

from app.manager.meta_manager import *
from app.obs_manager.obs_client import obs_client


class OBSMeta(Meta):
    def __init__(self):
        self.lock = threading.Lock()
        key_set = obs_client.get_all_object_key()
        # {url: object_key}
        self.meta = {key.split("/")[0]: key for key in key_set}

    def is_in_meta(self, url_sha256):
        with self.lock:
            return url_sha256 in self.meta

    def delete(self, url_sha256):
        with self.lock:
            if url_sha256 in self.meta:
                del self.meta[url_sha256]

    def update(self, url_sha256, object_key):
        with self.lock:
            self.meta[url_sha256] = object_key

    def get_object_key(self, url_sha256):
        with self.lock:
            if url_sha256 in self.meta:
                return self.meta[url_sha256]
            else:
                return None


obs_meta = OBSMeta()
