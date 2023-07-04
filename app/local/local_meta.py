import os
import threading

from app.manager.meta_manager import *
import config


class LocalMeta(Meta):
    def __init__(self):
        self.lock = threading.Lock()
        dir_names = os.listdir(config.CACHE_DIR)
        self.meta = {}
        for name in dir_names:
            dir_path = os.path.join(config.CACHE_DIR, name)
            if os.path.isdir(dir_path):
                if os.listdir(dir_path):
                    self.meta[name] = name + "/" + os.listdir(dir_path)[0]

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


local_meta = LocalMeta()

